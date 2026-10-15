"""
Library Management System - Flask Application
=============================================
MSBTE K Scheme - DMS 313302 Micro Project
Backend application running on top of MySQL library_management database.
"""

from functools import wraps
import re
from datetime import date
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
from config import Config
import db

app = Flask(__name__)
app.config.from_object(Config)

# ============================================================
# Helpers & Decorators
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_global_data():
    """Injects overdue counts and common info to all templates."""
    overdue_count = 0
    if session.get('logged_in'):
        try:
            ok, rows = db.call_list_overdue_books()
            if ok and isinstance(rows, list):
                overdue_count = len(rows)
        except Exception:
            pass
    return {'overdue_count': overdue_count}

def is_valid_email(email):
    return bool(re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email or ''))

# ============================================================
# Authentication Routes
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if username == Config.STAFF_USERNAME and password == Config.STAFF_PASSWORD:
            session['logged_in'] = True
            session['staff_user'] = username
            flash('Welcome back! Signed in to Library Circulation Desk.', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('login'))

# ============================================================
# Dashboard
# ============================================================

@app.route('/')
@app.route('/dashboard')
@login_required
def dashboard():
    # 1. Total Titles
    ok, total_titles = db.execute_query("SELECT COUNT(*) AS cnt FROM Books", fetch='value')
    total_titles = total_titles if ok and total_titles is not None else 0

    # 2. Copies on shelf
    ok, shelf_copies = db.execute_query("SELECT COALESCE(SUM(Available_Quantity), 0) AS cnt FROM Books", fetch='value')
    shelf_copies = int(shelf_copies) if ok and shelf_copies is not None else 0

    # 3. Books on loan
    ok, books_on_loan = db.execute_query("SELECT COUNT(*) AS cnt FROM Book_Issues WHERE Status = 'Issued'", fetch='value')
    books_on_loan = books_on_loan if ok and books_on_loan is not None else 0

    # 4. Overdue count via procedure list_overdue_books()
    ok, overdue_list = db.call_list_overdue_books()
    overdue_count = len(overdue_list) if ok and isinstance(overdue_list, list) else 0

    # 5. Total pending fines
    ok, pending_fines = db.execute_query(
        "SELECT COALESCE(SUM(Fine_Amount), 0) AS total FROM Fines_Payments WHERE Payment_Status = 'Pending'",
        fetch='value'
    )
    pending_fines = float(pending_fines) if ok and pending_fines is not None else 0.00

    # 6. Books running low on copies (Available <= 2)
    ok, low_stock_books = db.execute_query("""
        SELECT b.Book_ID, b.Title, b.Quantity, b.Available_Quantity, a.Author_Name
        FROM Books b
        INNER JOIN Authors a ON b.Author_ID = a.Author_ID
        WHERE b.Available_Quantity <= 2
        ORDER BY b.Available_Quantity ASC
    """)
    low_stock_books = low_stock_books if ok else []

    # 7. Recent activity from Audit_Log
    ok, recent_activity = db.execute_query("SELECT * FROM Audit_Log ORDER BY Log_ID DESC LIMIT 5")
    recent_activity = recent_activity if ok else []

    return render_template(
        'dashboard.html',
        active_page='dashboard',
        total_titles=total_titles,
        shelf_copies=shelf_copies,
        books_on_loan=books_on_loan,
        overdue_count=overdue_count,
        pending_fines=pending_fines,
        low_stock_books=low_stock_books,
        recent_activity=recent_activity
    )

# ============================================================
# Circulation: Issue Book
# ============================================================

