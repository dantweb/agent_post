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
