-- ============================================================
-- LIBRARY MANAGEMENT SYSTEM - FINAL CODE
-- DMS 313302 - MSBTE K Scheme
-- MySQL Workbench
-- ============================================================

-- This script can be run from the beginning again.
-- It recreates the database and all objects.

DROP DATABASE IF EXISTS library_management;
CREATE DATABASE library_management;
USE library_management;


-- ============================================================
-- 1. TABLES
-- ============================================================

CREATE TABLE Authors (
    Author_ID INT AUTO_INCREMENT PRIMARY KEY,
    Author_Name VARCHAR(50) NOT NULL,
    Author_Email VARCHAR(50) NOT NULL,
    City VARCHAR(50),

    CONSTRAINT UK_Author_Email
        UNIQUE (Author_Email)
);

CREATE TABLE Publishers (
    Publisher_ID INT AUTO_INCREMENT PRIMARY KEY,
    Publisher_Name VARCHAR(50) NOT NULL,
    Publisher_Email VARCHAR(50) NOT NULL,
    Publisher_Phone VARCHAR(15),
    Publisher_Address VARCHAR(100),

    CONSTRAINT UK_Publisher_Email
        UNIQUE (Publisher_Email)
);

CREATE TABLE Books (
    Book_ID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(100) NOT NULL,
    Author_ID INT NOT NULL,
    Publisher_ID INT NOT NULL,
    Genre VARCHAR(50) NOT NULL,
    Quantity INT NOT NULL,
    Available_Quantity INT NOT NULL,

    CONSTRAINT FK_Book_Author
        FOREIGN KEY (Author_ID)
        REFERENCES Authors(Author_ID),

    CONSTRAINT FK_Book_Publisher
        FOREIGN KEY (Publisher_ID)
        REFERENCES Publishers(Publisher_ID),

    CONSTRAINT CHK_Quantity
        CHECK (Quantity > 0),

    CONSTRAINT CHK_Available_Quantity
        CHECK (Available_Quantity >= 0
        AND Available_Quantity <= Quantity)
);

CREATE TABLE Members (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_Name VARCHAR(50) NOT NULL,
    Member_Email VARCHAR(50) NOT NULL,
    Member_Phone VARCHAR(15),
    Member_Address VARCHAR(100),

    CONSTRAINT UK_Member_Email
        UNIQUE (Member_Email)
);

CREATE TABLE Book_Issues (
    Issue_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_ID INT NOT NULL,
    Book_ID INT NOT NULL,
    Issue_Date DATE NOT NULL,
    Due_Date DATE NOT NULL,
    Return_Date DATE,
    Status VARCHAR(20) NOT NULL,

    CONSTRAINT FK_Issue_Member
        FOREIGN KEY (Member_ID)
        REFERENCES Members(Member_ID),

    CONSTRAINT FK_Issue_Book
        FOREIGN KEY (Book_ID)
        REFERENCES Books(Book_ID),

    CONSTRAINT CHK_Issue_Status
        CHECK (Status IN ('Issued', 'Returned')),

    CONSTRAINT CHK_Due_Date
        CHECK (Due_Date >= Issue_Date),

    CONSTRAINT CHK_Return_Date
        CHECK (Return_Date IS NULL OR Return_Date >= Issue_Date)
);

CREATE TABLE Fines_Payments (
    Fine_ID INT AUTO_INCREMENT PRIMARY KEY,
    Issue_ID INT NOT NULL,
    Fine_Amount DECIMAL(10,2) NOT NULL,
    Fine_Reason VARCHAR(100) NOT NULL,
    Payment_Status VARCHAR(20) NOT NULL,
    Payment_Mode VARCHAR(20),
    Payment_Date DATE,

    CONSTRAINT UK_Fine_Issue
        UNIQUE (Issue_ID),

    CONSTRAINT FK_Fine_Issue
        FOREIGN KEY (Issue_ID)
        REFERENCES Book_Issues(Issue_ID),

    CONSTRAINT CHK_Fine_Amount
        CHECK (Fine_Amount >= 0),

    CONSTRAINT CHK_Payment_Status
        CHECK (Payment_Status IN ('Pending', 'Paid'))
);

