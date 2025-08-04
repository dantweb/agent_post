import unittest
from datetime import datetime

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_repository import MessageRepository
from src.message_service import MessageService
from src.message import Message


class TestMultiRecipientMessage(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with real components"""
        self.city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
        self.external_api = ExternalAPI("XXXXX")
        self.repository = MessageRepository()
        self.service = MessageService(self.city_api, self.external_api, self.repository)

        # Clean up any existing test messages before running the test
        self.clean_up_test_messages()

    def tearDown(self):
        """Clean up after test execution"""
        self.clean_up_test_messages()

    def clean_up_test_messages(self):
        """Remove any test messages from the repository"""
        messages = self.repository.find_all()
        for message in messages:
            if message.data == "Test multi-recipient message":
                self.repository.delete(message)

    def test_message_multiple_recipients(self):
        """
        Test that MessageService correctly processes messages for multiple recipients
        using the actual MessageService with real components
        """

        test_message = Message(
            id=234,
            created_at=datetime(2025, 8, 4, 6, 1, 30, 826055),
            from_address='test_sender',
            to_address='agent1, agent2',  # Multiple recipients
            data='Test multi-recipient message',
        )

        self.repository.save(test_message)

        self.service.process_messages()

        processed_messages = self.repository.find_all()
        test_messages = [msg for msg in processed_messages
                         if msg.data == "Test multi-recipient message"]

        self.assertGreaterEqual(len(test_messages), 1,
                                "No messages found in repository")

        found_recipient = False
        for msg in test_messages:
            if 'agent1' in msg.address_list or 'agent2' in msg.address_list:
                found_recipient = True
                break

        self.assertTrue(found_recipient,
                        "No messages found with individual recipients")

        # Check that all messages have the right data and sender
        for msg in test_messages:
            self.assertEqual(msg.data, "Test multi-recipient message")
            self.assertEqual(msg.from_address, "test_sender")
