import unittest
from datetime import datetime
from unittest.mock import patch, Mock
from src.message import Message
from src.message_service import MessageService
from src.message_repository import MessageRepository
from src.city_api import CityAPI
from src.external_api import ExternalAPI


class TestMessageFlow(unittest.TestCase):

    def setUp(self):
        """Set up test dependencies with real CityAPI and mocked ExternalAPI"""
        # Use the specified initialization for CityAPI with real URL
        self.city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
        self.external_api = ExternalAPI("XXXXX")
        self.repository = MessageRepository()  # Uses in-memory DB

        # Create service with these components
        self.service = MessageService(
            city_api=self.city_api,
            external_api=self.external_api,
            message_repo=self.repository
        )

        # Clean up any existing test messages
        self.clean_up_test_messages()

    def clean_up_test_messages(self):
        """Remove any test messages from the repository"""
        messages = self.repository.find_all()
        for message in messages:
            self.repository.delete(message)

    def tearDown(self):
        """Clean up after test execution"""
        #self.clean_up_test_messages()

    def test_full_message_flow(self):
        """
        Test the full message flow through the system using real components
        - Fetches real city data from the API
        - Processes messages from outbox to inbox
        - Verifies message delivery and storage
        """
        # 1. First, create a test message and place it in the repository
        test_message = Message(
            id=12345,
            created_at=datetime.now(),
            from_address='FRBG/gustav',
            to_address='FRBG/cityhall, FRBG/walter',  # Multiple recipients
            data='Test full message flow',
            metadata={"test": True}
        )
        self.repository.save(test_message)

        initial_messages = self.repository.find_all()
        self.assertGreaterEqual(len(initial_messages), 1, "Test message was not saved to repository")

        self.service.process_messages()

        processed_messages = self.repository.find_all()

        test_messages = [msg for msg in processed_messages
                         if msg.data == 'Test full message flow']

        self.assertGreaterEqual(len(test_messages), 1,
                                "Expected at least one test message in repository after processing")

        for msg in test_messages:
            # Verify the sender and content remain consistent
            self.assertEqual(msg.from_address, 'FRBG/gustav')
            self.assertEqual(msg.data, 'Test full message flow')



if __name__ == '__main__':
    unittest.main()