-- Trigger demonstration table
CREATE TABLE Audit_Log (
    Log_ID INT AUTO_INCREMENT PRIMARY KEY,
    Action_Description VARCHAR(255),
    Log_Time DATETIME
);


-- ============================================================
-- 2. CHECK TABLE STRUCTURE
-- ============================================================

DESCRIBE Authors;
DESCRIBE Publishers;
DESCRIBE Books;
DESCRIBE Members;
DESCRIBE Book_Issues;
DESCRIBE Fines_Payments;
DESCRIBE Audit_Log;


-- ============================================================
-- 3. SAMPLE DATA
-- ============================================================

INSERT INTO Authors (Author_Name, Author_Email, City) VALUES
('J.K. Rowling', 'jkrowling@gmail.com', 'London'),
('George Orwell', 'georgeorwell@gmail.com', 'London'),
('Robert C. Martin', 'robertmartin@gmail.com', 'New York'),
('Yuval Noah Harari', 'yuvalharari@gmail.com', 'Haifa'),
('Stephen King', 'stephenking@gmail.com', 'Portland'),
('Agatha Christie', 'agathachristie@gmail.com', 'Torquay'),
('Dan Brown', 'danbrown@gmail.com', 'New Hampshire'),
('R.K. Narayan', 'rknarayan@gmail.com', 'Chennai'),
('Chetan Bhagat', 'chetanbhagat@gmail.com', 'New Delhi'),
('A.P.J. Abdul Kalam', 'apjabdulkalam@gmail.com', 'Rameswaram');

INSERT INTO Publishers
(Publisher_Name, Publisher_Email, Publisher_Phone, Publisher_Address)
VALUES
('Bloomsbury', 'contact@bloomsbury.com', '9876543210', 'London, UK'),
('Penguin Books', 'contact@penguin.com', '9876543211', 'London, UK'),
('Pearson', 'contact@pearson.com', '9876543212', 'New York, USA'),
('HarperCollins', 'contact@harpercollins.com', '9876543213', 'New York, USA'),
('Doubleday', 'contact@doubleday.com', '9876543214', 'New York, USA'),
('Simon & Schuster', 'contact@simon.com', '9876543215', 'New York, USA'),
('Rupa Publications', 'contact@rupa.com', '9876543216', 'New Delhi, India'),
('Wings Publications', 'contact@wings.com', '9876543217', 'Chennai, India');

INSERT INTO Books
(Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity)
VALUES
('Harry Potter and the Philosophers Stone', 1, 1, 'Fantasy', 6, 6),
('Harry Potter and the Chamber of Secrets', 1, 1, 'Fantasy', 5, 5),
('1984', 2, 2, 'Dystopian', 6, 6),
('Animal Farm', 2, 2, 'Political Fiction', 4, 4),
('Clean Code', 3, 3, 'Technology', 5, 5),
('The Clean Coder', 3, 3, 'Technology', 4, 4),
('Sapiens', 4, 4, 'History', 6, 6),
('Homo Deus', 4, 4, 'History', 4, 4),
('The Shining', 5, 5, 'Horror', 5, 5),
('It', 5, 5, 'Horror', 4, 4),
('Murder on the Orient Express', 6, 6, 'Mystery', 5, 5),
('And Then There Were None', 6, 6, 'Mystery', 4, 4),
('The Da Vinci Code', 7, 5, 'Thriller', 6, 6),
('Angels and Demons', 7, 5, 'Thriller', 5, 5),
('Swami and Friends', 8, 7, 'Fiction', 4, 4),
('The Guide', 8, 7, 'Fiction', 5, 5),
('Five Point Someone', 9, 7, 'Fiction', 5, 5),
('2 States', 9, 7, 'Romance', 4, 4),
('Wings of Fire', 10, 8, 'Biography', 6, 6),
('Ignited Minds', 10, 8, 'Motivational', 5, 5);

