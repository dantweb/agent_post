import json


from datetime import datetime

import requests
from typing import Dict, List
from requests import Response
from requests.exceptions import RequestException
from sqlalchemy.util import md5_hex

from src.broadcast_data import BroadcastData
from src.message import Message


class ExternalAPI:
    def __init__(self, token: str):
        self.token = token

    def _extract_message_data(self, file_entry: Dict) -> Dict:
        """
        Extract message data from file_content structure with flexible field aliasing.

        Handles multiple field name variations since LLM-generated messages use inconsistent naming:
        - from/from_address/from_agent/sender/sender_address
        - to/to_address/to_agent/recipient/recipient_address/address_to
        - body/data/message_body/message_data/content/message
        - timestamp/created_at/time/date
        - message_id/id/msg_id

        Args:
            file_entry: Dictionary containing 'file_content' and 'path' keys

        Returns:
            Dictionary with standardized field names or None if required fields missing
        """
        file_content = file_entry.get('file_content')
        if not file_content:
            return None

        # Handle JSON string in file_content
        if isinstance(file_content, str):
            try:
                file_content = json.loads(file_content)
            except json.JSONDecodeError:
                print(f"ERROR: Invalid JSON string in file_content")
                return None

        # Check for nested 'message' key (common pattern)
        if isinstance(file_content, dict) and 'message' in file_content:
            msg_data = file_content['message']
        else:
            msg_data = file_content

        # Field aliases for flexible extraction
        from_aliases = ['from', 'from_address', 'from_agent', 'sender', 'sender_address']
        to_aliases = ['to', 'to_address', 'to_agent', 'recipient', 'recipient_address', 'address_to']
        data_aliases = ['data', 'body', 'message_body', 'message_data', 'content', 'message']
        timestamp_aliases = ['timestamp', 'created_at', 'time', 'date']
        id_aliases = ['id', 'message_id', 'msg_id']

        # Extract fields using aliases
        extracted = {}

        # Find 'from' field
        for alias in from_aliases:
            if alias in msg_data and msg_data[alias]:
                extracted['from_address'] = msg_data[alias]
                break

        # Find 'to' field
        for alias in to_aliases:
            if alias in msg_data and msg_data[alias]:
                extracted['to_address'] = msg_data[alias]
                break

        # Find 'data' field
        for alias in data_aliases:
            if alias in msg_data:
                extracted['data'] = msg_data[alias]
                break

        # Find 'timestamp' field (optional)
        for alias in timestamp_aliases:
            if alias in msg_data and msg_data[alias]:
                extracted['timestamp'] = msg_data[alias]
                break

        # Find 'id' field (optional)
        for alias in id_aliases:
            if alias in msg_data and msg_data[alias]:
                extracted['id'] = msg_data[alias]
                break

        # Validate required fields
        if 'from_address' not in extracted or 'to_address' not in extracted:
            print(f"ERROR: Missing required fields. from_address: {extracted.get('from_address')}, to_address: {extracted.get('to_address')}")
            return None

        print(f"SUCCESS: Extracted message from {extracted['from_address']} to {extracted['to_address']}")
        return extracted

    def collect_from_outbox(self, url: str) -> List[Message]:
        try:
            response: Response = requests.post(url)
            response.raise_for_status()
            execution_id = response.json().get('execution_id')
            if not execution_id:
                return []

            execution_url = self.get_execution_url(url, execution_id)

            while True:
                execution_response = requests.get(execution_url)
                execution_response.raise_for_status()
                raw_json = execution_response.json()
                raw_bc = BroadcastData(raw_json)
                print(f"raw_bc = {raw_bc}")
                normal_json = raw_bc
                if 'execution' in normal_json and normal_json['execution']['status'] == 'running':
                    from time import sleep
                    print(f"Execution is still running, waiting 10 seconds...")
                    sleep(3)
                else:
                    break

            bc = raw_bc
            file_entries = bc.find_value_recursive_by_key('updated_files')

            if file_entries != [[]] and "path" in file_entries[0][0]:
                print(f"Found {len(file_entries)} updated files in outbox")
                print(f"\n\n {(file_entries)} \n\n")
                file_entries = file_entries[0]

            messages = []
            if len(file_entries) > 0 and file_entries != [[]]:
                for entry in file_entries:
                    bc_entry = BroadcastData(entry)
                    print(f"\n\nProcessing file entry: {bc_entry}\n\n")
                    print(f"\nentry internals are accessible with indices : {type(bc_entry['file_content'])}" )

                    # Use new _extract_message_data method with field aliasing
                    msg_data = self._extract_message_data(dict(bc_entry))

                    if msg_data is not None:
                        message = Message(
                            id=msg_data.get('id', md5_hex(str(msg_data))),
                            created_at=msg_data.get('timestamp', msg_data.get('created_at', datetime.now())),
                            from_address=msg_data.get('from_address'),
                            to_address=msg_data.get('to_address'),
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

        print(f"Extracting file entries from data type {type(data)} data = {data}")

        if results is None:
            results = []

        if isinstance(data, dict):
            # Check if this dictionary has a 'file_content' key
            if 'file_content' in data and 'path' in data:
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

    def get_execution_url(self, url, execution_id):
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        host = urlunparse((parsed.scheme, parsed.netloc, '', '', '', ''))
        return f"{host}/api/public/execution/{execution_id}/result/"
