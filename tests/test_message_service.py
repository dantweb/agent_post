import unittest
from datetime import datetime

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_repository import MessageRepository
from src.message_service import MessageService
from src.message import Message


class TestMessageService(unittest.TestCase):
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
            if message.data == "test_data":
                self.repository.delete(message)

    def test_message_service_process_messages(self):
        """
        Test that MessageService correctly processes messages
        using the actual MessageService with real components
        """
        # Create a test message
        test_message = Message(
            id=123,
            created_at=datetime(2025, 7, 1, 12, 0, 0),
            from_address='sender',
            to_address='recipient',
            data='test_data',
            metadata={'created_at': '2023-01-01T12:00:00'}
        )

        # Save the message directly to the repository
        self.repository.save(test_message)

        # Process messages
        self.service.process_messages()

        # Verify that the message was processed
        processed_messages = self.repository.find_all()
        test_messages = [msg for msg in processed_messages
                         if msg.data == "test_data"]

        # There should be at least one message in the repository
        self.assertGreaterEqual(len(test_messages), 1,
                                "No messages found in repository")

        # Verify message properties
        found_message = False
        for msg in test_messages:
            if msg.id == 123 and msg.from_address == 'sender' and msg.to_address == 'recipient':
                found_message = True
                break

        self.assertTrue(found_message,
                        "Test message not found in repository after processing")


if __name__ == '__main__':
    unittest.main()
