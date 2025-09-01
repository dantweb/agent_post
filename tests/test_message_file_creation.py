import unittest
import uuid
import time
from datetime import datetime
import requests
from flask import json

from src.message import Message


class TestMultiRecipientMessage(unittest.TestCase):
    def setUp(self):
        """Set up test environment with necessary URLs and agent IDs"""
        # Agent information
        self.sender_agent_id = "1"  # Sender agent ID (typically cityhall)
        self.recipient_agent_id = "2"  # Recipient agent ID

        # API endpoints
        self.base_url = "http://loopai_web:5000"
        self.filesystem_url = f"{self.base_url}/api/test/agentlife/fs/"
        self.receive_post_url = f"{self.base_url}/api/public/agent/{self.recipient_agent_id}/action/RECEIVE_POST/"

        # Agent addresses
        self.sender_address = "FRBG/cityhall"
        self.recipient_address = "FRBG/Agent_hwp2bg"

        # Generate a unique test identifier for this test run
        self.test_id = str(uuid.uuid4())[:8]

    def get_agent_filesystem(self, agent_id):
        """Retrieve the full filesystem structure of the specified agent using the real endpoint."""
        url = f"{self.filesystem_url}?agent_id={agent_id}"
        response = requests.get(url)
        response.raise_for_status()  # Ensure request was successful
        return response.json()

    def find_file_in_inbox(self, agent_id, message_id=None, message_content=None):
        """
        Search for a file in the agent's inbox by message ID or content
        Returns the file if found, otherwise None
        """
        filesystem = self.get_agent_filesystem(agent_id)
        inbox_files = filesystem.get("filesystem", {}).get("post", {}).get("inbox", {}).get("new", {})

        for filename, file_info in inbox_files.items():
            # If looking for a specific message ID
            if message_id and f"message{message_id}" in filename:
                return filename, file_info

            # If looking for specific content
            if message_content and file_info.get("content"):
                try:
                    content_json = json.loads(file_info.get("content", "{}"))
                    if message_content in json.dumps(content_json):
                        return filename, file_info
                except json.JSONDecodeError:
                    continue

        return None, None

    def send_message(self, message, message_id):
        """Send a message using the real API endpoint."""

        payload = {
            "result": {
                "result": {
                    "updated_files": [
                        {
                            "path": f"{message_id}.json",
                            "file_operation": "update",
                            "file_content": json.dumps({
                                "from": message.from_address,
                                "to": message.to_address,
                                "data": message.data,
                                "id": message.id,
                                "created_at": message.created_at
                            })
                        }
                    ]
                }
            }
        }

        print(f"\n\nSending message to {self.recipient_address} onto url {self.receive_post_url}...\n")
        response = requests.post(self.receive_post_url, json=payload)
        response.raise_for_status()  # Ensure the message was sent successfully

    def test_message_delivery_to_recipient(self):
        """Test message delivery and file creation for a single recipient using real endpoints."""
        # Prepare test message
        message = Message(
            from_address=self.sender_address,
            to_address=self.recipient_address,
            data=f"Test message with ID {self.test_id}",
            id=42
        )

        # Mock filesystem snapshot before sending the message
        before_filesystem = self.get_agent_filesystem(self.recipient_agent_id)
        before_files = before_filesystem.get("post", {}).get("inbox", {}).get("new", {})

        # Send the message
        message_id = uuid.uuid4()
        self.send_message(message, message_id)

        # Poll for new files in the inbox
        MAX_RETRIES = 3
        for attempt in range(MAX_RETRIES):
            new_file, file_info = self.find_file_in_inbox(self.recipient_agent_id, message_id, message_content=message.data)
            if new_file:
                break
            print(f"[DEBUG] Attempt {attempt + 1}/{MAX_RETRIES}: No new files yet. Retrying...\n")
            time.sleep(1.5)  # Increase retry delay to 1.5s for slow file creation


            print(f"\nNew file found: {new_file}")
            # Assert a new file was created in the recipient's inbox
            self.assertIsNotNone(new_file, f"No new files found for message ID {message.id}\n")

            content = file_info.get("content", "")
            self.assertIn(f'"id": {message.id}', content)
            self.assertIn(f'"data": "{message.data}"', content)

if __name__ == '__main__':
    unittest.main()
