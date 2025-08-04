import unittest

from src.message import Message
from datetime import datetime, timedelta


class TestMessage(unittest.TestCase):
    def test_message_creation(self):
        message = Message(id=1, created_at=datetime.now(), from_address="a", to_address="b", data="data")
        assert message.id == 1
        assert message.created_at

    def test_message_is_old(self):
        old_message = Message(id=1, created_at=datetime.now() - timedelta(days=4),
                              collected_at=datetime.now() - timedelta(days=4), from_address="a", to_address="b",
                              data="data")
        new_message = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="a",
                              to_address="b", data="data")
        assert old_message.is_old()
        assert not new_message.is_old()

    def test_to_list_single_recipient(self):
        """Test that a single address is correctly processed in to_list"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient",
            data="test data"
        )

        # Check that to_list correctly returns a list with the single address
        self.assertEqual(message.address_list, ["recipient"])

    def test_to_list_comma_separated(self):
        """Test that comma-separated addresses are correctly split"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient1,recipient2,recipient3",
            data="test data"
        )

        # Check that to_list correctly splits comma-separated addresses
        self.assertEqual(message.address_list, ["recipient1", "recipient2", "recipient3"])

    def test_to_list_semicolon_separated(self):
        """Test that semicolon-separated addresses are correctly split"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient1;recipient2;recipient3",
            data="test data"
        )

        # Check that to_list correctly splits semicolon-separated addresses
        self.assertEqual(message.address_list, ["recipient1", "recipient2", "recipient3"])

    def test_to_list_space_separated(self):
        """Test that space-separated addresses are correctly split"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient1 recipient2 recipient3",
            data="test data"
        )

        # Check that to_list correctly splits space-separated addresses
        self.assertEqual(message.address_list, ["recipient1", "recipient2", "recipient3"])

    def test_to_list_mixed_delimiters(self):
        """Test that mixed delimiter formats are correctly processed"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient1, recipient2; recipient3",
            data="test data"
        )

        # Check that to_list correctly handles mixed delimiters
        self.assertEqual(message.address_list, ["recipient1", "recipient2", "recipient3"])

    def test_to_list_extra_whitespace(self):
        """Test that extra whitespace is correctly handled"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="  recipient1  ,  recipient2  ",
            data="test data"
        )

        # Check that to_list correctly strips whitespace
        self.assertEqual(message.address_list, ["recipient1", "recipient2"])

    def test_to_list_empty_entries(self):
        """Test that empty entries are correctly filtered out"""
        message = Message(
            id=1,
            created_at=datetime.now(),
            from_address="sender",
            to_address="recipient1,,recipient2",
            data="test data"
        )

        # Check that to_list correctly filters out empty entries
        self.assertEqual(message.address_list, ["recipient1", "recipient2"])
