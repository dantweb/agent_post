import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.message_service import MessageService
from src.message_repository import MessageRepository
from src.city_api import CityAPI
from src.external_api import ExternalAPI


class TestMultiRecipientMessage(unittest.TestCase):

    @patch('src.city_api.CityAPI.get_cities')
    @patch('src.external_api.requests.post')
    @patch('src.external_api.requests.get')
    def test_message_multiple_recipients(self, mock_get, mock_post, mock_get_cities):
        now = datetime.now().replace(microsecond=0)

        # Step 0: Mock citizens' API endpoints
        mock_get_cities.return_value = {
            "city_name": "Loopland",
            "cloud_id": "cloud_test",
            "addresses": [
                {"citizen_1": "https://cloud.mock/loopland/api/v1/agent/1111/msg"},
                {"citizen_2": "https://cloud.mock/loopland/api/v1/agent/2222/msg"},
                {"citizen_3": "https://cloud.mock/loopland/api/v1/agent/3333/msg"}
            ]
        }

        # Step 0a: Mock outbox with one message to multiple recipients
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "messages": [{
                "from": "citizen_1",
                "to": "citizen_2 ; citizen_3, citizen_2 citizen_3",  # mixed delimiters
                "data": "Broadcast",
                "metadata": {"created_at": now.isoformat()}
            }]
        }

        mock_post.return_value.status_code = 200

        # Step 1: Repository and service
        repo = MessageRepository()
        service = MessageService(
            city_api=CityAPI("mocked"),
            external_api=ExternalAPI("token123"),
            message_repo=repo
        )

        service.process_messages()

        # Step 2: Collect all POST calls
        post_calls = [
            call for call in mock_post.call_args_list
            if isinstance(call, unittest.mock._Call) and isinstance(call[0], tuple)
        ]

        # Step 3: Extract unique recipient URLs
        posted_urls = [call[0][0] for call in post_calls]
        posted_recipients = set(u.split("/agent/")[1].split("/")[0] for u in posted_urls)

        self.assertIn("7676", posted_recipients)
        self.assertIn("3333", posted_recipients)

        # Step 4: Assert each received a call
        self.assertGreaterEqual(len(posted_urls), 2)

        # Step 5: Assert message content was preserved
        for call in post_calls:
            payload = call[1]['json']
            self.assertEqual(payload["from"], "citizen_1")
            self.assertEqual(payload["data"], "Broadcast")
            self.assertEqual(payload["metadata"]["created_at"], now.isoformat())


if __name__ == '__main__':
    unittest.main()
