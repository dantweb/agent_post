import unittest
import pytest
from src.message_repository import MessageRepository
from src.message.message import Message
from datetime import datetime


class TestMessageRepository(unittest.TestCase):
    @pytest.fixture
    def message_repo(self):
        repo = MessageRepository()
        yield repo
        repo.engine.dispose()


    def test_message_repository_save_and_retrieve(self, message_repo):
        msg = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from", to_address="to",
                      data="data")
        message_repo.save(msg)
        retrieved_messages = message_repo.find_all()
        assert len(retrieved_messages) == 1
        assert retrieved_messages[0] == msg


    def test_message_repository_delete(self, message_repo):
        msg = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from", to_address="to",
                      data="data")
        message_repo.save(msg)
        message_repo.delete(msg)
        retrieved_messages = message_repo.find_all()
        assert len(retrieved_messages) == 0


    def test_message_repository_find_by_address(self, message_repo):
        msg1 = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from_addr",
                       to_address="to_addr", data="data")
        msg2 = Message(id=2, created_at=datetime.now(), collected_at=datetime.now(), from_address="other_from",
                       to_address="to_addr", data="data")
        message_repo.save(msg1)
        message_repo.save(msg2)
        retrieved_messages = message_repo.find_by_address("to_addr")
        assert len(retrieved_messages) == 2