INSERT INTO Members
(Member_Name, Member_Email, Member_Phone, Member_Address)
VALUES
('Aarav Sharma', 'aarav@gmail.com', '9876500001', 'Mumbai, Maharashtra'),
('Riya Patil', 'riya@gmail.com', '9876500002', 'Navi Mumbai, Maharashtra'),
('Rahul Mehta', 'rahul@gmail.com', '9876500003', 'Thane, Maharashtra'),
('Sneha Joshi', 'sneha@gmail.com', '9876500004', 'Pune, Maharashtra'),
('Aditya Shah', 'aditya@gmail.com', '9876500005', 'Mumbai, Maharashtra'),
('Neha Kulkarni', 'neha@gmail.com', '9876500006', 'Nashik, Maharashtra'),
('Om Deshmukh', 'om@gmail.com', '9876500007', 'Nagpur, Maharashtra'),
('Isha More', 'isha@gmail.com', '9876500008', 'Aurangabad, Maharashtra'),
('Karan Gupta', 'karan@gmail.com', '9876500009', 'Mumbai, Maharashtra'),
('Pooja Verma', 'pooja@gmail.com', '9876500010', 'Thane, Maharashtra'),
('Vivek Joshi', 'vivek@gmail.com', '9876500011', 'Pune, Maharashtra'),
('Ananya Singh', 'ananya@gmail.com', '9876500012', 'Mumbai, Maharashtra'),
('Rohan Patil', 'rohan@gmail.com', '9876500013', 'Kolhapur, Maharashtra'),
('Meera Shah', 'meera@gmail.com', '9876500014', 'Navi Mumbai, Maharashtra'),
('Arjun Nair', 'arjun@gmail.com', '9876500015', 'Mumbai, Maharashtra');


-- ============================================================
-- 4. BASIC DML
-- ============================================================

-- UPDATE
UPDATE Members
SET Member_Phone = '9876500099'
WHERE Member_ID = 1;

UPDATE Books
SET Genre = 'Classic Fiction'
WHERE Book_ID = 3;

-- DELETE
INSERT INTO Publishers
(Publisher_Name, Publisher_Email, Publisher_Phone, Publisher_Address)
VALUES
('Test Publisher', 'test@publisher.com', '0000000000', 'Test City');

DELETE FROM Publishers
WHERE Publisher_Email = 'test@publisher.com';


-- ============================================================
-- 5. BASIC SELECT
-- ============================================================

SELECT * FROM Authors;
SELECT * FROM Publishers;
SELECT * FROM Books;
SELECT * FROM Members;
SELECT * FROM Book_Issues;
SELECT * FROM Fines_Payments;

-- WHERE
SELECT *
FROM Books
WHERE Genre = 'Technology';

-- ORDER BY
SELECT *
FROM Books
ORDER BY Title;

-- DISTINCT
SELECT DISTINCT Genre
FROM Books;

-- BETWEEN
SELECT *
FROM Books
WHERE Quantity BETWEEN 4 AND 6;

-- LIKE
SELECT *
FROM Members
WHERE Member_Name LIKE 'A%';


-- ============================================================
-- 6. AGGREGATE FUNCTIONS
-- ============================================================

SELECT COUNT(*) AS Total_Books
FROM Books;

SELECT SUM(Quantity) AS Total_Copies
FROM Books;

SELECT AVG(Quantity) AS Average_Quantity
FROM Books;

SELECT MAX(Quantity) AS Maximum_Quantity
FROM Books;

SELECT MIN(Quantity) AS Minimum_Quantity
FROM Books;

-- GROUP BY
SELECT Genre, COUNT(*) AS Total_Books
FROM Books
GROUP BY Genre;

-- HAVING
SELECT Genre, COUNT(*) AS Total_Books
FROM Books
GROUP BY Genre
HAVING COUNT(*) > 1;


-- ============================================================
-- 7. STRING AND DATE FUNCTIONS
-- ============================================================

SELECT UPPER(Member_Name) AS Member_Name
FROM Members;

SELECT LOWER(Member_Name) AS Member_Name
FROM Members;

SELECT CONCAT(Member_Name, ' - ', Member_Email) AS Member_Details
FROM Members;

SELECT CURDATE() AS Today;

SELECT DATE_ADD(CURDATE(), INTERVAL 14 DAY) AS Due_Date;


-- ============================================================
-- 8. JOINS
-- ============================================================

-- INNER JOIN
SELECT
    Books.Title,
    Authors.Author_Name,
    Publishers.Publisher_Name,
    Books.Genre
