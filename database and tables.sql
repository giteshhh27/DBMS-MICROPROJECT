CREATE DATABASE library_management;
USE library_management;

CREATE TABLE Authors (
	Author_ID INT AUTO_INCREMENT PRIMARY KEY,
    Author_Name VARCHAR(50) NOT NULL,
    Author_Email VARCHAR(50) NOT NULL,
    City VARCHAR(50),
    
    CONSTRAINT UK_Author_Email UNIQUE(Author_Email)
);

CREATE TABLE Publishers (
	Publisher_ID INT AUTO_INCREMENT PRIMARY KEY,
    Publisher_Name VARCHAR(50) NOT NULL,
    Publisher_Email VARCHAR(50) NOT NULL,
    Publisher_Phone	VARCHAR(15),
    Publisher_Address VARCHAR(100),
    
    CONSTRAINT UK_Publisher_Email UNIQUE (Publisher_Email)
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
        REFERENCES Publishers(Publisher_ID)
);

CREATE TABLE Members (
    Member_ID INT AUTO_INCREMENT PRIMARY KEY,
    Member_Name VARCHAR(50) NOT NULL,
    Member_Email VARCHAR(50) NOT NULL,
    Member_Phone VARCHAR(15),
    Member_Address VARCHAR(100),

    CONSTRAINT UK_Member_Email UNIQUE (Member_Email)
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
        REFERENCES Books(Book_ID)
);

CREATE TABLE Fines_Payments (
    Fine_ID INT AUTO_INCREMENT PRIMARY KEY,
    Issue_ID INT NOT NULL,
    Fine_Amount DECIMAL(10,2) NOT NULL,
    Fine_Reason VARCHAR(100) NOT NULL,
    Payment_Status VARCHAR(20) NOT NULL,
    Payment_Mode VARCHAR(20),
    Payment_Date DATE,

    CONSTRAINT FK_Fine_Issue
        FOREIGN KEY (Issue_ID)
        REFERENCES Book_Issues(Issue_ID)
);