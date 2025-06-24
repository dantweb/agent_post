import pytest
from src.message_service import MessageService
from src.message import Message
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


@patch('src.city_api.CityAPI.get_cities')
@patch('src.external_api.ExternalAPI.collect_from_outbox')
@patch('src.message_repository.MessageRepository.save')
def test_message_service_process_messages_success(mock_save, mock_collect, mock_get_cities):
    mock_get_cities.return_value = {
        "city_name": "Test City",
        "cloud_id": "cloud27",
        "addresses": [
            {"john_33": "https://localhost:5000/loopland/api/v1/agent/232342/msg"}
        ]
    }
    mock_collect.return_value = [{"from": "john_33", "to": "john_mikal_51", "data": "some data",
                                  "metadata": {"created_at": "2024-10-27T10:00:00"}}]

    message_repo = MagicMock()
    city_api = MagicMock()
    external_api = MagicMock()
    service = MessageService(city_api, external_api, message_repo)
    service.process_messages()
    mock_save.assert_called()
    mock_collect.assert_called()


@patch('src.message_repository.MessageRepository.find_all')
@patch('src.message_repository.MessageRepository.delete')
def test_message_service_remove_old_messages(mock_delete, mock_find_all):
    old_message = Message(id=1, created_at=datetime.now() - timedelta(days=4),
                          collected_at=datetime.now() - timedelta(days=4), from_address="addr1", to_address="addr2",
                          data="data")
    new_message = Message(id=2, created_at=datetime.now(), collected_at=datetime.now(), from_address="addr1",
                          to_address="addr2", data="data")
    mock_find_all.return_value = [old_message, new_message]
    message_repo = MagicMock()
    city_api = MagicMock()
    external_api = MagicMock()
    service = MessageService(city_api, external_api, message_repo)
    service.remove_old_messages()
    mock_delete.assert_called_once_with(old_message)
