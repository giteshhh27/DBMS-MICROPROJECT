"""
Database Management Module
==========================
Handles MySQL connection pooling, stored procedure invocations,
functions, views, and human-friendly error handling.
Does NOT modify or duplicate any database rules; calls existing DB routines directly.
"""

import mysql.connector
from mysql.connector import Error, errorcode
from config import Config

def get_connection():
    """Establish and return a new MySQL connection."""
    return mysql.connector.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        charset='utf8mb4'
    )

def test_connection():
    """Verify database connectivity."""
    try:
        conn = get_connection()
        if conn.is_connected():
            conn.close()
            return True, "Database connected successfully."
    except Error as e:
        return False, parse_database_error(e)
    return False, "Could not establish database connection."

def parse_database_error(err, member_id=None, book_id=None):
    """
    Translates raw MySQL errors and SQLSTATE 45000 signals into
    clear, user-friendly, plain language messages.
    """
    if not isinstance(err, Error):
        return str(err)

    msg = err.msg if hasattr(err, 'msg') else str(err)
    errno = getattr(err, 'errno', None)
    sqlstate = getattr(err, 'sqlstate', None)

    # 1. Custom Stored Procedure Signals (SQLSTATE 45000)
    if sqlstate == '45000' or '45000' in msg:
        if 'Member already has 3 active books' in msg:
            held_books_info = ""
            if member_id:
                try:
                    conn = get_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("""
                        SELECT b.Title, bi.Issue_Date, bi.Due_Date
                        FROM Book_Issues bi
                        INNER JOIN Books b ON bi.Book_ID = b.Book_ID
                        WHERE bi.Member_ID = %s AND bi.Status = 'Issued'
                        ORDER BY bi.Issue_Date ASC
                    """, (member_id,))
                    rows = cur.fetchall()
                    conn.close()
                    if rows:
                        items = [f"• \"{r['Title']}\" (Issued: {r['Issue_Date']})" for r in rows]
                        held_books_info = " Currently borrowed:\n" + "\n".join(items)
                except Exception:
                    pass
            return f"Member has reached the limit of 3 books.{held_books_info}\nPlease return a book before issuing a new one."

        if 'was already issued on' in msg:
            return msg

        if 'Book is currently unavailable' in msg:
            book_title = ""
            if book_id:
                try:
                    conn = get_connection()
                    cur = conn.cursor(dictionary=True)
                    cur.execute("SELECT Title FROM Books WHERE Book_ID = %s", (book_id,))
                    row = cur.fetchone()
                    conn.close()
                    if row:
                        book_title = f" '{row['Title']}'"
                except Exception:
                    pass
            return f"The book{book_title} is currently unavailable (all copies are issued to other members)."

        if 'Member does not exist' in msg:
            return "The selected member does not exist in the library records."

        if 'Book does not exist' in msg:
            return "The selected book does not exist in the library records."

        if 'This book is already returned' in msg:
            return "This book loan has already been marked as returned."

        if 'Fine record does not exist' in msg:
            return "No fine record was found for this loan issue."

        if 'Fine is already paid' in msg:
            return "This fine has already been paid."

        return msg

    # 2. Duplicate Key Errors (Error 1062)
    if errno == 1062 or '1062' in msg:
        if 'UK_Member_Email' in msg or 'Member_Email' in msg:
            return "A member with this email address is already registered. Please use a unique email."
        if 'UK_Author_Email' in msg or 'Author_Email' in msg:
            return "An author with this email address already exists. Please use a unique email."
        if 'UK_Publisher_Email' in msg or 'Publisher_Email' in msg:
            return "A publisher with this email address already exists. Please use a unique email."
        if 'UK_Fine_Issue' in msg:
            return "A fine record already exists for this book issue."
        return "Duplicate entry error: A record with these unique details already exists."

    # 3. Foreign Key Constraint Violations (Error 1451 / 1452)
    if errno == 1451 or '1451' in msg:
        return "Cannot delete this record because it has active references in other tables (e.g. books, loans, or fines). Please remove dependent records first."
    if errno == 1452 or '1452' in msg:
        return "Invalid reference: The selected author, publisher, member, or book does not exist."

    # 4. Check Constraint Violations (Error 3819)
    if errno == 3819 or '3819' in msg:
        if 'CHK_Quantity' in msg:
            return "Invalid quantity: Total book copies must be greater than zero."
        if 'CHK_Available_Quantity' in msg:
            return "Invalid copies: Available quantity must be between 0 and total quantity."
        if 'CHK_Fine_Amount' in msg:
            return "Fine amount must be greater than or equal to zero."
        return "Data validation constraint failed. Please check the values entered."

    # 5. Database Connection Errors
    if errno in (2002, 2003, 1045) or 'Access denied' in msg or "Can't connect" in msg:
        return f"Database connection error: Unable to connect to MySQL on {Config.DB_HOST}:{Config.DB_PORT}. Please ensure MySQL service is running and credentials in config.py are correct."

    return f"Database error: {msg}"


