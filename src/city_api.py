import requests
from typing import Dict, List
from requests import Response
from requests.exceptions import RequestException

class CityAPI:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_cities(self) -> Dict:
        try:
            response: Response = requests.get(self.api_url)
            response.raise_for_status()
            return response.json()
        except RequestException as e:
            raise Exception(f"Error fetching cities data: {e}")
