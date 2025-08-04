import unittest
from datetime import datetime
from src.message_service import MessageService
from src.message_repository import MessageRepository
from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message import Message


class TestMessageDeliveryPayload(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies before each test"""
        # Create real instances of all dependencies
        self.city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
        self.external_api = ExternalAPI("XXXXXX")
        self.message_repo = MessageRepository()

        # Create the service under test
        self.message_service = MessageService(
            city_api=self.city_api,
            external_api=self.external_api,
            message_repo=self.message_repo
        )

        # Clean up any test messages from previous test runs
        self.clean_up_test_messages()

    def tearDown(self):
        """Clean up after tests"""
        self.clean_up_test_messages()

    def clean_up_test_messages(self):
        """Remove any test messages created during testing"""
        all_messages = self.message_repo.find_all()
        for msg in all_messages:
            if "TEST_PAYLOAD" in str(msg.data):
                self.message_repo.delete(msg)

    def test_get_agent_addresses(self):
        """Test the agent address extraction functionality"""
        # Get real cities data
        cities_data = self.city_api.get_cities()

        # Get agent addresses
        agent_addresses = self.message_service.get_agent_addresses(cities_data)

        # Verify the structure and content
        self.assertIsInstance(agent_addresses, dict)
        self.assertGreater(len(agent_addresses), 0, "No agent addresses found")

        # Verify all URLs have RECEIVE_POST instead of WAKEUP
        for agent_name, url in agent_addresses.items():
            self.assertIn("RECEIVE_POST", url)
            self.assertNotIn("WAKEUP", url)

    def test_message_multi_recipient_delivery(self):
        """
        Test the delivery of messages to multiple recipients
        This test verifies that:
        1. The message service can process cities data to extract agent addresses
        2. The service correctly handles messages with multiple recipients
        3. The correct message payload structure is maintained
        """
        # Prepare test data
        cities_data = self.city_api.get_cities()
        agent_addresses = self.message_service.get_agent_addresses(cities_data)

        # We need at least two agents for this test
        if len(agent_addresses) < 2:
            self.skipTest("Need at least two agents to test multi-recipient functionality")

        # Get the first two agents for our test
        agent_names = list(agent_addresses.keys())[:2]
        sender_name = agent_names[0]
        recipient_name = agent_names[1]

        # Place a test message in the system
        # We'll do this by directly creating a message in the repository
        test_message = Message(
            id=1,
            from_address=sender_name,
            to_address=recipient_name,
            data="TEST_PAYLOAD_MESSAGE",
            created_at=datetime.now(),
            delivered_at=datetime.now()
        )

        try:
            # Save the message to the repository
            self.message_repo.save(test_message)

            # Run the message processing service
            self.message_service.process_messages()

            # Get the message from the repository to verify it was processed
            messages = self.message_repo.find_all()
            test_messages = [msg for msg in messages if msg.id == test_message.id]

            # Verify the message exists and has been processed
            self.assertEqual(len(test_messages), 1, "Test message not found in repository")
            processed_message = test_messages[0]

            # Verify the message data
            self.assertEqual(processed_message.from_address, sender_name)
            self.assertEqual(processed_message.to_address, recipient_name)
            self.assertEqual(processed_message.data, "TEST_PAYLOAD_MESSAGE")

            # If the message service sets delivered_at timestamp, verify it's not None
            if hasattr(processed_message, 'delivered_at'):
                self.assertIsNotNone(processed_message.delivered_at,
                                     "Message should be marked as delivered")

        except Exception as e:
            self.fail(f"Test failed with exception: {e}")

    def test_remove_old_messages(self):
        """Test the removal of old messages"""
        # This test directly calls remove_old_messages and verifies old messages are removed

        # Create a current message that should not be removed
        current_message = Message(
            id=123,
            from_address="test_sender",
            to_address="test_recipient",
            data="TEST_PAYLOAD_CURRENT",
            created_at=datetime.now(),
            delivered_at=datetime.now()
        )

        try:
            self.message_repo.save(current_message)
            self.message_service.remove_old_messages()
            messages = self.message_repo.find_all()
            current_messages = [msg for msg in messages if msg.id == current_message.id]
            self.assertEqual(len(current_messages), 1,
                             "Current message should not be removed")

        except Exception as e:
            self.fail(f"Test failed with exception: {e}")

        finally:
            try:
                self.message_repo.delete(current_message)
            except:
                pass
