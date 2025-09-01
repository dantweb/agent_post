# tests/test_message_integration.py
import os
import time
import unittest
import requests
from datetime import datetime
from dotenv import load_dotenv

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService


class TestMessageIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with real components"""
        # Load environment variables from .env file
        load_dotenv()

        # Get API URLs and tokens from environment variables, with defaults
        city_api_url = os.getenv("CITY_API_URL", "http://loopai_web:5000/api/agents/cities-data/")
        external_api_token = os.getenv("EXTERNAL_API_TOKEN", "xxxxxxx")

        # Create real API instances
        self.city_api = CityAPI(city_api_url)
        self.external_api = ExternalAPI(external_api_token)

        # Create the service with real dependencies
        self.service = MessageService(self.city_api, self.external_api)

        # Base URL to retrieve filesystem structure; note the endpoint is for testing purposes.
        self.filesystem_url = "http://loopai_web:5000/api/test/agentlife/fs/"

    def get_agent_filesystem(self, agent_id):
        """
        Retrieve the full filesystem structure of the specified agent using the real endpoint.
        """
        url = f"{self.filesystem_url}?agent_id={agent_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def test_message_flow_integration(self):
        """
        Test the complete message flow using real API calls. This test simply verifies that
        process_messages() runs without error.
        """
        self.service.process_messages()
        self.assertTrue(True, "Integration test completed without errors")

    def test_agent_addresses_from_real_api(self):
        """
        Test retrieving agent addresses from the real City API.
        """
        cities_data = self.city_api.get_cities()
        addresses = self.service.get_agent_addresses(cities_data)

        self.assertIsNotNone(addresses, "No addresses returned from real API")
        self.assertIsInstance(addresses, dict, "Addresses should be a dictionary")

        for agent_name, url in addresses.items():
            self.assertIsInstance(agent_name, str, "Agent name should be a string")
            self.assertIsInstance(url, str, "URL should be a string")
            self.assertTrue(url.startswith("http"), f"URL should start with http: {url}")
            self.assertTrue("/api/" in url.lower(), f"URL should contain /api/: {url}")

        print(f"\nRetrieved {len(addresses)} agent addresses from real City API")

    def test_message_delivery_integration(self):
        """
        Integration test that verifies a message is properly moved from sender's outbox to
        the recipient's inbox.

        Debugging output is added to log:
         - The sender's outbox/new content before processing.
         - The recipient's inbox/new content before processing.
         - The recipient's inbox/new content after process_messages() is called.
         - Confirmation that the real data was transferred.
        """
        sender_agent_id = "1"  # Replace with actual sender agent ID if needed
        recipient_agent_id = "2"  # Replace with actual recipient agent ID if needed

        # Step 1: Get filesystem state before processing
        sender_fs_before = self.get_agent_filesystem(sender_agent_id)
        recipient_fs_before = self.get_agent_filesystem(recipient_agent_id)

        # Extract sender outbox/new and recipient inbox/new
        sender_outbox = sender_fs_before.get('filesystem', {}).get('outbox', {}).get('new', {})
        recipient_inbox_before = recipient_fs_before.get('filesystem', {}).get('inbox', {}).get('new', {})


        if not sender_outbox:
            self.skipTest("No messages found in sender's outbox for testing")

        sender_outbox_count_before = len(sender_outbox)
        recipient_inbox_count_before = len(recipient_inbox_before) if recipient_inbox_before else 0

        # (Optional) Track one message ID for debugging purposes
        sample_message_id = list(sender_outbox.keys())[0] if sender_outbox else None
        if sample_message_id:
            print(f"\nTracking message ID from sender: {sample_message_id}")

        # Step 2: Process messages using the real service
        self.service.process_messages()

        # Allow some time for processing and filesystem update
        time.sleep(2)

        # Step 3: Get filesystem state after processing
        sender_fs_after = self.get_agent_filesystem(sender_agent_id)
        recipient_fs_after = self.get_agent_filesystem(recipient_agent_id)

        sender_outbox_after = sender_fs_after.get('filesystem', {}).get('outbox', {}).get('new', {})
        recipient_inbox_after = recipient_fs_after.get('filesystem', {}).get('inbox', {}).get('new', {})

        sender_outbox_count_after = len(sender_outbox_after) if sender_outbox_after else 0
        recipient_inbox_count_after = len(recipient_inbox_after) if recipient_inbox_after else 0

        # Step 4: Verify that the sender's outbox has fewer messages
        self.assertLess(sender_outbox_count_after, sender_outbox_count_before,
                        "Sender's outbox should have fewer messages after processing")
        # And that the recipient's inbox has more messages
        self.assertGreater(recipient_inbox_count_after, recipient_inbox_count_before,
                           "Recipient's inbox should have more messages after processing")

        # Step 5: Verify delivered file details in recipient's inbox
        delivered_file = None

        for file_path, file_info in recipient_inbox_after.items():
            content = file_info.get("file_content")
            if not content:
                continue
            try:
                delivered_data = self.service.get_message_from_json(content)
            except Exception:
                continue

            # Check if delivered_data appears to match expected message structure
            # If a sample_message_id was tracked, use it in the comparison.
            if sample_message_id and (sample_message_id in delivered_data.get("id", "")):
                delivered_file = {"path": file_path, "data": delivered_data}
                break

        # If not found by sample_message_id, simply pick the first delivered message
        if delivered_file is None and recipient_inbox_after:
            sample_path = list(recipient_inbox_after.keys())[0]
            delivered_file = {
                "path": sample_path,
                "data": self.service.get_message_from_json(recipient_inbox_after[sample_path]["file_content"])
            }

        self.assertIsNotNone(delivered_file,
                             "No delivered message file found in recipient's inbox after processing")

        # Verify that the filename starts with "./" and ends with ".txt"
        filename = delivered_file["path"]
        self.assertTrue(filename.startswith("./") and filename.endswith(".txt"),
                        "The delivered message filename should start with './' and end with '.txt'")

        # Extract and validate the timestamp part from the filename.
        timestamp_str = filename[2:-4]
        try:
            int(timestamp=int(timestamp_str))
        except ValueError:
            self.fail("The timestamp part of the filename is not an integer")

        # Check that the delivered message JSON content includes a delivered_at timestamp.
        self.assertIn("delivered_at", delivered_file["data"],
                      "Delivered message content must include a 'delivered_at' property")
        self.assertIsNotNone(delivered_file["data"]["delivered_at"],
                             "The 'delivered_at' field should not be None in the delivered content")



if __name__ == '__main__':
    unittest.main()
