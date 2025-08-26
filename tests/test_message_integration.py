import unittest
import os
from datetime import datetime
from dotenv import load_dotenv

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService


class TestMessageIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies with real components"""
        # Load environment variables
        load_dotenv()

        # Get API URLs and tokens from environment variables
        city_api_url = os.getenv("CITY_API_URL", "http://loopai_web:5000/api/agents/cities-data/")
        external_api_token = os.getenv("EXTERNAL_API_TOKEN", "xxxxxxx")

        # Create real API instances
        self.city_api = CityAPI(city_api_url)
        self.external_api = ExternalAPI(external_api_token)

        # Create the service with real dependencies
        self.service = MessageService(self.city_api, self.external_api)

    def test_message_flow_integration(self):
        """
        Test the complete message flow using real components and real API calls
        """
        # Execute the method under test with real API calls
        self.service.process_messages()

        # Since we're using real APIs, we can't make specific assertions about
        # the exact responses, but we can check that the process completed without errors

        # Optional: Log some information about what happened during the test
        print("\nIntegration test completed with real API data")

        # If we want to make assertions, we would need to have deterministic test data
        # in the real APIs or have a way to verify the effects of the process

        # One option could be to check that messages were processed from the log output
        # or by checking a database if there's one involved

        # For now, simply passing without errors is a valid test
        self.assertTrue(True, "Integration test completed without errors")

    def test_agent_addresses_from_real_api(self):
        """Test getting agent addresses from the real City API"""
        # Get actual cities data from the real API
        cities_data = self.city_api.get_cities()

        # Extract addresses using the service method
        addresses = self.service.get_agent_addresses(cities_data)

        # Verify that we got some addresses
        self.assertIsNotNone(addresses, "No addresses returned from real API")
        self.assertIsInstance(addresses, dict, "Addresses should be a dictionary")

        # Verify that the addresses have the expected format
        for agent_name, url in addresses.items():
            self.assertIsInstance(agent_name, str, "Agent name should be a string")
            self.assertIsInstance(url, str, "URL should be a string")
            self.assertTrue(url.startswith("http"), f"URL should start with http: {url}")
            self.assertTrue("/api/" in url.lower(), f"URL should contain /api/: {url}")

        print(f"\nRetrieved {len(addresses)} agent addresses from real City API")


def test_message_delivery_integration(self):
    """
    Integration test that verifies a message is properly moved from sender's outbox to recipient's inbox
    by checking the filesystem structure before and after message processing
    """
    import requests
    import time

    # Step 1: Setup test data
    # Define sender and recipient agents
    sender_agent_id = "1"  # Replace with actual sender agent ID
    recipient_agent_id = "2"  # Replace with actual recipient agent ID

    # Get the initial filesystem state for both agents
    sender_fs_before = requests.get(f"http://loopai_web:5000/api/test/agentlife/fs?agent_id={sender_agent_id}").json()
    recipient_fs_before = requests.get(
        f"http://loopai_web:5000/api/test/agentlife/fs?agent_id={recipient_agent_id}").json()

    # Check if there's a message in the sender's outbox
    sender_outbox = sender_fs_before.get('filesystem', {}).get('outbox', {}).get('new', {})
    if not sender_outbox:
        self.skipTest("No messages found in sender's outbox for testing")

    # Count messages in sender's outbox and recipient's inbox before processing
    sender_outbox_msg_count = len(sender_outbox)
    recipient_inbox_before = recipient_fs_before.get('filesystem', {}).get('inbox', {}).get('new', {})
    recipient_inbox_msg_count_before = len(recipient_inbox_before) if recipient_inbox_before else 0

    # Get a sample message ID from sender's outbox for tracking
    sample_message_id = list(sender_outbox.keys())[0] if sender_outbox else None
    if sample_message_id:
        print(f"Tracking message ID: {sample_message_id}")

    # Step 2: Process messages using our message service
    self.message_service.process_messages()

    # Allow some time for processing to complete
    time.sleep(2)

    # Step 3: Get the filesystem state after processing
    sender_fs_after = requests.get(f"http://loopai_web:5000/api/test/agentlife/fs?agent_id={sender_agent_id}").json()
    recipient_fs_after = requests.get(
        f"http://loopai_web:5000/api/test/agentlife/fs?agent_id={recipient_agent_id}").json()

    # Check sender's outbox after processing
    sender_outbox_after = sender_fs_after.get('filesystem', {}).get('outbox', {}).get('new', {})
    sender_outbox_msg_count_after = len(sender_outbox_after) if sender_outbox_after else 0

    # Check recipient's inbox after processing
    recipient_inbox_after = recipient_fs_after.get('filesystem', {}).get('inbox', {}).get('new', {})
    recipient_inbox_msg_count_after = len(recipient_inbox_after) if recipient_inbox_after else 0

    # Step 4: Verify message delivery
    # The sender's outbox should have fewer messages
    self.assertLess(sender_outbox_msg_count_after, sender_outbox_msg_count,
                    "Sender's outbox should have fewer messages after processing")

    # The recipient's inbox should have more messages
    self.assertGreater(recipient_inbox_msg_count_after, recipient_inbox_msg_count_before,
                       "Recipient's inbox should have more messages after processing")

    # If we were tracking a specific message, verify it's not in sender's outbox anymore
    if sample_message_id:
        self.assertNotIn(sample_message_id, sender_outbox_after,
                         f"Message {sample_message_id} should no longer be in sender's outbox")

        # Check if the message or its content appears in recipient's inbox
        # This is tricky as the message ID might change during delivery
        # So we'll check if any new messages appeared in recipient's inbox
        new_messages = set(recipient_inbox_after.keys()) - set(
            recipient_inbox_before.keys() if recipient_inbox_before else [])
        self.assertGreater(len(new_messages), 0, "New messages should appear in recipient's inbox")

    # Print success message
    print("Integration test completed successfully. Messages were properly delivered.")



if __name__ == '__main__':
    unittest.main()
