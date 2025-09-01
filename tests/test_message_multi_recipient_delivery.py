import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, call
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
            to_address='FRBG/cityhall, FRBG/Agent_hwp2bg',  # Multiple recipients in comma-separated format
            data='Test multi-recipient message',
            id=234,  # Still providing an ID for testing purposes
            created_at=datetime(2025, 8, 4, 6, 1, 30, 826055),
        )

        # Setup mock responses
        self.addresses_dict = {
            'FRBG/Agent_hwp2bg': 'http://loopai_web:5000/api/public/agent/2/action/RECEIVE_POST/',
            'FRBG/cityhall': 'http://loopai_web:5000/api/public/agent/1/action/RECEIVE_POST/'
        }

        # Mock city_api to return our test addresses
        self.city_api.get_cities.return_value = {
            'addresses': [self.addresses_dict]
        }

        # Mock external_api to return our test message
        self.external_api.collect_from_outbox.return_value = [self.test_message]

    def test_message_multiple_recipients(self):
        """
        Test that MessageService correctly processes messages for multiple recipients.
        """
        # Update `to_address` to match keys in `self.addresses_dict`
        self.test_message.to_address = 'FRBG/cityhall, FRBG/Agent_hwp2bg'

        # Execute the method under test
        self.service.process_messages()

        # Verify that `collect_from_outbox` was called
        self.external_api.collect_from_outbox.assert_called()

        # Capture actual calls made to `add_to_inbox`
        actual_calls = self.external_api.add_to_inbox.call_args_list

        # Validate the number of calls to `add_to_inbox` (should equal the number of recipients)
        self.assertEqual(len(actual_calls), 4, f"Expected 4 calls, but got {len(actual_calls)}")

        # Iterate through each call and verify its content
        for call_args in actual_calls:
            # Extract arguments passed to `add_to_inbox`
            actual_url, actual_blob = call_args[0]
            print(f"[test_message_multiple_recipients] Actual URL: {actual_url}")
            # Validate the URL (it should match one of the expected recipient URLs)
            self.assertIn(actual_url, [
                'http://loopai_web:5000/api/public/agent/1/action/RECEIVE_POST/',
                'http://loopai_web:5000/api/public/agent/2/action/RECEIVE_POST/',
            ])

            # Validate the blob structure
            self.assertIn('updated_files', actual_blob)
            self.assertEqual(len(actual_blob['updated_files']), 1)

            # Extract the file path and file content from the blob
            actual_file_data = actual_blob['updated_files'][0]
            actual_path = actual_file_data['path']
            actual_content = actual_file_data['file_content']

            from datetime import date
            today = date.today().strftime("%Y-%m-%d")

            # Verify the file path starts with the expected prefix (dynamic timestamp handling)
            self.assertTrue(actual_path.startswith(f"./{today}"), f"Unexpected file path: {actual_path}")

            # Deserialize the JSON content (if necessary, depending on how it's tested)
            import json
            actual_content_data = json.loads(actual_content)

            # Verify the `delivered_at` field exists and is within the valid range
            self.assertIn('delivered_at', actual_content_data)
            delivered_timestamp = actual_content_data['delivered_at']
            self.assertIsNotNone(delivered_timestamp, "The `delivered_at` field should not be None")

            # Verify the remainder of the file content matches the expected message
            expected_content_data = self.test_message.to_dict()
            expected_content_data['delivered_at'] = delivered_timestamp  # Update with dynamic value
            self.assertDictEqual(actual_content_data, expected_content_data, "Message content does not match")

        # Ensure all recipients' URLs were processed
        expected_urls = [
            'http://loopai_web:5000/api/public/agent/1/action/RECEIVE_POST/',
            'http://loopai_web:5000/api/public/agent/2/action/RECEIVE_POST/',
        ]
        actual_urls = [call_args[0][0] for call_args in actual_calls]
        self.assertCountEqual(expected_urls, actual_urls)

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

if __name__ == '__main__':
    unittest.main()
