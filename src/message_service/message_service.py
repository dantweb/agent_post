from typing import List
from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message import Message
from src.message_repository import MessageRepository
from datetime import datetime, timedelta


class MessageService:
    def __init__(self, city_api: CityAPI, external_api: ExternalAPI, message_repo: MessageRepository):
        self.city_api = city_api
        self.external_api = external_api
        self.message_repo = message_repo

    def process_messages(self) -> None:
        cities_data = self.city_api.get_cities()
        addresses = [addr for data in cities_data['addresses'] for addr in data.values()]

        for url in addresses:
            try:
                messages_data = self.external_api.collect_from_outbox(url)
                for msg in messages_data:
                    message = Message(id=0,  # You need to generate unique IDs here
                                      created_at=datetime.fromisoformat(msg['metadata']['created_at']),
                                      collected_at=datetime.now(),
                                      delivered_at=None,
                                      from_address=f"{url.split('/')[6]}/{msg['from']}",
                                      to_address=f"{url.split('/')[6]}/{msg['to']}",
                                      data=msg['data'])
                    self.message_repo.save(message)
                    self.external_api.add_to_inbox(url, msg)
            except Exception as e:
                print(f"Error processing messages from {url}: {e}")
        self.remove_old_messages()

    def remove_old_messages(self) -> None:
        messages = self.message_repo.find_all()
        old_messages = [msg for msg in messages if msg.is_old()]
        for msg in old_messages:
            try:
                self.message_repo.delete(msg)
            except Exception as e:
                print(f"Error deleting old message {msg.id}: {e}")
