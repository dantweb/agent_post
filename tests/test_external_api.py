import unittest
import pytest
from src.external_api import ExternalAPI
from unittest.mock import patch
import requests


class TestExternalAPI(unittest.TestCase):

    @patch('requests.get')
    def test_external_api_collect_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"messages": [{"data": "test"}]}
        external_api = ExternalAPI("test_token")
        messages = external_api.collect_from_outbox("test_url")
        assert len(messages) == 1
        assert messages[0]['data'] == "test"


    @patch('requests.get')
    def test_external_api_collect_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        external_api = ExternalAPI("test_token")
        with pytest.raises(Exception):
            external_api.collect_from_outbox("test_url")


    @patch('requests.post')
    def test_external_api_add_success(self, mock_post):
        mock_post.return_value.status_code = 200
        external_api = ExternalAPI("test_token")
        external_api.add_to_inbox("test_url", {"data": "test"})
        mock_post.assert_called()


    @patch('requests.post')
    def test_external_api_add_failure(self, mock_post):
        mock_post.side_effect = requests.exceptions.RequestException("Network error")
        external_api = ExternalAPI("test_token")
        with pytest.raises(Exception):
            external_api.add_to_inbox("test_url", {"data": "test"})
