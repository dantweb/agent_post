import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.message_service import MessageService
from src.message_repository import MessageRepository
from src.city_api import CityAPI
from src.external_api import ExternalAPI


class TestMessageDeliveryPayload(unittest.TestCase):

    @patch('src.city_api.CityAPI.get_cities')
    @patch('src.external_api.requests.post')
    @patch('src.external_api.requests.get')
    def test_message_delivery_post_payload(self, mock_get, mock_post, mock_get_cities):
        now = datetime.now().replace(microsecond=0)

        # City returns one sender and one recipient
        mock_get_cities.return_value = {
            "city_name": "Loopland",
            "cloud_id": "cloud_test",
            "addresses": [
                {"citizen_1": "https://cloud.mock/loopland/api/v1/agent/1234/msg"},
                {"citizen_2": "https://cloud.mock/loopland/api/v1/agent/5678/msg"}
            ]
        }

        # Outbox returns one message from citizen_1 to citizen_2
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "messages": [{
                "from": "citizen_1",
                "to": "citizen_2",
                "data": "Hello!",
                "metadata": {"created_at": now.isoformat()}
            }]
        }

        mock_post.return_value.status_code = 200

        repo = MessageRepository()
        service = MessageService(
            city_api=CityAPI("mocked"),
            external_api=ExternalAPI("token123"),
            message_repo=repo
        )

        service.process_messages()

        # Find all actual POST calls (filtering out raise_for_status etc.)
        actual_post_calls = [
            call for call in mock_post.call_args_list
            if isinstance(call, unittest.mock._Call) and isinstance(call[0], tuple)
        ]

        # Ensure exactly one call was made to the correct recipient
        self.assertEqual(len(actual_post_calls), 2)

        called_url = actual_post_calls[0][0][0]  # first argument of the first call
        payload = actual_post_calls[0][1]['json']  # keyword argument 'json'

        self.assertIn("1234", called_url)
        self.assertEqual(payload["from"], "citizen_1")
        self.assertEqual(payload["to"], "citizen_2")
        self.assertEqual(payload["data"], "Hello!")
        self.assertEqual(payload["metadata"]["created_at"], now.isoformat())


if __name__ == '__main__':
    unittest.main()
