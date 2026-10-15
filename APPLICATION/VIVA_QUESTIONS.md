# 15 High-Probability Viva Questions & Concise Answers
**Project**: College Library Management System &bull; **Subject**: Database Management Systems (DMS 313302 &mdash; MSBTE K Scheme)

---

### Q1. What is the difference between a Stored Procedure and a Stored Function in MySQL? Give examples from your project.
**Answer:**
- **Stored Procedure** (e.g., `issue_book`, `return_book`): A precompiled block of SQL statements designed to execute business workflows. It can perform DML operations (INSERT, UPDATE, DELETE), manage transactions (`START TRANSACTION`, `COMMIT`, `ROLLBACK`), does not require returning a value, and is executed using `CALL procedure_name()`.
- **Stored Function** (e.g., `fn_calculate_fine`, `fn_check_availability`): A routine designed to compute and return exactly one scalar value (`RETURNS INT`, `RETURNS DECIMAL`). It can be invoked directly inside standard SQL queries (e.g. `SELECT fn_calculate_fine(Issue_ID)`).

---

### Q2. What is a Database Trigger, and how is it used in this project?
**Answer:**
A **Trigger** is a set of SQL statements that automatically executes (fires) in response to a specified event (`INSERT`, `UPDATE`, or `DELETE`) on a specific table.
In our project:
- Trigger **`trg_return_audit`** is an `AFTER UPDATE` trigger on `Book_Issues`.
- When a book's status changes from `Issued` to `Returned`, the trigger automatically captures the event and inserts a timestamped record into the `Audit_Log` table without requiring any manual application code.

---

### Q3. What is an Explicit Cursor, and where is it implemented in this system?
**Answer:**
A **Cursor** is a database pointer used to retrieve and process a query result set row-by-row rather than as a single bulk operation.
- In our project, procedure **`list_overdue_books()`** declares an explicit cursor (`cur_overdue`) to traverse all active book issues where `Due_Date < CURDATE()`.
- It uses `OPEN`, `FETCH`, a `CONTINUE HANDLER FOR NOT FOUND` loop condition, and `CLOSE` to insert overdue records and calculated days late into a temporary table for reporting.

---

### Q4. What is the purpose of `SIGNAL SQLSTATE '45000'` in MySQL stored procedures?
**Answer:**
`SIGNAL SQLSTATE '45000'` is the standard ANSI SQL instruction used to raise a user-defined custom exception from inside a stored procedure or trigger.
- Class `'45000'` represents an "unhandled user-defined exception".
- In our project, it stops execution, triggers automatic transaction `ROLLBACK`, and returns custom plain-language error messages such as `'Member already has 3 active books.'` or `'Book is currently unavailable.'`

---

### Q5. How does this system ensure ACID transaction properties during book circulation?
**Answer:**
Circulation operations (issuing/returning) touch multiple tables simultaneously:
1. **Atomicity**: Wrapped inside `START TRANSACTION ... COMMIT ... ROLLBACK`. If updating `Books` stock fails, the `Book_Issues` insert is automatically rolled back.
2. **Consistency**: Database `CHECK` constraints (`CHK_Available_Quantity`) and foreign keys prevent invalid states.
3. **Isolation**: Uses `SELECT ... FOR UPDATE` (pessimistic row locking) so two concurrent users cannot check out the last remaining copy at the same time.
4. **Durability**: InnoDB transaction logs ensure committed changes survive server crashes or power failures.

---

### Q6. Why is `SELECT ... FOR UPDATE` used in the `issue_book` procedure?
**Answer:**
`SELECT ... FOR UPDATE` applies an **exclusive row-level write lock** on the specific book record in the `Books` table until the transaction commits or rolls back. This prevents **race conditions** (concurrency conflicts) where two librarians attempt to issue the last available copy of the same book to two different members at the exact same split-second.

---

### Q7. What is Database Normalization, and what normal form does your database achieve?
**Answer:**
**Normalization** is the systematic process of organizing tables to eliminate data redundancy and modification anomalies (insertion, deletion, update).
- Our schema achieves **Third Normal Form (3NF)**:
  - **1NF**: All column values are atomic (indivisible), and there are no repeating groups.
  - **2NF**: In 1NF, and all non-key attributes are fully functionally dependent on the entire primary key (no partial dependencies).
  - **3NF**: In 2NF, and no non-key attribute is transitively dependent on another non-key attribute (e.g. Author details and Publisher details are segregated into separate tables referenced by Foreign Keys).

---

### Q8. What is the difference between an `INNER JOIN` and a `LEFT OUTER JOIN`? Where are they used in this project?
**Answer:**
- **`INNER JOIN`**: Returns only rows where there is a matching value in both joined tables.
  - *Example in project*: Joining `Books`, `Authors`, and `Publishers` to display catalog details (every book must have an author and publisher).
