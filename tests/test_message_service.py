import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, call

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService
from src.message import Message


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
        # Execute the method under test
        self.service.process_messages()

        # Verify that collect_from_outbox was called for each agent address
        self.assertEqual(self.external_api.collect_from_outbox.call_count, 2)

        # Create expected call list to verify correct order and parameters
        expected_calls = [
            call('http://agent2/api/RECEIVE_POST', self.test_message),
            call('http://agent1/api/RECEIVE_POST', self.test_message)
        ]

        # Verify add_to_inbox was called with the correct parameters
        self.external_api.add_to_inbox.assert_has_calls(expected_calls, any_order=True)

        # Verify the delivered_at timestamp was updated
        self.assertIsNotNone(self.test_message.delivered_at)

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