FROM Books
INNER JOIN Authors
ON Books.Author_ID = Authors.Author_ID
INNER JOIN Publishers
ON Books.Publisher_ID = Publishers.Publisher_ID;

-- LEFT JOIN
SELECT
    Members.Member_Name,
    Book_Issues.Issue_ID,
    Books.Title,
    Book_Issues.Status
FROM Members
LEFT JOIN Book_Issues
ON Members.Member_ID = Book_Issues.Member_ID
LEFT JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID
ORDER BY Members.Member_Name;


-- ============================================================
-- 9. SUBQUERIES
-- ============================================================

-- Books with quantity greater than average
SELECT Title, Quantity
FROM Books
WHERE Quantity > (
    SELECT AVG(Quantity)
    FROM Books
);

-- Members who issued a book
SELECT Member_Name
FROM Members
WHERE Member_ID IN (
    SELECT Member_ID
    FROM Book_Issues
);


-- ============================================================
-- 10. SET OPERATION
-- ============================================================

SELECT Author_Name AS Person_Name
FROM Authors
UNION
SELECT Member_Name AS Person_Name
FROM Members;


-- ============================================================
-- 11. INDEX
-- ============================================================

CREATE INDEX idx_issue_member_book
ON Book_Issues(Member_ID, Book_ID);


-- ============================================================
-- 12. VIEW
-- ============================================================

CREATE OR REPLACE VIEW Current_Issued_Books AS
SELECT
    Book_Issues.Issue_ID,
    Members.Member_Name,
    Books.Title,
    Book_Issues.Issue_Date,
    Book_Issues.Due_Date
FROM Book_Issues
INNER JOIN Members
ON Book_Issues.Member_ID = Members.Member_ID
INNER JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID
WHERE Book_Issues.Status = 'Issued';

SELECT * FROM Current_Issued_Books;


-- ============================================================
-- 13. FUNCTION - CHECK AVAILABILITY
-- ============================================================

DELIMITER $$

CREATE FUNCTION fn_check_availability(p_book_id INT)
RETURNS INT
READS SQL DATA
BEGIN
    DECLARE v_available INT DEFAULT 0;

    SELECT COALESCE(MAX(Available_Quantity), 0)
    INTO v_available
    FROM Books
    WHERE Book_ID = p_book_id;

    RETURN v_available;
END$$

DELIMITER ;


-- ============================================================
-- 14. FUNCTION - CALCULATE FINE
-- Rs.5 per late day
-- ============================================================

DELIMITER $$

CREATE FUNCTION fn_calculate_fine(p_issue_id INT)
RETURNS DECIMAL(10,2)
NOT DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE v_due_date DATE;
    DECLARE v_return_date DATE;
    DECLARE v_days_late INT DEFAULT 0;

    SELECT Due_Date,
           COALESCE(Return_Date, CURDATE())
    INTO v_due_date, v_return_date
    FROM Book_Issues
    WHERE Issue_ID = p_issue_id;

    SET v_days_late = DATEDIFF(v_return_date, v_due_date);

    IF v_days_late > 0 THEN
        RETURN v_days_late * 5.00;
    ELSE
        RETURN 0.00;
    END IF;
END$$

DELIMITER ;


-- ============================================================
-- 15. TRIGGER - RETURN AUDIT
-- ============================================================

DELIMITER $$

CREATE TRIGGER trg_return_audit
AFTER UPDATE ON Book_Issues
FOR EACH ROW
BEGIN
    IF NEW.Status = 'Returned'
       AND OLD.Status <> 'Returned' THEN

        INSERT INTO Audit_Log
        (Action_Description, Log_Time)
        VALUES
        (
            CONCAT('Book returned. Issue ID: ', NEW.Issue_ID),
            NOW()
        );

    END IF;
END$$

DELIMITER ;


-- ============================================================
-- 16. PROCEDURE - ISSUE BOOK
--
-- Rules:
-- 1. Member must exist.
-- 2. Book must exist.
-- 3. Book must be available.
-- 4. Same member cannot issue same book twice.
-- 5. A member can have maximum 3 active books.
-- ============================================================

DELIMITER $$

