import unittest
import json
import time
from traceback import print_tb

import requests
import subprocess
import uuid
from datetime import datetime


class TestDirectPostToFilesystem(unittest.TestCase):
    """
    Test class for testing direct CURL requests to create files in an agent's filesystem
    """

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
        """Helper method to fetch agent's filesystem structure"""
        url = f"{self.filesystem_url}?agent_id={agent_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            self.fail(f"Failed to get agent filesystem: {response.text}")

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

    def test_direct_post_to_filesystem(self):
        """
        Test sending a direct CURL request to create a file in the filesystem
        and verify its existence using the agent filesystem API
        """
        try:
            # Step 1: Check initial state of recipient's inbox
            initial_filesystem = self.get_agent_filesystem(self.recipient_agent_id)
            initial_inbox_files = initial_filesystem.get("filesystem", {}).get("post", {}).get("inbox", {}).get("new",
                                                                                                                {})
            initial_file_count = len(initial_inbox_files)

            print(f"Initial inbox files count: {initial_file_count}")

            # Step 2: Create a unique message with timestamp and test ID
            timestamp = datetime.now().isoformat()
            message_id = int(time.time())
            unique_content = f"Test message {self.test_id} sent at {timestamp}"

            # Step 3: Prepare the message data according to filesystem_adapter requirements
            # This follows the format needed by the FilesystemAdapter.write() method
            payload = {
                "result": {
                    "result": {
                        "updated_files": [
                            {
                                "path": f"{message_id}.json",
                                "file_operation": "update",
                                "file_content": json.dumps({
                                    "message": {
                                        "from": self.sender_address,
                                        "to": self.recipient_address,
                                        "data": unique_content,
                                        "id": message_id,
                                        "created_at": timestamp
                                    }
                                })
                            }
                        ]
                    }
                }
            }

            # Step 4: Send the direct CURL request to the RECEIVE_POST endpoint
            print(f"Sending message with ID {message_id} directly to RECEIVE_POST endpoint...")

            # Convert the message data to a properly escaped JSON string for curl
            json_data = json.dumps(payload)

            # Execute the curl command
            curl_command = [
                'curl', '-X', 'POST',
                '-H', 'Content-Type: application/json',
                '-d', f'{json_data}',
                self.receive_post_url
            ]

            # Output the equivalent curl command that could be run manually
            curl_command_str = f"curl -X POST -H 'Content-Type: application/json' -d '{json_data}' {self.receive_post_url}"
            print("\nEquivalent curl command:")
            print(curl_command_str)
            print("\nExecuting command programmatically...")

            result = subprocess.run(curl_command, capture_output=True, text=True)

            # Check if the curl command was successful
            self.assertEqual(0, result.returncode, f"CURL command failed: {result.stderr}")

            # Step 5: Wait for file creation
            print("Waiting for file to be created...")
            max_attempts = 5
            file_found = False

            for attempt in range(1, max_attempts + 1):
                print(f"Checking for file (attempt {attempt}/{max_attempts})...")
                time.sleep(2)  # Wait for file processing

                # Look for the file by message ID
                filename, file_info = self.find_file_in_inbox(
                    self.recipient_agent_id,
                    message_id=message_id,
                    message_content=unique_content
                )

                if filename:
                    file_found = True
                    print(f"File found: {filename}")
                    break

            # Step 6: Verify the file was created
            self.assertTrue(file_found, f"Message file with ID {message_id} not found in recipient's inbox")

            # Step 7: Verify the file content
            try:
                file_content = json.loads(file_info.get("content", "{}"))
                message = file_content.get("message", {})

                # Verify message properties
                self.assertEqual(self.sender_address, message.get("from"),
                                 "Sender address doesn't match in the created file")
                self.assertEqual(self.recipient_address, message.get("to"),
                                 "Recipient address doesn't match in the created file")
                self.assertEqual(unique_content, message.get("data"),
                                 "Message content doesn't match in the created file")
                self.assertEqual(message_id, message.get("id"),
                                 "Message ID doesn't match in the created file")

                print("File content verification successful!")

            except (json.JSONDecodeError, TypeError) as e:
                self.fail(f"Error parsing file content: {str(e)}")

            # Step 8: Final verification - check total file count increased
            final_filesystem = self.get_agent_filesystem(self.recipient_agent_id)
            final_inbox_files = final_filesystem.get("filesystem", {}).get("post", {}).get("inbox", {}).get("new", {})
            final_file_count = len(final_inbox_files)

            self.assertGreater(final_file_count, initial_file_count,
                               "Total file count in inbox should have increased")

            print(f"Test completed successfully! Initial files: {initial_file_count}, Final files: {final_file_count}")

        except Exception as e:
            self.fail(f"Test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