@app.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_book():
    confirmation = None
    selected_member_id = None
    selected_book_id = None

    if request.method == 'POST':
        member_id_str = request.form.get('member_id', '').strip()
        book_id_str = request.form.get('book_id', '').strip()

        if not member_id_str or not book_id_str:
            flash('Please select both a member and a book.', 'warning')
        else:
            try:
                selected_member_id = int(member_id_str)
                selected_book_id = int(book_id_str)

                # Call database procedure issue_book(member_id, book_id)
                ok, result = db.call_issue_book(selected_member_id, selected_book_id)

                if ok:
                    # Fetch member name for slip
                    _, mem = db.execute_query("SELECT Member_Name FROM Members WHERE Member_ID = %s", (selected_member_id,), fetch='one')
                    member_name = mem['Member_Name'] if mem else f"Member #{selected_member_id}"

                    confirmation = {
                        'Book': result.get('Book', 'Selected Book'),
                        'Member_Name': member_name,
                        'Issue_Date': result.get('Issue_Date', date.today().isoformat()),
                        'Due_Date': result.get('Due_Date', '14 days from issue')
                    }
                    flash(f"Book '{confirmation['Book']}' issued successfully to {member_name}.", 'success')
                    selected_member_id = None
                    selected_book_id = None
                else:
                    flash(result, 'danger')

            except ValueError:
                flash('Invalid member or book selection.', 'danger')

    # Fetch members & books for dropdowns
    _, members = db.execute_query("SELECT Member_ID, Member_Name, Member_Email FROM Members ORDER BY Member_Name ASC")
    _, books = db.execute_query("""
        SELECT b.Book_ID, b.Title, b.Available_Quantity, b.Quantity, a.Author_Name
        FROM Books b
        INNER JOIN Authors a ON b.Author_ID = a.Author_ID
        ORDER BY b.Title ASC
    """)

    return render_template(
        'issue_book.html',
        active_page='issue',
        members=members or [],
        books=books or [],
        confirmation=confirmation,
        selected_member_id=selected_member_id,
        selected_book_id=selected_book_id
    )

# ============================================================
# Circulation: Return Book
# ============================================================

@app.route('/return')
@login_required
def return_book():
    query = """
        SELECT bi.Issue_ID, bi.Member_ID, m.Member_Name, m.Member_Phone,
               bi.Book_ID, b.Title, b.Genre, bi.Issue_Date, bi.Due_Date
        FROM Book_Issues bi
        INNER JOIN Members m ON bi.Member_ID = m.Member_ID
        INNER JOIN Books b ON bi.Book_ID = b.Book_ID
        WHERE bi.Status = 'Issued'
        ORDER BY bi.Due_Date ASC
    """
    ok, loans = db.execute_query(query)
    loans = loans or []

    # Calculate days late & live fine today for each loan using fn_calculate_fine
    today = date.today()
    for loan in loans:
        due = loan['Due_Date']
        if isinstance(due, str):
            due = date.fromisoformat(due)
        days_late = (today - due).days
        loan['days_late'] = max(0, days_late)
        loan['fine_today'] = db.calculate_fine_today(loan['Issue_ID'])

    return render_template('return_book.html', active_page='return', loans=loans)

@app.route('/return/<int:issue_id>', methods=['POST'])
@login_required
def process_return(issue_id):
    ok, result = db.call_return_book(issue_id)
    if ok:
        fine_amount = float(result.get('Fine_Amount', 0.0) or 0.0)
        if fine_amount > 0:
            flash(
                f"Book returned. Note: This loan was returned late. A fine of ₹ {fine_amount:.2f} has been created and marked as Pending.",
                'warning'
            )
        else:
            flash("Book returned on schedule! Inventory updated and return logged to audit trail.", 'success')
    else:
        flash(result, 'danger')

    return redirect(url_for('return_book'))

# ============================================================
# Circulation: Fines Management
# ============================================================

