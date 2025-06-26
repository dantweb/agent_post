import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.message import Message
from src.message_service import MessageService
from src.message_repository import MessageRepository
from src.city_api import CityAPI
from src.external_api import ExternalAPI


class TestMessageFlow(unittest.TestCase):

    @patch('src.city_api.CityAPI.get_cities')
    @patch('src.external_api.requests.post')
    @patch('src.external_api.requests.get')
    def test_full_message_flow(self, mock_outbox_get, mock_post, mock_get_cities):
        now = datetime.now()

        # Step 0: Mock host that returns citizens' addresses
        mock_get_cities.return_value = {
            "city_name": "Loopland",
            "cloud_id": "cloud_test",
            "addresses": [
                {"citizen_1": "https://cloud.mock/loopland/api/v1/agent/1234/msg"},
                {"citizen_2": "https://cloud.mock/loopland/api/v1/agent/5678/msg"}
            ]
        }

        # Step 0a: Mock outbox messages
        def mock_outbox(url, *args, **kwargs):
            mock_response = MagicMock()
            mock_response.status_code = 200
            if "1234" in url:
                mock_response.json.return_value = {
                    "messages": [{
                        "from": "citizen_1",
                        "to": "citizen_2",
                        "data": "Hello!",
                        "metadata": {"created_at": now.isoformat()}
                    }]
                }
            else:
                mock_response.json.return_value = {"messages": []}
            return mock_response

        mock_outbox_get.side_effect = mock_outbox

        # Step 1: Create real repository with SQLite
        repo = MessageRepository()  # Uses in-memory DB

        # Step 2: Patch message delivery (inbox)
        mock_post.return_value.status_code = 200

        # Step 3: Run service
        service = MessageService(
            city_api=CityAPI("mocked"),
            external_api=ExternalAPI("token123"),
            message_repo=repo
        )
        service.process_messages()

        # Step 4: Validate stored message
        stored = repo.find_all()
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0].from_address.split('/')[-1], "citizen_1")
        self.assertEqual(stored[0].to_address.split('/')[-1], "citizen_2")

        # Step 5: Validate message was posted (delivered)
        mock_post.assert_called()
        called_url = mock_post.call_args[0][0]
        self.assertIn("1234", called_url)


if __name__ == '__main__':
    unittest.main()
