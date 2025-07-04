import pytest
from src.city_api import CityAPI
from unittest.mock import patch
import requests
import unittest


class TestCityAPI(unittest.TestCase):
    @patch('requests.get')
    def test_city_api_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}
        city_api = CityAPI("test_url")
        data = city_api.get_cities()
        assert data == {"data": "test"}


    @patch('requests.get')
    def test_city_api_failure(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        city_api = CityAPI("test_url")
        with pytest.raises(Exception):
            city_api.get_cities()
