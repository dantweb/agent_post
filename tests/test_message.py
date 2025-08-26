import unittest
from datetime import datetime

from src.message import Message


class TestMessage(unittest.TestCase):
    def test_message_creation(self):
        """Test basic message creation and properties"""
        message = Message(
            id=123,
            from_address='sender@example.com',
            to_address='recipient@example.com',
            data='Test message content'
        )

        self.assertEqual(123, message.id)
        self.assertEqual('sender@example.com', message.from_address)
        self.assertEqual('recipient@example.com', message.to_address)
        self.assertEqual('Test message content', message.data)
        self.assertIsNotNone(message.created_at)
        self.assertIsNone(message.collected_at)
        self.assertIsNone(message.delivered_at)

    def test_address_list_single(self):
        """Test address_list property with a single recipient"""
        message = Message(
            from_address='sender@example.com',
            to_address='recipient@example.com',
            data='Test message'
        )

        self.assertEqual(['recipient@example.com'], message.address_list)

    def test_address_list_multiple_comma(self):
        """Test address_list property with comma-separated recipients"""
        message = Message(
            from_address='sender@example.com',
            to_address='recipient1@example.com, recipient2@example.com',
            data='Test message'
        )

        self.assertEqual(['recipient1@example.com', 'recipient2@example.com'],
                         message.address_list)

    def test_address_list_multiple_semicolon(self):
        """Test address_list property with semicolon-separated recipients"""
        message = Message(
            from_address='sender@example.com',
            to_address='recipient1@example.com; recipient2@example.com',
            data='Test message'
        )

        self.assertEqual(['recipient1@example.com', 'recipient2@example.com'],
                         message.address_list)

    def test_to_dict(self):
        """Test conversion to dictionary"""
        created_time = datetime(2025, 1, 1, 12, 0, 0)
        message = Message(
            id=456,
            from_address='sender@example.com',
            to_address='recipient@example.com',
            data='Test dictionary conversion',
            created_at=created_time
        )

        result = message.to_dict()

        self.assertEqual(456, result['id'])
        self.assertEqual('sender@example.com', result['from_address'])
        self.assertEqual('recipient@example.com', result['to_address'])
        self.assertEqual('Test dictionary conversion', result['data'])
        self.assertEqual(created_time.isoformat(), result['created_at'])
