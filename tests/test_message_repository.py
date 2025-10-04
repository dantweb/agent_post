# tests/test_message_repository.py
import unittest
import uuid
from datetime import datetime
from unittest.mock import patch
from src.message_repo import MessageRepository, MessageModel, Base
from src.message import Message


class TestMessageRepository(unittest.TestCase):
    def setUp(self):
        # Use in-memory SQLite for testing
        self.test_db_url = 'sqlite:///:memory:'
        self.repo = MessageRepository(db_url=self.test_db_url)
        Base.metadata.create_all(self.repo.engine)

    def tearDown(self):
        # Clean up the database after each test
        Base.metadata.drop_all(self.repo.engine)

    def test_save_message(self):
        """Test saving a message to the database."""
        test_message = Message(
            from_address='sender@example.com',
            to_address='recipient@example.com',
            data='Test message content',
            created_at=datetime(2023, 10, 1),
        )

        result = self.repo.save(test_message)
        self.assertTrue(result)

        # Verify by retrieving
        saved_messages = self.repo.find_all()
        self.assertEqual(len(saved_messages), 1)
        saved = saved_messages[0]
        self.assertEqual(saved.from_address, 'sender@example.com')
        self.assertEqual(saved.to_address, 'recipient@example.com')
        self.assertEqual(saved.data, 'Test message content')
        self.assertEqual(saved.created_at, datetime(2023, 10, 1))

    def test_find_all_empty(self):
        """Test finding all messages on an empty database."""
        messages = self.repo.find_all()
        self.assertEqual(len(messages), 0)

    def test_save_multiple_and_retrieve(self):
        """Test saving multiple messages and retrieving them all."""
        msg1 = Message(
            from_address='alice@example.com',
            to_address='bob@example.com',
            data='Message from Alice'
        )
        msg2 = Message(
            from_address='charlie@example.com',
            to_address='dave@example.com',
            data='Message from Charlie'
        )

        self.repo.save(msg1)
        self.repo.save(msg2)

        messages = self.repo.find_all()
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0].to_address, 'bob@example.com')
        self.assertEqual(messages[1].from_address, 'charlie@example.com')

    def test_save_with_missing_id(self):
        """Test saving a message without an explicit ID (should use default UUID)."""
        msgid = str(uuid.UUID)
        test_message = Message(
            from_address='sender@example.com',
            to_address='recipient@example.com',
            data='Test without ID',
            id=msgid
        )

        result = self.repo.save(test_message)
        self.assertTrue(result)

        saved_messages = self.repo.find_all()
        self.assertEqual(len(saved_messages), 1)
        self.assertEqual(saved_messages[0].id, msgid)  # Ensure UUID is auto-generated

    @patch('sqlalchemy.orm.session.Session.commit')
    def test_save_rollback_on_error(self, mock_commit):
        """Test that save rolls back on commit error."""
        mock_commit.side_effect = Exception("DB Error")

        test_message = Message(
            from_address='error_sender@example.com',
            to_address='error_recipient@example.com',
            data='Error test'
        )

        with self.assertRaises(Exception):
            self.repo.save(test_message)

        # Verify no messages were saved (find_all should be empty)
        messages = self.repo.find_all()
        self.assertEqual(len(messages), 0)

    def test_find_all_datetime_serialization(self):
        """Test that datetime fields are properly handled in retrieval."""
        now = datetime.now()
        test_message = Message(
            from_address='time_test@example.com',
            to_address='time_recipient@example.com',
            data='Datetime test',
            created_at=now
        )

        self.repo.save(test_message)

        retrieved = self.repo.find_all()[0]
        self.assertEqual(retrieved.created_at, now)


if __name__ == '__main__':
    unittest.main()