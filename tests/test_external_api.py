import unittest

import pytest
from src.external_api import ExternalAPI
from unittest.mock import patch, Mock
import requests


class TestExternalAPI(unittest.TestCase):


    def test_external_api_collect_success(self):
        # Patch 'requests.get' to mock the GET API call
        with patch('requests.get') as mock_get:
            # Mock response setup
            mock_response = Mock()
            mock_response.status_code = 200
            # Mock response that matches the format from the curl output
            mock_response.json.return_value = {
                "data": [
                    {"result": {"updated_files": []}, "session_id": "", "step_id": ""},
                    {"result": {"updated_files": []}, "session_id": "", "step_id": ""},
                    [
                        {"args": {}, "method": "GET", "path": "/api/public/agent/6/action/WAKEUP/",
                         "query_params": {}, "remote_addr": "172.19.0.5",
                         "url": "http://loopai_web:5000/api/public/agent/6/action/WAKEUP/"},
                        {"result": []}
                    ],
                    [
                        {"args": {}, "method": "GET", "path": "/api/public/agent/6/action/WAKEUP/",
                         "query_params": {}, "remote_addr": "172.19.0.5",
                         "url": "http://loopai_web:5000/api/public/agent/6/action/WAKEUP/"},
                        {"result": [
                            {"file_content": {"message": {"data": "test_data", "from": "sender", "to": "recipient"}},
                             "path": "message1.json"}
                        ]}
                    ]
                ],
                "message": "Action executed successfully",
                "success": True
            }
            mock_get.return_value = mock_response

            # Instantiate the ExternalAPI class
            api = ExternalAPI("XXXXX")

            # Call the method we're testing
            messages = api.collect_from_outbox("http://loopai_web:5000/api/public/agent/6/action/WAKEUP/")

            # Assertions
            self.assertEqual(len(messages), 1)  # Expecting one message
            self.assertEqual(messages[0].from_address, "sender")  # Validate message sender
            self.assertEqual(messages[0].to_address, "recipient")  # Validate message recipient
            self.assertEqual(messages[0].data, "test_data")  # Validate message content

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
            with pytest.raises(Exception):
                external_api.add_to_inbox("test_url", {"data": "test"})

if __name__ == '__main__':
    unittest.main()
