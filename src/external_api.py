## ./agent_post/src/external_api/external_api.py
import json

import requests
from typing import Dict, List
from requests import Response
from requests.exceptions import RequestException


class ExternalAPI:
    def __init__(self, token: str):
        self.token = token

    def collect_from_outbox(self, url: str) -> List[Dict]:
        try:
            response: Response = requests.get(url)
            response.raise_for_status()
            messages = collect_file_contents(response.json())
            return messages  # Handle case where 'messages' key is missing
        except (RequestException, json.JSONDecodeError) as e:
            raise Exception(f"Error collecting messages from {url}: {e}")

    def add_to_inbox(self, url: str, message: Dict) -> None:
        try:
            response: Response = requests.post(url, json=message)
            response.raise_for_status()
        except RequestException as e:
            raise Exception(f"Error adding message to inbox: {e}")


def collect_file_contents(data, results=None):
    """
    Recursively parses through a dictionary or list and collects all 'file_content' values
    into a list.

    Args:
        data: The dictionary or list to search through
        results: List to accumulate results (used in recursion)

    Returns:
        List of all file_content values found in the data structure
    """
    if results is None:
        results = []

    if isinstance(data, dict):
        # Check if this dictionary has a 'file_content' key
        if 'file_content' in data:
            results.append(data['file_content'])

        # Recursively search through all values in this dictionary
        for value in data.values():
            collect_file_contents(value, results)

    elif isinstance(data, list):
        # Recursively search through all items in this list
        for item in data:
            collect_file_contents(item, results)

    return results
