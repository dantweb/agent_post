import unittest
from datetime import datetime
from src.message_repository import MessageRepository
from src.message import Message

class TestMessageRepository(unittest.TestCase):

    def setUp(self):
        self.repo = MessageRepository()

    def tearDown(self):
        self.repo.engine.dispose()

    def test_message_repository_save_and_retrieve(self):
        msg = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from", to_address="to", data="data")
        self.repo.save(msg)
        retrieved = self.repo.find_all()
        self.assertEqual(len(retrieved), 1)
        self.assertEqual(retrieved[0], msg)

    def test_message_repository_delete(self):
        msg = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from", to_address="to", data="data")
        self.repo.save(msg)
        self.repo.delete(msg)
        self.assertEqual(len(self.repo.find_all()), 0)

    def test_message_repository_find_by_address(self):
        msg1 = Message(id=1, created_at=datetime.now(), collected_at=datetime.now(), from_address="from_addr", to_address="to_addr", data="data")
        msg2 = Message(id=2, created_at=datetime.now(), collected_at=datetime.now(), from_address="other_from", to_address="to_addr", data="data")
        self.repo.save(msg1)
        self.repo.save(msg2)
        results = self.repo.find_by_address("to_addr")
        self.assertEqual(len(results), 2)