@app.route('/fines')
@login_required
def fines():
    query = """
        SELECT fp.Fine_ID, fp.Issue_ID, fp.Fine_Amount, fp.Fine_Reason,
               fp.Payment_Status, fp.Payment_Mode, fp.Payment_Date,
               m.Member_Name, b.Title
        FROM Fines_Payments fp
        INNER JOIN Book_Issues bi ON fp.Issue_ID = bi.Issue_ID
        INNER JOIN Members m ON bi.Member_ID = m.Member_ID
        INNER JOIN Books b ON bi.Book_ID = b.Book_ID
        ORDER BY CASE WHEN fp.Payment_Status = 'Pending' THEN 1 ELSE 2 END, fp.Fine_ID DESC
    """
    ok, fines_list = db.execute_query(query)
    fines_list = fines_list or []

    pending_total = sum(float(f['Fine_Amount']) for f in fines_list if f['Payment_Status'] == 'Pending')
    collected_total = sum(float(f['Fine_Amount']) for f in fines_list if f['Payment_Status'] == 'Paid')

    return render_template(
        'fines.html',
        active_page='fines',
        fines=fines_list,
        pending_total=pending_total,
        collected_total=collected_total
    )

@app.route('/fines/pay', methods=['POST'])
@login_required
def pay_fine_route():
    issue_id_str = request.form.get('issue_id', '').strip()
    payment_mode = request.form.get('payment_mode', '').strip()

    if not issue_id_str or payment_mode not in ('Cash', 'UPI', 'Card'):
        flash('Invalid payment details. Please select Cash, UPI, or Card.', 'danger')
        return redirect(url_for('fines'))

    try:
        issue_id = int(issue_id_str)
        ok, res = db.call_pay_fine(issue_id, payment_mode)
        if ok:
            flash(f"Fine for Issue #{issue_id} settled successfully via {payment_mode}.", 'success')
        else:
            flash(res, 'danger')
    except ValueError:
        flash('Invalid issue ID format.', 'danger')

    return redirect(url_for('fines'))

# ============================================================
# Circulation: Overdue Books
# ============================================================

@app.route('/overdue')
@login_required
def overdue():
    ok, overdue_books = db.call_list_overdue_books()
    if not ok:
        flash(overdue_books, 'danger')
        overdue_books = []

    return render_template('overdue.html', active_page='overdue', overdue_books=overdue_books or [])

# ============================================================
# Circulation: History (View + Full Log)
# ============================================================

@app.route('/history')
@login_required
def history():
    # 1. Active issues from View: Current_Issued_Books
    ok1, current_issues = db.execute_query("SELECT * FROM Current_Issued_Books ORDER BY Due_Date ASC")
    current_issues = current_issues if ok1 else []

    # 2. Complete Loan Archive
    query = """
        SELECT bi.Issue_ID, bi.Member_ID, m.Member_Name, bi.Book_ID, b.Title,
               bi.Issue_Date, bi.Due_Date, bi.Return_Date, bi.Status,
               fp.Fine_Amount, fp.Payment_Status
        FROM Book_Issues bi
        INNER JOIN Members m ON bi.Member_ID = m.Member_ID
        INNER JOIN Books b ON bi.Book_ID = b.Book_ID
        LEFT JOIN Fines_Payments fp ON bi.Issue_ID = fp.Issue_ID
        ORDER BY bi.Issue_ID DESC
    """
    ok2, all_issues = db.execute_query(query)
    all_issues = all_issues if ok2 else []

    return render_template(
        'history.html',
        active_page='history',
        current_issues=current_issues,
        all_issues=all_issues
    )

# ============================================================
# Database Audit Log
# ============================================================

@app.route('/audit-log')
@login_required
def audit_log():
    ok, logs = db.execute_query("SELECT * FROM Audit_Log ORDER BY Log_ID DESC")
    logs = logs if ok else []
    return render_template('audit_log.html', active_page='audit', logs=logs)

# ============================================================
# Catalog: Books Management
# ============================================================

