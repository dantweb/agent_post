import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService
from src.message import Message


class TestMultiRecipientMessage(unittest.TestCase):
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
            id=234,  # Still providing an ID for testing purposes
            created_at=datetime(2025, 8, 4, 6, 1, 30, 826055),
        )

        # Setup mock responses
        self.addresses_dict = {
            'agent2': 'http://agent2/api/WAKEUP',
            'agent1': 'http://agent1/api/WAKEUP'
        }

        # Mock city_api to return our test addresses
        self.city_api.get_cities.return_value = {
            'addresses': [self.addresses_dict]
        }

        # Mock external_api to return our test message
        self.external_api.collect_from_outbox.return_value = [self.test_message]

    def test_message_multiple_recipients(self):
        """
        Test that MessageService correctly processes messages for multiple recipients
        """
        # Execute the method under test
        self.service.process_messages()

        # Verify that collect_from_outbox was called for each agent address
        self.external_api.collect_from_outbox.assert_called()

        # Verify that add_to_inbox was called for each recipient
        expected_calls = 2  # One for each recipient (agent1, agent2)
        actual_calls = self.external_api.add_to_inbox.call_count
        self.assertEqual(expected_calls, actual_calls,
                         f"Expected {expected_calls} calls to add_to_inbox, but got {actual_calls}")

        # Verify the URLs were correctly transformed from WAKEUP to RECEIVE_POST
        for i, recipient in enumerate(['agent1', 'agent2']):
            # Get the args from the i-th call to add_to_inbox
            call_args = self.external_api.add_to_inbox.call_args_list[i][0]
            print(
                f"add_to_inbox call {i} args: {call_args}")

            # First arg should be the URL with WAKEUP replaced by RECEIVE_POST
            expected_url = self.addresses_dict[recipient].replace('WAKEUP', 'RECEIVE_POST')
            actual_url = call_args[0]
            print(f"add_to_inbox call {i} URL: {actual_url}")

            self.assertEqual(expected_url, actual_url,
                    f"Expected URL {expected_url} for {recipient}, but got {actual_url}")

            # Second arg should be the message
            message_arg = call_args[1]
            self.assertEqual(self.test_message.data, message_arg.data)
            self.assertEqual(self.test_message.from_address, message_arg.from_address)

    def test_get_agent_addresses(self):
        """Test that addresses are correctly extracted from cities data"""
        cities_data = {
            'addresses': [
                {'agent1': 'http://agent1/api/WAKEUP'},
                {'agent2': 'http://agent2/api/WAKEUP'}
            ]
        }

        result = self.service.get_agent_addresses(cities_data)

        expected = {
            'agent1': 'http://agent1/api/WAKEUP',
            'agent2': 'http://agent2/api/WAKEUP'
        }

        self.assertEqual(expected, result)
