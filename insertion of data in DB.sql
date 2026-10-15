USE library_management;


-- =====================================================
-- 1. INSERT DATA INTO AUTHORS
-- =====================================================

INSERT INTO Authors
(Author_Name, Author_Email, City)
VALUES
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


-- =====================================================
-- 2. INSERT DATA INTO PUBLISHERS
-- =====================================================

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


-- =====================================================
-- 3. INSERT DATA INTO BOOKS
-- =====================================================

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


-- =====================================================
-- 4. INSERT DATA INTO MEMBERS
-- =====================================================

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


-- =====================================================
-- 5. VERIFY INSERTED DATA
-- =====================================================

SELECT * FROM Authors;

SELECT * FROM Publishers;

SELECT * FROM Books;

SELECT * FROM Members;


-- =====================================================
-- 6. CHECK TOTAL RECORDS
-- =====================================================

SELECT COUNT(*) AS Total_Authors
FROM Authors;

SELECT COUNT(*) AS Total_Publishers
FROM Publishers;

SELECT COUNT(*) AS Total_Books
FROM Books;

SELECT COUNT(*) AS Total_Members
FROM Members;