- **`LEFT OUTER JOIN`**: Returns all rows from the left table and matched rows from the right table; if no match exists, NULL values are returned for right-side columns.
  - *Example in project*: Joining `Members` to `Book_Issues` to display a list of all members, including those who have never borrowed any books.

---

### Q9. What is a Database View, and what benefit does `Current_Issued_Books` provide?
**Answer:**
A **View** is a virtual table based on the stored result-set of an SQL statement. It does not store physical data itself.
- **Benefits of `Current_Issued_Books`**:
  1. **Simplification**: Simplifies complex joins between `Book_Issues`, `Members`, and `Books` into a simple `SELECT * FROM Current_Issued_Books`.
  2. **Security**: Allows read access to currently issued titles and borrowers without exposing internal foreign key relationships or financial penalty data.

---

### Q10. What is the difference between a `PRIMARY KEY` and a `UNIQUE` constraint?
**Answer:**
- **`PRIMARY KEY`**: Uniquely identifies each record in a table. It cannot accept `NULL` values, and each table can have only **one** primary key (e.g., `Member_ID`, `Book_ID`).
- **`UNIQUE` constraint**: Ensures all values in a column are distinct, but allows a `NULL` value (unless defined `NOT NULL`). A table can have **multiple** unique constraints (e.g., `UK_Member_Email`, `UK_Author_Email`).

---

### Q11. How are overdue fines calculated, and where is this business rule implemented?
**Answer:**
- The rule states that loans last **14 days**, and overdue returns incur a fine of **Rs. 5.00 per day late**.
- This rule is implemented inside the database function **`fn_calculate_fine(p_issue_id)`**:
  $$\text{Days Late} = \text{DATEDIFF}(\text{COALESCE}(\text{Return\_Date}, \text{CURDATE()}), \text{Due\_Date})$$
  $$\text{Fine Amount} = \max(0, \text{Days Late}) \times 5.00$$
- When `return_book` is called, it queries `fn_calculate_fine` and automatically inserts a `Pending` record into `Fines_Payments` if the book was returned late.

---

### Q12. Explain the difference between DDL, DML, DCL, and TCL with an example of each from this project.
**Answer:**
1. **DDL (Data Definition Language)**: Defines and modifies schema structure.
   - *Example*: `CREATE TABLE Books (...)`, `ALTER TABLE ...`, `DROP DATABASE ...`
2. **DML (Data Manipulation Language)**: Manages and queries data tuples.
   - *Example*: `SELECT * FROM Books`, `INSERT INTO Members ...`, `UPDATE ...`, `DELETE ...`
3. **DCL (Data Control Language)**: Controls permissions and user rights.
   - *Example*: `CREATE USER 'library_staff'@'localhost'`, `GRANT SELECT, INSERT ON ...`
4. **TCL (Transaction Control Language)**: Manages transactional integrity.
   - *Example*: `START TRANSACTION`, `COMMIT`, `ROLLBACK`, `SAVEPOINT`

---

### Q13. What is an Index, and why was `idx_issue_member_book` created on `Book_Issues`?
**Answer:**
An **Index** is a data structure (typically a B-Tree) that the database storage engine uses to quickly locate rows without scanning the entire table sequentially.
- Index **`idx_issue_member_book`** was created on composite columns `(Member_ID, Book_ID)`.
- It speeds up the validation checks in procedure `issue_book`: verifying if a member already has 3 books or has borrowed the exact same book previously.

---

### Q14. What happens if staff attempts to delete an Author whose books exist in the library catalog?
**Answer:**
The database rejects the deletion with error `1451 (Foreign Key constraint failure)` because table `Books` has a foreign key constraint (`FK_Book_Author`) referencing `Authors(Author_ID)`.
- The application's error translation layer catches this constraint violation and displays a friendly message: *"Cannot delete this record because it has active references in other tables (e.g. books, loans, or fines)."*

---

### Q15. What is the difference between `DELETE`, `TRUNCATE`, and `DROP`?
**Answer:**
- **`DELETE`**: A DML command that removes specific rows matching a `WHERE` condition. It fires `DELETE` triggers, can be rolled back if inside a transaction, and does not reset `AUTO_INCREMENT`.
- **`TRUNCATE`**: A DDL command that deallocates all data pages in a table. It cannot be filtered with `WHERE`, resets `AUTO_INCREMENT` to 1, does not fire row triggers, and is much faster than `DELETE`.
- **`DROP`**: A DDL command that completely deletes the table definition, data, constraints, triggers, and associated indexes from the database dictionary.
