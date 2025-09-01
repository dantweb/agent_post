import json
from datetime import datetime

import requests
from typing import Dict, List
from requests import Response
from requests.exceptions import RequestException

from app import messages
from src.message import Message


class ExternalAPI:
    def __init__(self, token: str):
        self.token = token

    def collect_from_outbox(self, url: str) -> List[Message]:
        try:
            response: Response = requests.post(url)
            response.raise_for_status()
            file_entries = self._extract_file_entries(response.json())

            # Transform the file entries into Message objects
            messages = []
            for entry in file_entries:
                if 'file_content' in entry and 'message' in entry['file_content']:
                    msg_data = entry['file_content']['message']

                    # Create a Message object directly
                    message = Message(
                        id=msg_data.get('id', None),  # Use None if id is missing
                        created_at=msg_data.get('created_at', datetime.now()),  # Set current time as created_at
                        collected_at=datetime.now(),  # Set current time as collected_at
                        from_address=msg_data.get('from', ''),
                        to_address=msg_data.get('to', ''),
                        data=msg_data.get('data', '')
                    )
                    messages.append(message)

            return messages
        except (RequestException, json.JSONDecodeError) as e:
            raise Exception(f"Error collecting messages from {url}: {e}")

    def _extract_file_entries(self, data, results=None):
        """
        Recursively searches through a dictionary or list and collects all dictionaries
        that contain a 'file_content' key.

        Args:
            data: The dictionary or list to search through
            results: List to accumulate results (used in recursion)

        Returns:
            List of dictionaries containing 'file_content' and 'path' keys
        """
        if results is None:
            results = []

        if isinstance(data, dict):
            # Check if this dictionary has a 'file_content' key
            if 'file_content' in data:
                results.append(data)
            else:
                for value in data.values():
                    self._extract_file_entries(value, results)

        elif isinstance(data, list):
            # Recursively search through all items in this list
            for item in data:
                self._extract_file_entries(item, results)

        return results

    def add_to_inbox(self, url: str, message: dict) -> Response:
        print(f"Sending message to {url}...payload = {message}")
        response = requests.post(url, json=message)
        print(f"Response: {response.status_code} {response.text}")
        return response

    def serialize_message(self, obj):
        # Handle datetime conversion for JSON
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO 8601 string
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")  # Debugging edge cases