CREATE PROCEDURE issue_book(
    IN p_member_id INT,
    IN p_book_id INT
)
BEGIN
    DECLARE v_member_count INT DEFAULT 0;
    DECLARE v_book_count INT DEFAULT 0;
    DECLARE v_available INT DEFAULT 0;
    DECLARE v_old_issue INT DEFAULT 0;
    DECLARE v_active_issues INT DEFAULT 0;
    DECLARE v_book_name VARCHAR(100);
    DECLARE v_old_date DATE;
    DECLARE v_error_message VARCHAR(128);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check member
    SELECT COUNT(*)
    INTO v_member_count
    FROM Members
    WHERE Member_ID = p_member_id;

    IF v_member_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Member does not exist.';
    END IF;

    -- Check book
    SELECT COUNT(*)
    INTO v_book_count
    FROM Books
    WHERE Book_ID = p_book_id;

    IF v_book_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Book does not exist.';
    END IF;

    -- Get book details and lock the book row during the transaction
    SELECT Title, Available_Quantity
    INTO v_book_name, v_available
    FROM Books
    WHERE Book_ID = p_book_id
    FOR UPDATE;

    -- Check availability
    IF v_available <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Book is currently unavailable.';
    END IF;

    -- Check same member + same book
    SELECT COUNT(*)
    INTO v_old_issue
    FROM Book_Issues
    WHERE Member_ID = p_member_id
      AND Book_ID = p_book_id
      AND Status = 'Issued'
      AND Return_Date IS NULL;

    IF v_old_issue > 0 THEN

        SELECT Issue_Date
        INTO v_old_date
        FROM Book_Issues
        WHERE Member_ID = p_member_id
          AND Book_ID = p_book_id
          AND Status = 'Issued'
          AND Return_Date IS NULL
        ORDER BY Issue_ID DESC
        LIMIT 1;

        SET v_error_message = CONCAT(
            'Book ', v_book_name,
            ' was already issued on ', DATE_FORMAT(v_old_date, '%Y-%m-%d'),
            '. Please return it first.'
        );

        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = v_error_message;
    END IF;

    -- Check maximum 3 books
    SELECT COUNT(*)
    INTO v_active_issues
    FROM Book_Issues
    WHERE Member_ID = p_member_id
      AND Status = 'Issued'
      AND Return_Date IS NULL;

    IF v_active_issues >= 3 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Member already has 3 active books.';
    END IF;

    -- Insert issue
    INSERT INTO Book_Issues
    (
        Member_ID,
        Book_ID,
        Issue_Date,
        Due_Date,
        Return_Date,
        Status
    )
    VALUES
    (
        p_member_id,
        p_book_id,
        CURDATE(),
        DATE_ADD(CURDATE(), INTERVAL 14 DAY),
        NULL,
        'Issued'
    );

    -- Reduce available copies
    UPDATE Books
    SET Available_Quantity = Available_Quantity - 1
    WHERE Book_ID = p_book_id;

    COMMIT;

    SELECT
        'Book issued successfully.' AS Message,
        v_book_name AS Book,
        CURDATE() AS Issue_Date,
        DATE_ADD(CURDATE(), INTERVAL 14 DAY) AS Due_Date;
END$$

DELIMITER ;


-- ============================================================
-- 17. PROCEDURE - RETURN BOOK
-- ============================================================

DELIMITER $$

CREATE PROCEDURE return_book(
    IN p_issue_id INT
)
BEGIN
    DECLARE v_issue_count INT DEFAULT 0;
    DECLARE v_status VARCHAR(20);
    DECLARE v_book_id INT;
    DECLARE v_fine DECIMAL(10,2) DEFAULT 0.00;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;

    -- Check issue
    SELECT COUNT(*)
    INTO v_issue_count
    FROM Book_Issues
    WHERE Issue_ID = p_issue_id;

    IF v_issue_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Issue record does not exist.';
    END IF;

    -- Get issue details
    SELECT Status, Book_ID
    INTO v_status, v_book_id
    FROM Book_Issues
    WHERE Issue_ID = p_issue_id
    FOR UPDATE;

    -- Check already returned
    IF v_status = 'Returned' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'This book is already returned.';
    END IF;

    -- Return book
    UPDATE Book_Issues
    SET Return_Date = CURDATE(),
        Status = 'Returned'
    WHERE Issue_ID = p_issue_id;

    -- Increase available copies
    UPDATE Books
    SET Available_Quantity = Available_Quantity + 1
    WHERE Book_ID = v_book_id;

    -- Calculate fine
    SET v_fine = fn_calculate_fine(p_issue_id);

    -- Create fine if late
    IF v_fine > 0 THEN

        INSERT INTO Fines_Payments
        (
            Issue_ID,
            Fine_Amount,
            Fine_Reason,
            Payment_Status,
            Payment_Mode,
            Payment_Date
        )
        VALUES
        (
            p_issue_id,
            v_fine,
            'Late return',
            'Pending',
            NULL,
            NULL
        );

    END IF;

    COMMIT;

    SELECT
        'Book returned successfully.' AS Message,
        v_fine AS Fine_Amount;
