## ./agent_post/src/external_api/external_api.py

import requests
from typing import Dict, List
from requests import Response
from requests.exceptions import RequestException


class ExternalAPI:
    def __init__(self, token: str):
        self.token = token

    def collect_from_outbox(self, url: str) -> List[Dict]:
        try:
            collect_url = f"{url}?token={self.token}&action=collect_from_outbox"
            response: Response = requests.get(collect_url)
            response.raise_for_status()
            return response.json().get('messages', [])  # Handle case where 'messages' key is missing
        except (RequestException, json.JSONDecodeError) as e:
            raise Exception(f"Error collecting messages from {url}: {e}")

    def add_to_inbox(self, url: str, message: Dict) -> None:
        try:
            add_url = f"{url}?token={self.token}&action=add_to_inbox"
            response: Response = requests.post(add_url, json=message)
            response.raise_for_status()
        except RequestException as e:
            raise Exception(f"Error adding message to inbox: {e}")