@app.route('/books')
@login_required
def books():
    query = """
        SELECT b.Book_ID, b.Title, b.Author_ID, b.Publisher_ID, b.Genre,
               b.Quantity, b.Available_Quantity,
               a.Author_Name, p.Publisher_Name
        FROM Books b
        INNER JOIN Authors a ON b.Author_ID = a.Author_ID
        INNER JOIN Publishers p ON b.Publisher_ID = p.Publisher_ID
        ORDER BY b.Title ASC
    """
    _, books_list = db.execute_query(query)
    _, authors_list = db.execute_query("SELECT Author_ID, Author_Name FROM Authors ORDER BY Author_Name ASC")
    _, publishers_list = db.execute_query("SELECT Publisher_ID, Publisher_Name FROM Publishers ORDER BY Publisher_Name ASC")

    return render_template(
        'books.html',
        active_page='books',
        books=books_list or [],
        authors=authors_list or [],
        publishers=publishers_list or []
    )

@app.route('/books/add', methods=['POST'])
@login_required
def add_book():
    title = request.form.get('title', '').strip()
    author_id = request.form.get('author_id', '').strip()
    publisher_id = request.form.get('publisher_id', '').strip()
    genre = request.form.get('genre', '').strip()
    quantity_str = request.form.get('quantity', '').strip()

    if not all([title, author_id, publisher_id, genre, quantity_str]):
        flash('All fields are required to add a book.', 'warning')
        return redirect(url_for('books'))

    try:
        qty = int(quantity_str)
        if qty <= 0:
            flash('Total quantity must be greater than zero.', 'danger')
            return redirect(url_for('books'))

        # Rule: A new book starts with all copies available (Available_Quantity = Quantity)
        ok, res = db.execute_dml("""
            INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, int(author_id), int(publisher_id), genre, qty, qty))

        if ok:
            flash(f"Book '{title}' added to catalog with {qty} available copies.", 'success')
        else:
            flash(res, 'danger')

    except ValueError:
        flash('Invalid numeric value for quantity, author, or publisher.', 'danger')

    return redirect(url_for('books'))

@app.route('/books/edit', methods=['POST'])
@login_required
def edit_book():
    book_id_str = request.form.get('book_id', '').strip()
    title = request.form.get('title', '').strip()
    author_id_str = request.form.get('author_id', '').strip()
    publisher_id_str = request.form.get('publisher_id', '').strip()
    genre = request.form.get('genre', '').strip()
    new_qty_str = request.form.get('quantity', '').strip()

    if not all([book_id_str, title, author_id_str, publisher_id_str, genre, new_qty_str]):
        flash('All fields are required.', 'warning')
        return redirect(url_for('books'))

    try:
        book_id = int(book_id_str)
        new_qty = int(new_qty_str)
        author_id = int(author_id_str)
        publisher_id = int(publisher_id_str)

        if new_qty <= 0:
            flash('Total copies must be greater than zero.', 'danger')
            return redirect(url_for('books'))

        # Fetch current quantities
        _, cur_book = db.execute_query("SELECT Quantity, Available_Quantity FROM Books WHERE Book_ID = %s", (book_id,), fetch='one')
        if not cur_book:
            flash('Book not found.', 'danger')
            return redirect(url_for('books'))

        old_qty = cur_book['Quantity']
        old_avail = cur_book['Available_Quantity']
        borrowed = old_qty - old_avail

        # Rule: Changing a book's total copies must keep the available count correct.
        # Total cannot be reduced below the number of currently borrowed copies.
        if new_qty < borrowed:
            flash(
                f"Cannot reduce total quantity to {new_qty}. There are currently {borrowed} copies checked out to members.",
                'danger'
            )
            return redirect(url_for('books'))

        new_avail = old_avail + (new_qty - old_qty)

        ok, res = db.execute_dml("""
            UPDATE Books
            SET Title = %s, Author_ID = %s, Publisher_ID = %s, Genre = %s,
                Quantity = %s, Available_Quantity = %s
            WHERE Book_ID = %s
        """, (title, author_id, publisher_id, genre, new_qty, new_avail, book_id))

        if ok:
            flash(f"Book '{title}' updated successfully. Total: {new_qty}, Available: {new_avail}.", 'success')
        else:
            flash(res, 'danger')

    except ValueError:
        flash('Invalid input formats.', 'danger')

    return redirect(url_for('books'))

@app.route('/books/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    ok, res = db.execute_dml("DELETE FROM Books WHERE Book_ID = %s", (book_id,))
    if ok:
        flash('Book deleted from catalog.', 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('books'))

# ============================================================
# Directory: Members Management
# ============================================================

@app.route('/members')
@login_required
def members():
    query = """
        SELECT m.Member_ID, m.Member_Name, m.Member_Email, m.Member_Phone, m.Member_Address,
               (SELECT COUNT(*) FROM Book_Issues bi WHERE bi.Member_ID = m.Member_ID AND bi.Status = 'Issued') AS active_loans
        FROM Members m
        ORDER BY m.Member_Name ASC
    """
    _, members_list = db.execute_query(query)
    return render_template('members.html', active_page='members', members=members_list or [])

@app.route('/members/add', methods=['POST'])
@login_required
def add_member():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not name or not email:
        flash('Member Name and Email are required.', 'warning')
        return redirect(url_for('members'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('members'))

    ok, res = db.execute_dml("""
        INSERT INTO Members (Member_Name, Member_Email, Member_Phone, Member_Address)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, address))

    if ok:
        flash(f"Member '{name}' registered successfully.", 'success')
    else:
        flash(res, 'danger')

    return redirect(url_for('members'))