END$$

DELIMITER ;


-- ============================================================
-- 18. PROCEDURE - PAY FINE
-- ============================================================

DELIMITER $$

CREATE PROCEDURE pay_fine(
    IN p_issue_id INT,
    IN p_payment_mode VARCHAR(20)
)
BEGIN
    DECLARE v_fine_count INT DEFAULT 0;
    DECLARE v_status VARCHAR(20);

    SELECT COUNT(*)
    INTO v_fine_count
    FROM Fines_Payments
    WHERE Issue_ID = p_issue_id;

    IF v_fine_count = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Fine record does not exist.';
    END IF;

    SELECT Payment_Status
    INTO v_status
    FROM Fines_Payments
    WHERE Issue_ID = p_issue_id;

    IF v_status = 'Paid' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Fine is already paid.';
    END IF;

    UPDATE Fines_Payments
    SET Payment_Status = 'Paid',
        Payment_Mode = p_payment_mode,
        Payment_Date = CURDATE()
    WHERE Issue_ID = p_issue_id;

    SELECT 'Fine paid successfully.' AS Message;
END$$

DELIMITER ;


-- ============================================================
-- 19. PROCEDURE - OVERDUE BOOKS
-- Explicit cursor + NOT FOUND handler
-- ============================================================

DELIMITER $$

CREATE PROCEDURE list_overdue_books()
BEGIN
    DECLARE v_issue_id INT;
    DECLARE v_member_id INT;
    DECLARE v_book_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_done INT DEFAULT 0;

    DECLARE cur_overdue CURSOR FOR
        SELECT Issue_ID, Member_ID, Book_ID, Due_Date
        FROM Book_Issues
        WHERE Status = 'Issued'
          AND Due_Date < CURDATE();

    DECLARE CONTINUE HANDLER FOR NOT FOUND
        SET v_done = 1;

    DROP TEMPORARY TABLE IF EXISTS Overdue_Books;

    CREATE TEMPORARY TABLE Overdue_Books
    (
        Issue_ID INT,
        Member_Name VARCHAR(50),
        Book_Title VARCHAR(100),
        Due_Date DATE,
        Days_Late INT
    );

    OPEN cur_overdue;

    read_loop: LOOP

        FETCH cur_overdue
        INTO v_issue_id, v_member_id, v_book_id, v_due_date;

        IF v_done = 1 THEN
            LEAVE read_loop;
        END IF;

        INSERT INTO Overdue_Books
        SELECT
            v_issue_id,
            Members.Member_Name,
            Books.Title,
            v_due_date,
            DATEDIFF(CURDATE(), v_due_date)
        FROM Members
        INNER JOIN Books
        ON Books.Book_ID = v_book_id
        WHERE Members.Member_ID = v_member_id;

    END LOOP;

    CLOSE cur_overdue;

    SELECT * FROM Overdue_Books;

    DROP TEMPORARY TABLE Overdue_Books;
END$$

DELIMITER ;


-- ============================================================
-- 20. DCL
-- Run these commands only if you are using MySQL root/admin.
-- They are commented so the main project runs safely.
-- ============================================================

-- CREATE USER 'library_staff'@'localhost'
-- IDENTIFIED BY 'Library123';

-- GRANT SELECT, INSERT, UPDATE
-- ON library_management.*
-- TO 'library_staff'@'localhost';

-- REVOKE UPDATE
-- ON library_management.*
-- FROM 'library_staff'@'localhost';


