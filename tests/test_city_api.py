import pytest
from src.city_api import CityAPI
from unittest.mock import patch, Mock
import requests
import unittest


class TestCityAPI(unittest.TestCase):

    def test_city_api_success(self):
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            # Update this to match the real API response format from your curl command
            mock_response.json.return_value = {
                "data": {
                    "success": True,
                    "addresses": [
                        {
                            "FRBG/walter": "http://loopai_web:5000/api/public/agent/6/action/WAKEUP/"
                        }
                    ]
                }
            }

            mock_get.return_value = mock_response

            api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
            data = api.get_cities()

            # Update the assertion to match what you expect
            self.assertIn("addresses", data)
            self.assertEqual(True, data["success"])



    def test_city_api_failure(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Network error")
            city_api = CityAPI("test_url")
            with pytest.raises(Exception):
                city_api.get_cities()
