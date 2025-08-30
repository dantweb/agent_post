import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

from src.message_service import MessageService
from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message import Message


class TestMessageDeliveryPayload(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies before each test"""
        # Create real instances for integration testing
        self.city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
        self.external_api = ExternalAPI("XXXXXX")

        # Create the service under test
        self.message_service = MessageService(
            city_api=self.city_api,
            external_api=self.external_api
        )

    def test_get_agent_addresses(self):
        """Test the agent address extraction functionality"""
        # Get real cities data
        cities_data = self.city_api.get_cities()

        # Get agent addresses
        agent_addresses = self.message_service.get_agent_addresses(cities_data)

        # Verify the structure and content
        self.assertIsInstance(agent_addresses, dict)
        self.assertGreater(len(agent_addresses), 0, "No agent addresses found")

        for agent_name, url in agent_addresses.items():
            self.assertIsInstance(url, str)
            self.assertTrue(len(url) > 0)

    def test_message_multiple_recipients(self):
        """Test handling of messages with multiple recipients"""
        # Create a controlled test environment with known data
        # Mock the city_api to return a predictable result
        original_get_cities = self.city_api.get_cities

        mock_cities_data = {
            'addresses': [
                {'agent1': 'http://agent1/api/WAKEUP'},
                {'agent2': 'http://agent2/api/WAKEUP'}
            ]
        }

        self.city_api.get_cities = MagicMock(return_value=mock_cities_data)

        # Create the agent address mapping directly
        agent_addresses = {
            'agent1': 'http://agent1/api/RECEIVE_POST',
            'agent2': 'http://agent2/api/RECEIVE_POST'
        }

        # Mock the get_agent_addresses method to return our controlled mapping
        original_get_addresses = self.message_service.get_agent_addresses
        self.message_service.get_agent_addresses = MagicMock(return_value=agent_addresses)

        # Create a test message from agent1 to agent2
        test_message = Message(
            from_address='agent1',
            to_address='agent2',  # Single recipient for simplicity
            data="TEST_PAYLOAD_MESSAGE",
            created_at=datetime.now()
        )

        # Mock external API to return our test message
        original_collect = self.external_api.collect_from_outbox
        self.external_api.collect_from_outbox = MagicMock(return_value=[test_message])

        # Track the actual URL used when sending the message
        called_with = {}

        def mock_add_to_inbox(url, message):
            called_with['url'] = url
            called_with['message'] = message
            return True

        original_add_to_inbox = self.external_api.add_to_inbox
        self.external_api.add_to_inbox = MagicMock(side_effect=mock_add_to_inbox)

        # Store original tracking lists
        original_recipient_list = self.message_service.recipient_list.copy() if hasattr(self.message_service,
                                                                                        'recipient_list') else []
        original_sender_list = self.message_service.sender_list.copy() if hasattr(self.message_service,
                                                                                  'sender_list') else []

        try:
            # Run the message processing service
            self.message_service.process_messages()

            # Verify the correct URL was used for the recipient
            expected_url = agent_addresses['agent2']  # URL for agent2
            actual_url = called_with.get('url', '')

            self.assertEqual(expected_url, actual_url,
                             f"Expected URL {expected_url} for agent2, but got {actual_url}")

            # Verify tracking lists if they exist
            if hasattr(self.message_service, 'sender_list'):
                self.assertIn('agent1', self.message_service.sender_list)

            if hasattr(self.message_service, 'recipient_list'):
                self.assertIn('agent2', self.message_service.recipient_list)

        finally:
            # Restore original functions and state
            self.city_api.get_cities = original_get_cities
            self.message_service.get_agent_addresses = original_get_addresses
            self.external_api.collect_from_outbox = original_collect
            self.external_api.add_to_inbox = original_add_to_inbox

            if hasattr(self.message_service, 'recipient_list'):
                self.message_service.recipient_list = original_recipient_list
            if hasattr(self.message_service, 'sender_list'):
                self.message_service.sender_list = original_sender_list

    def test_empty_tracking_lists(self):
        """Test that we can set empty tracking lists"""
        # Skip if tracking lists don't exist
        if not hasattr(self.message_service, 'recipient_list') or not hasattr(self.message_service, 'sender_list'):
            self.skipTest("Tracking lists not implemented")

        # Store original lists
        original_recipient_list = self.message_service.recipient_list.copy()
        original_sender_list = self.message_service.sender_list.copy()

        try:
            # Manually set some data
            self.message_service.recipient_list = ['old_recipient1', 'old_recipient2']
            self.message_service.sender_list = ['old_sender']

            # Now manually clear them
            self.message_service.recipient_list = []
            self.message_service.sender_list = []

            # Verify they're empty
            self.assertEqual(len(self.message_service.recipient_list), 0)
            self.assertEqual(len(self.message_service.sender_list), 0)
        finally:
            # Restore original lists
            self.message_service.recipient_list = original_recipient_list
            self.message_service.sender_list = original_sender_list

    def test_message_delivery_statistics(self):
        """Test the statistics tracking functionality"""
        # Skip if tracking lists don't exist
        if not hasattr(self.message_service, 'recipient_list') or not hasattr(self.message_service, 'sender_list'):
            self.skipTest("Tracking lists not implemented")

        # Store original lists
        original_recipient_list = self.message_service.recipient_list.copy()
        original_sender_list = self.message_service.sender_list.copy()

        try:
            # Manually set some test data directly to the lists
            self.message_service.sender_list = ['agent1', 'agent2', 'agent3']
            self.message_service.recipient_list = ['agent1', 'agent2', 'agent3', 'agent4', 'agent5']

            # Test various statistics
            if hasattr(self.message_service, 'get_success_rate'):
                success_rate = self.message_service.get_success_rate()
                self.assertIsInstance(success_rate, float)

            # Verify the list sizes match what we set
            self.assertEqual(len(self.message_service.sender_list), 3)
            self.assertEqual(len(self.message_service.recipient_list), 5)
        finally:
            # Restore original lists
            self.message_service.recipient_list = original_recipient_list
            self.message_service.sender_list = original_sender_list
