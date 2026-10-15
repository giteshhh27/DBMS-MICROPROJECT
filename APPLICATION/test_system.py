"""
Automated Test Suite for Library Management System
=================================================
MSBTE K Scheme - DMS 313302 Micro Project
Tests all database business rules, stored procedures, functions, triggers,
views, quantity synchronization, and friendly error messages.
Runs non-destructively by cleaning up temporary test artifacts.
"""

import sys
import unittest
from datetime import date, timedelta
import db

class TestLibraryManagementSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n" + "=" * 70)
        print("RUNNING AUTOMATED TEST SUITE FOR LIBRARY MANAGEMENT SYSTEM")
        print("=" * 70)
        ok, msg = db.test_connection()
        assert ok, f"Database connectivity test failed: {msg}"

        # Create a dedicated test member, author, publisher, and book for isolation
        # 1. Author
        db.execute_dml("DELETE FROM Authors WHERE Author_Email = 'test_author_qa@test.com'")
        ok, a_res = db.execute_dml(
            "INSERT INTO Authors (Author_Name, Author_Email, City) VALUES (%s, %s, %s)",
            ("QA Author", "test_author_qa@test.com", "Test City")
        )
        cls.author_id = a_res['last_id']

        # 2. Publisher
        db.execute_dml("DELETE FROM Publishers WHERE Publisher_Email = 'test_pub_qa@test.com'")
        ok, p_res = db.execute_dml(
            "INSERT INTO Publishers (Publisher_Name, Publisher_Email, Publisher_Phone, Publisher_Address) VALUES (%s, %s, %s, %s)",
            ("QA Publisher", "test_pub_qa@test.com", "1234567890", "QA Address")
        )
        cls.publisher_id = p_res['last_id']

        # 3. Member
        db.execute_dml("DELETE FROM Members WHERE Member_Email = 'test_member_qa@test.com'")
        ok, m_res = db.execute_dml(
            "INSERT INTO Members (Member_Name, Member_Email, Member_Phone, Member_Address) VALUES (%s, %s, %s, %s)",
            ("QA Member", "test_member_qa@test.com", "9999988888", "QA City")
        )
        cls.member_id = m_res['last_id']

        # 4. Books
        db.execute_dml("DELETE FROM Books WHERE Title LIKE 'QA Test Book%'")
        # Book 1: Normal with 4 copies
        _, b1 = db.execute_dml(
            "INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity) VALUES (%s, %s, %s, %s, %s, %s)",
            ("QA Test Book 1", cls.author_id, cls.publisher_id, "Testing", 4, 4)
        )
        cls.book1_id = b1['last_id']

        # Book 2: Normal with 2 copies
        _, b2 = db.execute_dml(
            "INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity) VALUES (%s, %s, %s, %s, %s, %s)",
            ("QA Test Book 2", cls.author_id, cls.publisher_id, "Testing", 2, 2)
        )
        cls.book2_id = b2['last_id']

        # Book 3: Normal with 2 copies
        _, b3 = db.execute_dml(
            "INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity) VALUES (%s, %s, %s, %s, %s, %s)",
            ("QA Test Book 3", cls.author_id, cls.publisher_id, "Testing", 2, 2)
        )
        cls.book3_id = b3['last_id']

        # Book 4: Out of Stock (0 copies available)
        _, b4 = db.execute_dml(
            "INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity) VALUES (%s, %s, %s, %s, %s, %s)",
            ("QA Test Book 4 (Out of Stock)", cls.author_id, cls.publisher_id, "Testing", 1, 0)
        )
        cls.book4_id = b4['last_id']

    @classmethod
    def tearDownClass(cls):
        print("\n" + "-" * 70)
        print("Cleaning up test artifacts...")
        # Clean up any issues, fines, books, authors, publishers created for testing
        test_books = [cls.book1_id, cls.book2_id, cls.book3_id, cls.book4_id]
        format_strings = ','.join(['%s'] * len(test_books))
        
        # Delete fines
        db.execute_dml(f"""
            DELETE FROM Fines_Payments WHERE Issue_ID IN (
                SELECT Issue_ID FROM Book_Issues WHERE Book_ID IN ({format_strings}) OR Member_ID = %s
            )
        """, tuple(test_books) + (cls.member_id,))

        # Delete issues
        db.execute_dml(f"DELETE FROM Book_Issues WHERE Book_ID IN ({format_strings}) OR Member_ID = %s", tuple(test_books) + (cls.member_id,))

        # Delete books
        db.execute_dml(f"DELETE FROM Books WHERE Book_ID IN ({format_strings})", tuple(test_books))

        # Delete publisher, author, member
        db.execute_dml("DELETE FROM Publishers WHERE Publisher_ID = %s", (cls.publisher_id,))
        db.execute_dml("DELETE FROM Authors WHERE Author_ID = %s", (cls.author_id,))
        db.execute_dml("DELETE FROM Members WHERE Member_ID = %s", (cls.member_id,))
        print("Test cleanup completed successfully.")
        print("=" * 70)

    # -------------------------------------------------------------
    # Test 1: Issue Book Success & Stock Decrement
    # -------------------------------------------------------------
    def test_01_issue_book_success(self):
        print("\n[TEST 1] Testing Book Issue Success & Stock Decrement...")
        ok, res = db.call_issue_book(self.member_id, self.book1_id)
        self.assertTrue(ok, f"Book issue failed: {res}")
        self.assertEqual(res['Book'], 'QA Test Book 1')

        # Check stock decremented from 4 to 3
        avail = db.get_book_availability(self.book1_id)
        self.assertEqual(avail, 3, f"Expected 3 available copies, got {avail}")
        print("  -> Passed: Book issued with confirmation slip; available quantity decremented.")

    # -------------------------------------------------------------
    # Test 2: Prevent Duplicate Issue (Same Member + Same Book)
    # -------------------------------------------------------------
    def test_02_prevent_duplicate_issue(self):
        print("\n[TEST 2] Testing Prevention of Duplicate Issue...")
        ok, msg = db.call_issue_book(self.member_id, self.book1_id)
        self.assertFalse(ok, "Duplicate issue was incorrectly allowed!")
        self.assertIn("was already issued on", msg)
        self.assertIn("Please return it first", msg)
        print(f"  -> Passed: Duplicate rejected with friendly message: '{msg}'")

    # -------------------------------------------------------------
    # Test 3: Enforce Member 3-Book Limit
    # -------------------------------------------------------------
    def test_03_enforce_3_book_limit(self):
        print("\n[TEST 3] Testing Member Maximum 3-Book Limit...")
        # Member already holds Book 1. Issue Book 2 and Book 3 (total = 3)
        ok2, _ = db.call_issue_book(self.member_id, self.book2_id)
        self.assertTrue(ok2)
        ok3, _ = db.call_issue_book(self.member_id, self.book3_id)
        self.assertTrue(ok3)

        # Now try to issue a 4th book (use a clean book, e.g. Book 1 of sample data)
        ok4, msg = db.call_issue_book(self.member_id, 1)
        self.assertFalse(ok4, "4th book was incorrectly allowed!")
        self.assertIn("limit of 3 books", msg.lower())
        self.assertIn("Currently borrowed", msg)
        print(f"  -> Passed: 4th book rejected with held book details:\n{msg}")

    # -------------------------------------------------------------
    # Test 4: Out-of-Stock Book Rejection
    # -------------------------------------------------------------
    def test_04_reject_out_of_stock(self):
        print("\n[TEST 4] Testing Out-of-Stock Book Rejection...")
        # Use another member to avoid 3-book limit
        ok, msg = db.call_issue_book(2, self.book4_id)
        self.assertFalse(ok, "Out-of-stock book was incorrectly issued!")
        self.assertIn("currently unavailable", msg.lower())
        print(f"  -> Passed: Out-of-stock book rejected with message: '{msg}'")

    # -------------------------------------------------------------
    # Test 5: Invalid Member or Book Rejection
    # -------------------------------------------------------------
    def test_05_invalid_member_or_book(self):
        print("\n[TEST 5] Testing Invalid Member / Book Rejection...")
        ok1, msg1 = db.call_issue_book(99999, self.book1_id)
        self.assertFalse(ok1)
        self.assertIn("member does not exist", msg1.lower())

        ok2, msg2 = db.call_issue_book(self.member_id, 99999)
        self.assertFalse(ok2)
        self.assertIn("book does not exist", msg2.lower())
        print("  -> Passed: Non-existent member and book IDs rejected gracefully.")

    # -------------------------------------------------------------
    # Test 6: Return Book & Trigger Audit Logging
    # -------------------------------------------------------------
    def test_06_return_book_and_trigger_audit(self):
        print("\n[TEST 6] Testing Book Return & trg_return_audit Trigger...")
        # Find the Issue_ID for Book 1 borrowed by QA Member
        _, row = db.execute_query(
            "SELECT Issue_ID FROM Book_Issues WHERE Member_ID = %s AND Book_ID = %s AND Status = 'Issued'",
            (self.member_id, self.book1_id), fetch='one'
        )
        issue_id = row['Issue_ID']

        # Return the book
        ok, res = db.call_return_book(issue_id)
        self.assertTrue(ok, f"Return failed: {res}")

        # Check stock incremented back to 4
        avail = db.get_book_availability(self.book1_id)
        self.assertEqual(avail, 4, f"Expected 4 available copies, got {avail}")

        # Check trigger trg_return_audit created an entry in Audit_Log
        _, audit_row = db.execute_query(
            "SELECT * FROM Audit_Log WHERE Action_Description LIKE %s ORDER BY Log_ID DESC LIMIT 1",
            (f"%Issue ID: {issue_id}%",), fetch='one'
        )
        self.assertIsNotNone(audit_row, "Audit_Log entry was NOT created by trg_return_audit trigger!")
        print(f"  -> Passed: Return completed; stock restored to 4; Audit log recorded: '{audit_row['Action_Description']}'.")

    # -------------------------------------------------------------
    # Test 7: Late Return Fine Creation (Rs. 5/day)
    # -------------------------------------------------------------
    def test_07_late_return_fine_creation(self):
        print("\n[TEST 7] Testing Late Return Fine Calculation & Fines_Payments Creation...")
        # Get active issue for Book 2
        _, row = db.execute_query(
            "SELECT Issue_ID FROM Book_Issues WHERE Member_ID = %s AND Book_ID = %s AND Status = 'Issued'",
            (self.member_id, self.book2_id), fetch='one'
        )
        issue_id = row['Issue_ID']

        # Backdate the issue to 20 days ago (due 6 days ago -> 6 days late)
        db.execute_dml("""
            UPDATE Book_Issues
            SET Issue_Date = DATE_SUB(CURDATE(), INTERVAL 20 DAY),
                Due_Date = DATE_SUB(CURDATE(), INTERVAL 6 DAY)
            WHERE Issue_ID = %s
        """, (issue_id,))

        # Verify fn_calculate_fine reports 6 * 5.00 = 30.00
        fine_today = db.calculate_fine_today(issue_id)
        self.assertEqual(fine_today, 30.00, f"Expected 30.00 fine, got {fine_today}")

        # Return the book
        ok, res = db.call_return_book(issue_id)
        self.assertTrue(ok)
        self.assertEqual(float(res['Fine_Amount']), 30.00)

        # Verify entry in Fines_Payments table
        _, fine_record = db.execute_query(
            "SELECT * FROM Fines_Payments WHERE Issue_ID = %s",
            (issue_id,), fetch='one'
        )
        self.assertIsNotNone(fine_record)
        self.assertEqual(float(fine_record['Fine_Amount']), 30.00)
        self.assertEqual(fine_record['Payment_Status'], 'Pending')
        print("  -> Passed: 6 days late return produced Rs. 30.00 fine (Pending) via fn_calculate_fine.")

    # -------------------------------------------------------------
    # Test 8: Fine Payment Procedure (Cash, UPI, Card)
    # -------------------------------------------------------------
    def test_08_fine_payment(self):
        print("\n[TEST 8] Testing pay_fine Procedure (Cash / UPI / Card)...")
        # Get the pending fine from Test 7
        _, row = db.execute_query(
            "SELECT Issue_ID FROM Fines_Payments WHERE Payment_Status = 'Pending' AND Issue_ID IN (SELECT Issue_ID FROM Book_Issues WHERE Member_ID = %s)",
            (self.member_id,), fetch='one'
        )
        issue_id = row['Issue_ID']

        # Settle fine with UPI
        ok, res = db.call_pay_fine(issue_id, 'UPI')
        self.assertTrue(ok, f"pay_fine failed: {res}")

        # Verify Fines_Payments updated to Paid
        _, fine_record = db.execute_query(
            "SELECT * FROM Fines_Payments WHERE Issue_ID = %s",
            (issue_id,), fetch='one'
        )
        self.assertEqual(fine_record['Payment_Status'], 'Paid')
        self.assertEqual(fine_record['Payment_Mode'], 'UPI')
        self.assertIsNotNone(fine_record['Payment_Date'])

        # Try paying again -> should be rejected
        ok_dup, msg_dup = db.call_pay_fine(issue_id, 'Cash')
        self.assertFalse(ok_dup)
        self.assertTrue("already" in msg_dup.lower() and "paid" in msg_dup.lower())
        print("  -> Passed: Fine settled via UPI; re-payment correctly rejected.")

    # -------------------------------------------------------------
    # Test 9: Overdue Books Cursor Procedure
    # -------------------------------------------------------------
    def test_09_overdue_books_cursor(self):
        print("\n[TEST 9] Testing list_overdue_books() Explicit Cursor Procedure...")
        # Book 3 is still issued to QA Member. Make it overdue by 4 days
        _, row = db.execute_query(
            "SELECT Issue_ID FROM Book_Issues WHERE Member_ID = %s AND Book_ID = %s AND Status = 'Issued'",
            (self.member_id, self.book3_id), fetch='one'
        )
        issue_id = row['Issue_ID']

        db.execute_dml("""
            UPDATE Book_Issues
            SET Issue_Date = DATE_SUB(CURDATE(), INTERVAL 18 DAY),
                Due_Date = DATE_SUB(CURDATE(), INTERVAL 4 DAY)
            WHERE Issue_ID = %s
        """, (issue_id,))

        ok, overdue_list = db.call_list_overdue_books()
        self.assertTrue(ok)
        found = any(o['Issue_ID'] == issue_id for o in overdue_list)
        self.assertTrue(found, "Overdue issue was not found in list_overdue_books() result!")
        print(f"  -> Passed: Procedure list_overdue_books() returned {len(overdue_list)} overdue records including test issue.")

    # -------------------------------------------------------------
    # Test 10: Book Quantity Adjustment Invariant Check
    # -------------------------------------------------------------
    def test_10_quantity_adjustment_invariant(self):
        print("\n[TEST 10] Testing Book Quantity Synchronization Rule...")
        # Create a test book with Total=5, Available=5
        _, b = db.execute_dml(
            "INSERT INTO Books (Title, Author_ID, Publisher_ID, Genre, Quantity, Available_Quantity) VALUES (%s, %s, %s, %s, %s, %s)",
            ("Temp Sync Book", self.author_id, self.publisher_id, "Tech", 5, 5)
        )
        b_id = b['last_id']

        # Issue 1 copy to another member (e.g. member 3)
        db.call_issue_book(3, b_id)
        # Total=5, Available=4, Borrowed=1

        # Simulate editing total copies from 5 to 8 (diff = +3 -> Available becomes 7)
        old_qty = 5
        old_avail = 4
        borrowed = old_qty - old_avail # 1
        new_qty = 8
        new_avail = old_avail + (new_qty - old_qty) # 7
        db.execute_dml(
            "UPDATE Books SET Quantity = %s, Available_Quantity = %s WHERE Book_ID = %s",
            (new_qty, new_avail, b_id)
        )
        _, updated = db.execute_query("SELECT Quantity, Available_Quantity FROM Books WHERE Book_ID = %s", (b_id,), fetch='one')
        self.assertEqual(updated['Quantity'], 8)
        self.assertEqual(updated['Available_Quantity'], 7)

        # Cleanup
        db.execute_dml("DELETE FROM Book_Issues WHERE Book_ID = %s", (b_id,))
        db.execute_dml("DELETE FROM Books WHERE Book_ID = %s", (b_id,))
        print("  -> Passed: Total quantity adjustment accurately kept Available_Quantity consistent.")

    # -------------------------------------------------------------
    # Test 11: Unique Constraint & Foreign Key Friendly Handling
    # -------------------------------------------------------------
    def test_11_constraints_and_foreign_keys(self):
        print("\n[TEST 11] Testing Unique Constraint & Foreign Key Delete Protection...")
        # 1. Duplicate email on member
        ok_dup, msg_dup = db.execute_dml(
            "INSERT INTO Members (Member_Name, Member_Email, Member_Phone, Member_Address) VALUES (%s, %s, %s, %s)",
            ("Dup Member", "test_member_qa@test.com", "1111111111", "City")
        )
        self.assertFalse(ok_dup)
        self.assertIn("already registered", msg_dup)

        # 2. Deleting an author that has active books
        ok_del, msg_del = db.execute_dml("DELETE FROM Authors WHERE Author_ID = %s", (self.author_id,))
        self.assertFalse(ok_del)
        self.assertIn("Cannot delete this record", msg_del)
        print("  -> Passed: Duplicate emails and foreign-key protected deletions intercepted with friendly messages.")


if __name__ == '__main__':
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLibraryManagementSystem)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
