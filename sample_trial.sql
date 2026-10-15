USE library_management;
-- 1st
SHOW TABLES;

-- 2nd
SELECT * FROM Books;
SELECT * FROM Members;
SELECT * FROM Book_Issues;
-- 3rd
SELECT
    Book_Issues.Issue_ID,
    Members.Member_Name,
    Books.Title,
    Book_Issues.Issue_Date,
    Book_Issues.Due_Date,
    Book_Issues.Return_Date,
    Book_Issues.Status
FROM Book_Issues
INNER JOIN Members
ON Book_Issues.Member_ID = Members.Member_ID
INNER JOIN Books
ON Book_Issues.Book_ID = Books.Book_ID;

-- 4th 

SELECT * FROM Current_Issued_Books;

-- 5th
SHOW INDEX FROM Book_Issues;

-- 6th
SELECT fn_check_availability(5) AS Available_Copies;

-- 7th this must return fine amount.
SELECT fn_calculate_fine(1) AS Fine_Amount;

-- 8th maybe cursor
CALL list_overdue_books();

SELECT * FROM Current_Issued_Books;


SELECT
    Book_ID,
    Title,
    Quantity,
    Available_Quantity
FROM Books;
CALL return_book(2);

-- 9 issuing more books
CALL issue_book(2, 1);
CALL issue_book(3, 2);
CALL issue_book(4, 3);
CALL issue_book(5, 4);
CALL issue_book(6, 5);
CALL issue_book(7, 6);
CALL issue_book(8, 7);

ROLLBACK;