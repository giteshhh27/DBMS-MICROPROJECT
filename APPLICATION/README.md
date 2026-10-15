# College Library Management System

A complete, production-grade Library Management System web application built for college circulation desks (MSBTE K Scheme &mdash; DMS 313302 Micro Project).

The application runs seamlessly on Windows and directly connects to the MySQL `library_management` database script. It preserves and executes all business logic, stored procedures, functions, triggers, and views inside the database without altering the underlying SQL schema.

---

## 🌟 Key Features

1. **Circulation & Issue Desk**:
   - Issue books with dynamic member and book selectors.
   - Generates a circulation slip confirmation displaying Book Title, Member Name, Issue Date, and Due Date (14-day loan).
   - Strict database rule enforcement: Maximum 3 active books per member, no duplicate loans for the same book, zero-stock rejection, and row-level locking.

2. **Return Desk & Live Fine Calculation**:
   - Displays all active loans with real-time days late and live fine preview calculated via database function `fn_calculate_fine(Issue_ID)`.
   - Single-click return executing procedure `return_book(Issue_ID)`.
   - Restores book inventory and automatically creates pending fine records if late.

3. **Fines & Invoicing**:
   - Ordered with **Pending** fines first, followed by settled records.
   - Settle fines directly through procedure `pay_fine(Issue_ID, Mode)` using **Cash**, **UPI**, or **Card**.

4. **Overdue Books Tracking**:
   - Explicit cursor-driven procedure `list_overdue_books()` with a `NOT FOUND` handler, returning members and loans exceeding the 14-day borrowing window.

5. **Circulation History**:
   - Tab 1: Live view querying MySQL View `Current_Issued_Books`.
   - Tab 2: Complete loan and return history archive.

6. **Catalog & Directory Management (CRUD)**:
   - Full search, filter, add, edit, and delete for **Books**, **Members**, **Authors**, and **Publishers**.
   - **Quantity Invariant**: Adding a book auto-sets available copies to total copies. Editing total copies automatically updates available count and prevents reducing copies below currently loaned items.

7. **System Overview Dashboard**:
   - 6 KPI metric cards: Total Titles, Copies on Shelf, Books on Loan, Overdue Loans, Total Pending Fines, and Low Stock Titles (&le; 2 copies).
   - Quick action shortcuts for circulation staff.

8. **Database Trigger Audit Trail**:
   - Real-time logging of book returns into `Audit_Log` powered by MySQL Trigger `trg_return_audit`.

9. **Plain Language Error Translation**:
   - Translates database signals (SQLSTATE 45000), duplicate keys (1062), and foreign key constraints (1451) into friendly, human explanations. When the 3-book quota is reached, the system lists the 3 books currently held with their issue dates.

10. **Staff Security**:
    - Secure session authentication protecting circulation routes.

---

## 💻 Windows Setup & Run Instructions

### Prerequisites
- **Windows 10 or 11**
- **Python 3.8+** (installed and added to PATH)
- **MySQL 8.0 Server** (Service running, e.g. MySQL80)

---

### Step 1: Verify / Configure Database Settings

All database configuration parameters are centralized in a single settings file:
👉 **`config.py`**

Open `config.py` in Notepad or any code editor if your MySQL root password is not `12345`:

```python
class Config:
    DB_HOST = 'localhost'
    DB_PORT = 3306
    DB_USER = 'root'
    DB_PASSWORD = 'YOUR_MYSQL_PASSWORD'  # Default is '12345'
    DB_NAME = 'library_management'
```

> **Note**: If you have not loaded the database script into MySQL yet, open MySQL Workbench, open `Library_Management_System.sql` located in the parent directory, and execute the entire script.

---

### Step 2: Install Python Dependencies (If not already installed)

Open Command Prompt or PowerShell in the `APPLICATION` folder and run:

```cmd
pip install -r requirements.txt
```

*(If `Flask` and `mysql-connector-python` are already installed on your system, you can skip this step.)*

---

### Step 3: Run the Application

#### Option A: One-Click Launch (Recommended for Windows)
Simply double-click the **`run.bat`** file in the `APPLICATION` folder!
It will:
1. Verify Python is installed.
2. Test connection to the MySQL database.
3. Automatically open your default web browser to `http://127.0.0.1:5000`.
4. Start the application server.

#### Option B: From Command Prompt / PowerShell
Open your terminal in the `APPLICATION` folder and execute:

```cmd
python app.py
```

Then open your web browser and navigate to:
**`http://127.0.0.1:5000`**

---

### Step 4: Sign In with Staff Credentials

On the login page, enter the default staff credentials:
- **Username**: `admin`
- **Password**: `admin123`

---

## 🧪 Running the Automated Test Suite

A comprehensive test suite covering all 11 business rules, stored procedures, triggers, and constraints is provided in `test_system.py`.

Run the test suite with:

```cmd
python test_system.py
```

### What `test_system.py` Validates:
1. **Test 1**: Book issue success, circulation slip generation, and stock decrement.
2. **Test 2**: Duplicate loan rejection for the same member and book.
3. **Test 3**: Enforcement of the 3-book borrowing limit per member, returning held book titles and dates.
4. **Test 4**: Immediate rejection when requesting a book with 0 available copies.
5. **Test 5**: Graceful rejection of non-existent member and book IDs.
6. **Test 6**: Book return processing, inventory replenishment, and `trg_return_audit` trigger execution.
7. **Test 7**: Late return penalty generation (Rs. 5/day) via `fn_calculate_fine` into `Fines_Payments`.
8. **Test 8**: Fine payment procedure `pay_fine` with Cash, UPI, or Card, preventing duplicate settlement.
9. **Test 9**: Overdue loan detection via explicit cursor procedure `list_overdue_books`.
10. **Test 10**: Total copies adjustment invariant check (maintaining available stock consistency).
11. **Test 11**: Data integrity protection (duplicate email rejection and foreign-key delete guard).

*All test records are automatically rolled back or cleaned up after the test completes, leaving your database intact.*

---

## 🛠️ Windows Troubleshooting Guide

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| **"Could not connect to MySQL database"** | MySQL service is stopped or password mismatch. | 1. Open Windows Services (`services.msc`), find **MySQL80**, right-click and choose **Start**.<br>2. Check `DB_PASSWORD` in `config.py`. |
| **"Table or database does not exist"** | `library_management` DB was not initialized. | Run `Library_Management_System.sql` in MySQL Workbench or run: `mysql -u root -p < ..\Library_Management_System.sql`. |
| **"Port 5000 already in use"** | Another Flask process or app is running on port 5000. | Change port in `app.py` line `app.run(..., port=5001)` or close the other process. |
| **"python is not recognized"** | Python is not added to the Windows environment `PATH`. | Re-run the Python installer, select **Modify**, and check **"Add Python to PATH"**. |