def execute_query(query, params=None, fetch='all'):
    """
    Executes a SELECT query and returns rows as dictionaries.
    fetch can be 'all', 'one', or 'value'.
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        if fetch == 'one':
            result = cur.fetchone()
        elif fetch == 'value':
            row = cur.fetchone()
            result = list(row.values())[0] if row else None
        else:
            result = cur.fetchall()
        cur.close()
        return True, result
    except Error as e:
        return False, parse_database_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def execute_dml(query, params=None):
    """
    Executes an INSERT, UPDATE, or DELETE query and commits.
    Returns (success, result_id_or_affected_rows_or_error).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params or ())
        conn.commit()
        last_id = cur.lastrowid
        row_count = cur.rowcount
        cur.close()
        return True, {'last_id': last_id, 'row_count': row_count}
    except Error as e:
        if conn:
            conn.rollback()
        return False, parse_database_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================
# Stored Procedures Calling Helpers
# ============================================================

def call_issue_book(member_id, book_id):
    """
    Calls the database procedure issue_book(p_member_id, p_book_id).
    Returns (success, result_dict_or_error_message).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.callproc('issue_book', [member_id, book_id])
        conn.commit()

        # The procedure returns: Message, Book, Issue_Date, Due_Date
        result_data = None
        for result in cur.stored_results():
            rows = result.fetchall()
            if rows:
                result_data = rows[0]
                break

        cur.close()
        return True, result_data or {'Message': 'Book issued successfully.'}
    except Error as e:
        if conn:
            conn.rollback()
        return False, parse_database_error(e, member_id=member_id, book_id=book_id)
    finally:
        if conn and conn.is_connected():
            conn.close()


def call_return_book(issue_id):
    """
    Calls the database procedure return_book(p_issue_id).
    Returns (success, result_dict_or_error_message).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.callproc('return_book', [issue_id])
        conn.commit()

        # The procedure returns: Message, Fine_Amount
        result_data = None
        for result in cur.stored_results():
            rows = result.fetchall()
            if rows:
                result_data = rows[0]
                break

        cur.close()
        return True, result_data or {'Message': 'Book returned successfully.', 'Fine_Amount': 0.00}
    except Error as e:
        if conn:
            conn.rollback()
        return False, parse_database_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def call_pay_fine(issue_id, payment_mode):
    """
    Calls the database procedure pay_fine(p_issue_id, p_payment_mode).
    Returns (success, result_dict_or_error_message).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.callproc('pay_fine', [issue_id, payment_mode])
        conn.commit()

        result_data = None
        for result in cur.stored_results():
            rows = result.fetchall()
            if rows:
                result_data = rows[0]
                break

        cur.close()
        return True, result_data or {'Message': 'Fine paid successfully.'}
    except Error as e:
        if conn:
            conn.rollback()
        return False, parse_database_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


def call_list_overdue_books():
    """
    Calls the database procedure list_overdue_books() which uses an explicit cursor.
    Returns (success, list_of_overdue_books_or_error).
    """
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=True)
        cur.callproc('list_overdue_books')

        rows = []
        for result in cur.stored_results():
            rows = result.fetchall()
            break

        cur.close()
        return True, rows
    except Error as e:
        return False, parse_database_error(e)
    finally:
        if conn and conn.is_connected():
            conn.close()


# ============================================================
# Stored Function Calling Helpers
# ============================================================

def get_book_availability(book_id):
    """Calls function fn_check_availability(p_book_id)."""
    ok, res = execute_query("SELECT fn_check_availability(%s) AS Available", (book_id,), fetch='value')
    return res if ok else 0


def calculate_fine_today(issue_id):
    """Calls function fn_calculate_fine(p_issue_id)."""
    ok, res = execute_query("SELECT fn_calculate_fine(%s) AS Fine", (issue_id,), fetch='value')
    return float(res) if ok and res is not None else 0.00
