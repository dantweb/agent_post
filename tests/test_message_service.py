import json
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, call

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService
from src.message import Message
from unittest.mock import ANY



class TestMessageService(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with mock components"""
        # Create mocks for external dependencies
        self.city_api = MagicMock(spec=CityAPI)
        self.external_api = MagicMock(spec=ExternalAPI)

        # Create the service with mocked dependencies
        self.service = MessageService(self.city_api, self.external_api)

        # Setup test data
        self.test_message = Message(
            from_address='test_sender',
            to_address='agent1, agent2',  # Multiple recipients in comma-separated format
            data='Test multi-recipient message',
            id=234,
            created_at=datetime(2025, 8, 4, 6, 1, 30, 826055),
        )

        # Setup mock responses
        self.addresses_dict = {
            'agent1': 'http://agent1/api/WAKEUP',
            'agent2': 'http://agent2/api/WAKEUP'
        }

        self.city_api.get_cities.return_value = {
            'addresses': [self.addresses_dict]
        }

        self.external_api.collect_from_outbox.return_value = [self.test_message]


def test_message_multiple_recipients(self):
    """
    Test that MessageService correctly processes messages for multiple recipients
    """
    # Call the method to process messages
    self.service.process_messages()

    # Ensure `collect_from_outbox` was called once per agent
    self.assertEqual(self.external_api.collect_from_outbox.call_count, 2)

    # Access the actual calls to `add_to_inbox`
    actual_calls = self.external_api.add_to_inbox.call_args_list

    # Verify the number of calls matches the expected number of recipients
    self.assertEqual(len(actual_calls), 2)

    # Iterate through the actual calls and validate their arguments
    for actual_call in actual_calls:
        recipient_url, payload = actual_call[0]  # Unpack `call` arguments

        # Verify the structure of the payload
        self.assertIn('updated_files', payload)
        self.assertEqual(len(payload['updated_files']), 1)

        updated_file = payload['updated_files'][0]
        self.assertIn('file_content', updated_file)
        self.assertIn('path', updated_file)

        # Convert file_content back to a dictionary and validate
        file_content = json.loads(updated_file['file_content'])
        self.assertEqual(file_content['id'], self.test_message.id)
        self.assertEqual(file_content['from_address'], self.test_message.from_address)
        self.assertEqual(file_content['to_address'], self.test_message.to_address)
        self.assertEqual(file_content['data'], self.test_message.data)
        self.assertIn('delivered_at', file_content)
        self.assertIsNotNone(file_content['delivered_at'])  # Ensure `delivered_at` is set

    # Ensure that the `delivered_at` timestamp is set on the message
    self.assertIsNotNone(self.test_message.delivered_at)
