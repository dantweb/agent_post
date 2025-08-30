import unittest
import json
import time
import requests
from datetime import datetime

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService
from src.message import Message


class TestMessageFileCreation(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with real components"""
        # Create actual API instances - no mocks
        self.city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
        self.external_api = ExternalAPI("XXXXX")

        # Create the service with real dependencies
        self.service = MessageService(self.city_api, self.external_api)

        # Set real agent IDs for testing
        # Using consistent IDs that should exist in the test environment
        self.sender_agent_id = "1"  # Sender agent ID (cityhall)
        self.recipient_agent_id = "2"  # Recipient agent ID

        # For real API testing, we'll use consistent addresses
        self.sender_address = "FRBG/cityhall"
        self.recipient_address = "FRBG/Agent_hwp2bg"

        # URL for checking agent filesystem
        self.filesystem_url = "http://loopai_web:5000/api/test/agentlife/fs/"

        # Base URL for agent API calls
        self.agent_api_base_url = "http://loopai_web:5000/api"

    def get_agent_filesystem(self, agent_id):
        """Helper method to fetch agent's filesystem structure"""
        url = f"{self.filesystem_url}?agent_id={agent_id}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            self.fail(f"Failed to get agent filesystem: {response.text}")

    def count_inbox_files(self, agent_id):
        """Helper method to count files in agent's inbox/new folder"""
        filesystem = self.get_agent_filesystem(agent_id)
        inbox_files = filesystem.get("filesystem", {}).get("post", {}).get("inbox", {}).get("new", {})
        return len(inbox_files), inbox_files

    def send_message(self, from_address, to_address, message_data):
        """Helper method to send a real message using the API"""
        message_payload = {"result": {
            "updated_files":
                [{"path": "message999.json",
                  "file_content": json.dumps({
                      "message": {
                          "from": from_address,
                          "to": to_address,
                          "data": message_data
                        }
                    })
                  }
                ]
            }
        }

        print("\n\nSending payload  " + str(message_payload) + "\n\n...")

        # Use the proper endpoint for message delivery
        send_url = f"{self.agent_api_base_url}/public/agent/{self.sender_agent_id}/action/RECEIVE_POST/"
        print(f"Sending message to {to_address} via {send_url}")
        response = requests.post(send_url, json=message_payload)

        if response.status_code != 200:
            self.fail(f"Failed to send message: {response.text}")

        return response

    def test_end_to_end_message_delivery_and_file_creation(self):
        """
        End-to-end test that sends a real message and verifies file creation
        in the recipient's inbox using the real API
        """
        try:
            file_count_before, inbox_files_before = self.count_inbox_files(self.recipient_agent_id)

            print(f"Before test: Recipient has {file_count_before} files in inbox/new")

            timestamp = datetime.now().isoformat()
            message_content = f"Test message sent at {timestamp} for file creation verification"

            print(f"Sending message from {self.sender_address} to {self.recipient_address}")
            self.send_message(self.sender_address, self.recipient_address, message_content)

            print("Waiting for message processing...")

            max_attempts = 5
            for attempt in range(1, max_attempts + 1):
                print(f"Checking for message (attempt {attempt}/{max_attempts})...")
                time.sleep(attempt * 2)

                file_count_after, inbox_files_after = self.count_inbox_files(self.recipient_agent_id)

                if file_count_after > file_count_before:
                    print(f"New files detected! Count before: {file_count_before}, count after: {file_count_after}")
                    break

                if attempt == max_attempts:
                    self.fail(f"No new files found after {max_attempts} attempts with increasing wait times")

                # Step 5: Verify that a new file was created
                self.assertGreater(file_count_after, file_count_before,
                           "No new files found in recipient's inbox after message delivery")

                # Step 6: Find the new message file(s)
                new_files = set(inbox_files_after.keys()) - set(inbox_files_before.keys())
                self.assertGreater(len(new_files), 0, "No new message files found")

                # Step 7: Verify the content of at least one new message file contains our test message
                message_found = False
                for new_file in new_files:
                    file_content = inbox_files_after[new_file].get("content")
                    if not file_content:
                        continue

                    try:
                        content_json = json.loads(file_content)
                        message = content_json.get("message", {})

                        # Check if this is our message by comparing content
                        if message.get("data") == message_content:
                            message_found = True

                            # Verify sender and recipient information
                            self.assertEqual(self.sender_address, message.get("from"),
                                             "Sender address doesn't match in the delivered message")
                            self.assertEqual(self.recipient_address, message.get("to"),
                                             "Recipient address doesn't match in the delivered message")
                            break
                    except (json.JSONDecodeError, TypeError):
                        # Not a JSON file or not properly formatted, continue checking
                        continue

                # Final verification that our specific message was found
                self.assertTrue(message_found,
                            f"Sent message with content '{message_content}' not found in recipient's inbox")

            print("Test completed successfully - message was delivered and verified!")

        except Exception as e:
            self.fail(f"End-to-end test failed: {str(e)}")


if __name__ == '__main__':
    unittest.main()