@app.route('/members/edit', methods=['POST'])
@login_required
def edit_member():
    member_id_str = request.form.get('member_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not member_id_str or not name or not email:
        flash('Member ID, Name, and Email are required.', 'warning')
        return redirect(url_for('members'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('members'))

    try:
        member_id = int(member_id_str)
        ok, res = db.execute_dml("""
            UPDATE Members
            SET Member_Name = %s, Member_Email = %s, Member_Phone = %s, Member_Address = %s
            WHERE Member_ID = %s
        """, (name, email, phone, address, member_id))

        if ok:
            flash(f"Member details for '{name}' updated successfully.", 'success')
        else:
            flash(res, 'danger')

    except ValueError:
        flash('Invalid member ID.', 'danger')

    return redirect(url_for('members'))

@app.route('/members/delete/<int:member_id>', methods=['POST'])
@login_required
def delete_member(member_id):
    # Friendly check: active loans
    _, active = db.execute_query(
        "SELECT COUNT(*) AS cnt FROM Book_Issues WHERE Member_ID = %s AND Status = 'Issued'",
        (member_id,), fetch='value'
    )
    if active and active > 0:
        flash(f"Cannot delete member: This member currently has {active} book(s) on loan. Please return them first.", 'danger')
        return redirect(url_for('members'))

    ok, res = db.execute_dml("DELETE FROM Members WHERE Member_ID = %s", (member_id,))
    if ok:
        flash('Member record deleted successfully.', 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('members'))

# ============================================================
# Catalog: Authors Management
# ============================================================

@app.route('/authors')
@login_required
def authors():
    query = """
        SELECT a.Author_ID, a.Author_Name, a.Author_Email, a.City,
               (SELECT COUNT(*) FROM Books b WHERE b.Author_ID = a.Author_ID) AS book_count
        FROM Authors a
        ORDER BY a.Author_Name ASC
    """
    _, authors_list = db.execute_query(query)
    return render_template('authors.html', active_page='authors', authors=authors_list or [])

@app.route('/authors/add', methods=['POST'])
@login_required
def add_author():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    city = request.form.get('city', '').strip()

    if not name or not email:
        flash('Author Name and Email are required.', 'warning')
        return redirect(url_for('authors'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('authors'))

    ok, res = db.execute_dml("INSERT INTO Authors (Author_Name, Author_Email, City) VALUES (%s, %s, %s)", (name, email, city))
    if ok:
        flash(f"Author '{name}' added successfully.", 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('authors'))

@app.route('/authors/edit', methods=['POST'])
@login_required
def edit_author():
    author_id_str = request.form.get('author_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    city = request.form.get('city', '').strip()

    if not author_id_str or not name or not email:
        flash('Author ID, Name, and Email are required.', 'warning')
        return redirect(url_for('authors'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('authors'))

    try:
        author_id = int(author_id_str)
        ok, res = db.execute_dml("""
            UPDATE Authors SET Author_Name = %s, Author_Email = %s, City = %s WHERE Author_ID = %s
        """, (name, email, city, author_id))
        if ok:
            flash(f"Author '{name}' updated successfully.", 'success')
        else:
            flash(res, 'danger')
    except ValueError:
        flash('Invalid author ID.', 'danger')

    return redirect(url_for('authors'))

@app.route('/authors/delete/<int:author_id>', methods=['POST'])
@login_required
def delete_author(author_id):
    ok, res = db.execute_dml("DELETE FROM Authors WHERE Author_ID = %s", (author_id,))
    if ok:
        flash('Author deleted successfully.', 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('authors'))

# ============================================================
# Catalog: Publishers Management
# ============================================================

@app.route('/publishers')
@login_required
def publishers():
    query = """
        SELECT p.Publisher_ID, p.Publisher_Name, p.Publisher_Email, p.Publisher_Phone, p.Publisher_Address,
               (SELECT COUNT(*) FROM Books b WHERE b.Publisher_ID = p.Publisher_ID) AS book_count
        FROM Publishers p
        ORDER BY p.Publisher_Name ASC
    """
    _, pub_list = db.execute_query(query)
    return render_template('publishers.html', active_page='publishers', publishers=pub_list or [])

@app.route('/publishers/add', methods=['POST'])
@login_required
def add_publisher():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not name or not email:
        flash('Publisher Name and Email are required.', 'warning')
        return redirect(url_for('publishers'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('publishers'))

    ok, res = db.execute_dml("""
        INSERT INTO Publishers (Publisher_Name, Publisher_Email, Publisher_Phone, Publisher_Address)
        VALUES (%s, %s, %s, %s)
    """, (name, email, phone, address))

    if ok:
        flash(f"Publisher '{name}' added successfully.", 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('publishers'))

@app.route('/publishers/edit', methods=['POST'])
@login_required
def edit_publisher():
    publisher_id_str = request.form.get('publisher_id', '').strip()
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    address = request.form.get('address', '').strip()

    if not publisher_id_str or not name or not email:
        flash('Publisher ID, Name, and Email are required.', 'warning')
        return redirect(url_for('publishers'))

    if not is_valid_email(email):
        flash('Please enter a valid email address.', 'danger')
        return redirect(url_for('publishers'))

    try:
        publisher_id = int(publisher_id_str)
        ok, res = db.execute_dml("""
            UPDATE Publishers
            SET Publisher_Name = %s, Publisher_Email = %s, Publisher_Phone = %s, Publisher_Address = %s
            WHERE Publisher_ID = %s
        """, (name, email, phone, address, publisher_id))

        if ok:
            flash(f"Publisher '{name}' updated successfully.", 'success')
        else:
            flash(res, 'danger')
    except ValueError:
        flash('Invalid publisher ID.', 'danger')

    return redirect(url_for('publishers'))

@app.route('/publishers/delete/<int:publisher_id>', methods=['POST'])
@login_required
def delete_publisher(publisher_id):
    ok, res = db.execute_dml("DELETE FROM Publishers WHERE Publisher_ID = %s", (publisher_id,))
    if ok:
        flash('Publisher deleted successfully.', 'success')
    else:
        flash(res, 'danger')
    return redirect(url_for('publishers'))

# ============================================================
# Main Entry Point
# ============================================================

if __name__ == '__main__':
    print("=" * 60)
    print("College Library Management System (Flask + MySQL)")
    print("MSBTE K-Scheme DMS 313302")
    print("Starting server on http://127.0.0.1:5000 ...")
    print("=" * 60)
    app.run(host='127.0.0.1', port=5000, debug=True)
