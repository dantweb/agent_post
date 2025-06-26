import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta
from src.message import Message
from src.message_service import MessageService

class TestMessageService(unittest.TestCase):

    def test_message_service_process_messages_success(self):
        # Mocks
        city_api = MagicMock()
        external_api = MagicMock()
        message_repo = MagicMock()

        # Simulated data
        city_api.get_cities.return_value = {
            "city_name": "Test City",
            "cloud_id": "cloud27",
            "addresses": [
                {"john_33": "https://localhost:5000/loopland/api/v1/agent/232342/msg"}
            ]
        }
        external_api.collect_from_outbox.return_value = [{
            "from": "john_33",
            "to": "john_mikal_51",
            "data": "some data",
            "metadata": {"created_at": "2024-10-27T10:00:00"}
        }]

        # Service and call
        service = MessageService(city_api, external_api, message_repo)
        service.process_messages()

        # Verify
        self.assertTrue(message_repo.save.called)
        self.assertTrue(external_api.add_to_inbox.called)

    def test_message_service_remove_old_messages(self):
        old_message = Message(
            id=1,
            created_at=datetime.now() - timedelta(days=4),
            collected_at=datetime.now() - timedelta(days=4),
            from_address="addr1",
            to_address="addr2",
            data="data"
        )
        new_message = Message(
            id=2,
            created_at=datetime.now(),
            collected_at=datetime.now(),
            from_address="addr1",
            to_address="addr2",
            data="data"
        )

        message_repo = MagicMock()
        message_repo.find_all.return_value = [old_message, new_message]

        city_api = MagicMock()
        external_api = MagicMock()

        service = MessageService(city_api, external_api, message_repo)
        service.remove_old_messages()

        message_repo.delete.assert_called_once_with(old_message)
