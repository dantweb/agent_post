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
                    msg_data = None
                    if isinstance(bc_entry['file_content'], str):
                        file_content_bc_dict = BroadcastData(json.loads(bc_entry['file_content']))
                        msg_data = file_content_bc_dict['message']

                    if isinstance(bc_entry['file_content'], dict):
                        if 'message' in bc_entry['file_content'] and 'message' in bc_entry['file_content']:
                            msg_data = bc_entry['file_content']['message']
                        if 'data' in bc_entry['file_content'] and 'to' in bc_entry['file_content']:
                            msg_data = bc_entry

                    if ('to' in bc_entry or 'to_address' in bc_entry) and 'data' in bc_entry:
                        msg_data = bc_entry

                    print(f"\n\nmsg_data = {msg_data}\n\n")

                    if msg_data is not None:
                        message = Message(
                            id=msg_data.get('id', md5_hex(str(msg_data))),  # Use None if id is missing
                            created_at=msg_data.get('created_at', datetime.now()),  # Set current time as created_at
                            from_address=msg_data.get('from_address', msg_data.get('from', '<no sender address>')),
                            to_address=msg_data.get('to_address', msg_data.get('to', '<no recipient address>')),
                            data=msg_data.get('data', '[[-the message has no data at collection-]]')
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