-- ============================================================
-- 21. TCL - SAFE COMMIT DEMONSTRATION
-- A temporary table is used so real library quantities are not changed.
-- ============================================================

CREATE TEMPORARY TABLE TCL_Test
(
    Test_ID INT PRIMARY KEY,
    Test_Value INT
);

INSERT INTO TCL_Test
VALUES (1, 10);

START TRANSACTION;

UPDATE TCL_Test
SET Test_Value = Test_Value + 5
WHERE Test_ID = 1;

COMMIT;

SELECT * FROM TCL_Test;


-- ============================================================
-- 22. TCL - SAVEPOINT AND ROLLBACK
-- ============================================================

START TRANSACTION;

UPDATE TCL_Test
SET Test_Value = Test_Value + 10
WHERE Test_ID = 1;

SAVEPOINT before_second_update;

UPDATE TCL_Test
SET Test_Value = Test_Value + 20
WHERE Test_ID = 1;

ROLLBACK TO before_second_update;

COMMIT;

SELECT * FROM TCL_Test;


-- ============================================================
-- 23. TCL - FULL ROLLBACK
-- ============================================================

START TRANSACTION;

UPDATE TCL_Test
SET Test_Value = Test_Value + 100
WHERE Test_ID = 1;

ROLLBACK;

SELECT * FROM TCL_Test;

DROP TEMPORARY TABLE TCL_Test;


-- ============================================================
-- 24. TEST THE PROJECT
-- ============================================================

-- Test 1: Issue a book
CALL issue_book(1, 5);

-- Test 2: Make Issue_ID 1 overdue for cursor demonstration.
-- This changes only the test issue created above.
UPDATE Book_Issues
SET Issue_Date = DATE_SUB(CURDATE(), INTERVAL 21 DAY),
    Due_Date = DATE_SUB(CURDATE(), INTERVAL 7 DAY)
WHERE Issue_ID = 1;

-- Test 3: Run explicit cursor.
CALL list_overdue_books();

-- Test 4: Same member tries to issue same book again.
-- Run separately. It should give an error.
-- CALL issue_book(1, 5);

-- Test 5: Issue another book to the same member.
-- CALL issue_book(1, 6);

-- Test 6: Return a book.
-- Use the actual Issue_ID shown in Book_Issues.
-- CALL return_book(1);

-- Test 7: Pay a fine if one exists.
-- CALL pay_fine(1, 'Cash');


-- ============================================================
-- 25. FINAL REPORT QUERIES
-- ============================================================

-- All currently issued books
SELECT
    Book_Issues.Issue_ID,
    Members.Member_Name,
    Books.Title,
    Book_Issues.Issue_Date,
    Book_Issues.Due_Date,
    Book_Issues.Status
FROM Book_Issues
INNER JOIN Members
ON Book_Issues.Member_ID = Members.Member_ID
INNER JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID
WHERE Book_Issues.Status = 'Issued';

-- All returned books
SELECT
    Book_Issues.Issue_ID,
    Members.Member_Name,
    Books.Title,
    Book_Issues.Return_Date
FROM Book_Issues
INNER JOIN Members
ON Book_Issues.Member_ID = Members.Member_ID
INNER JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID
WHERE Book_Issues.Status = 'Returned';

-- Fine report
SELECT
    Fines_Payments.Fine_ID,
    Members.Member_Name,
    Books.Title,
    Fines_Payments.Fine_Amount,
    Fines_Payments.Fine_Reason,
    Fines_Payments.Payment_Status,
    Fines_Payments.Payment_Mode
FROM Fines_Payments
INNER JOIN Book_Issues
ON Fines_Payments.Issue_ID = Book_Issues.Issue_ID
INNER JOIN Members
ON Book_Issues.Member_ID = Members.Member_ID
INNER JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID;

-- Audit report
SELECT * FROM Audit_Log;

-- Books with low availability
SELECT
    Title,
    Quantity,
    Available_Quantity
FROM Books
WHERE Available_Quantity <= 2;

-- Function test
SELECT fn_check_availability(5) AS Available_Copies;

-- Fine function test
-- SELECT fn_calculate_fine(1) AS Fine_Amount;


-- ============================================================
-- END OF LIBRARY MANAGEMENT SYSTEM
-- ============================================================
