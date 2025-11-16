import unittest

from src.external_api import ExternalAPI
from unittest.mock import patch, Mock
import requests


class TestExternalAPI(unittest.TestCase):


    def test_external_api_collect_success(self):
        # Patch both 'requests.post' and 'requests.get' to mock the full API flow
        with patch('requests.post') as mock_post, patch('requests.get') as mock_get:
            # Mock POST response (triggers action execution)
            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.json.return_value = {"execution_id": "test-exec-123"}
            mock_post.return_value = mock_post_response

            # Mock GET response (retrieves execution result)
            mock_get_response = Mock()
            mock_get_response.status_code = 200
            # Mock response that matches the actual WAKEUP format
            mock_get_response.json.return_value = {
                "data": {
                    "session_id": "test-session-123",
                    "broadcast_data": [
                        {
                            "step_id": "wakeup_and_give_posts_to_agent",
                            "result": [
                                {
                                    "method": "POST",
                                    "path": "/api/public/agent/6/action/WAKEUP/",
                                    "url": "http://loopai_web:5000/api/public/agent/6/action/WAKEUP/"
                                },
                                {
                                    "updated_files": [
                                        {
                                            "file_content": {"message": {"data": "test_data", "from": "sender", "to": "recipient"}},
                                            "path": "message1.json"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "execution_id": "test-exec-123",
                "status": "completed",
                "success": True
            }
            mock_get.return_value = mock_get_response

            # Instantiate the ExternalAPI class
            api = ExternalAPI("XXX-X-XXX-XXX")

            # Call the method we're testing
            messages = api.collect_from_outbox("http://loopai_web:5000/api/public/agent/6/action/WAKEUP/")
            # Assertions
            self.assertEqual(len(messages), 1)  # Expecting one message
            self.assertEqual(messages[0].from_address, "sender")  # Validate message sender (corrected)
            self.assertEqual(messages[0].to_address, "recipient")  # Validate message recipient (corrected)
            self.assertTrue(isinstance(messages[0].data, str) and len(messages[0].data)>0)  # Validate message content

    def test_external_api_collect_failure(self):
        # Simulate a network exception
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            external_api = ExternalAPI("test_token")
            with self.assertRaises(Exception):
                external_api.collect_from_outbox("test_url")


    def test_external_api_add_success(self):
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            external_api = ExternalAPI("test_token")
            external_api.add_to_inbox("test_url", {"data": "test"})
            mock_post.assert_called()


    def test_external_api_add_failure(self):
        with patch('requests.post') as mock_post:
            mock_post.side_effect = requests.exceptions.RequestException("Network error")
            external_api = ExternalAPI("test_token")
            with self.assertRaises(Exception):
                external_api.add_to_inbox("test_url", {"data": "test"})

    def test_extract_message_with_body_field(self):
        """
        RED: Test extraction when message uses 'body' instead of 'data'
        This test will FAIL initially because _extract_message_data doesn't handle this format
        """
        api = ExternalAPI("token")

        # Actual format discovered from cityhall's outbox
        file_entry = {
            "path": "sprint3_day1_test.json",
            "file_content": {
                "from": "cityhall",
                "to": "padre",
                "body": "Sprint 3 Day 1 test - understanding message format",
                "subject": "Sprint 3 Test",
                "timestamp": "2025-11-16T17:00:00Z",
                "priority": "high"
            }
        }

        # This will FAIL - method doesn't exist yet or returns None
        msg_data = api._extract_message_data(file_entry)

        # Assertions that will FAIL initially
        self.assertIsNotNone(msg_data, "Extraction should not return None")
        self.assertEqual(msg_data['from_address'], 'cityhall')
        self.assertEqual(msg_data['to_address'], 'padre')
        self.assertEqual(msg_data['data'], 'Sprint 3 Day 1 test - understanding message format')  # Maps 'body' to 'data'

if __name__ == '__main__':
    unittest.main()
