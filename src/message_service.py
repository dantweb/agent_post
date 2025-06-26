from datetime import datetime, timedelta
from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message import Message
from src.message_repository import MessageRepository


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
                    # Split the 'to' field by common delimiters
                    raw_to_field = msg['to']
                    to_parts = [raw_to_field]  # fallback

                    for delim in [';', ',', ' ']:
                        if delim in raw_to_field:
                            to_parts = [addr.strip() for addr in raw_to_field.replace(';', ' ').replace(',', ' ').split()]
                            break

                    # Get sender prefix (e.g., agent_id from URL)
                    sender_prefix = url.split('/')[6]

                    for recipient in set(to_parts):  # remove duplicates
                        recipient_url = next(
                            (addr for data in cities_data['addresses'] for key, addr in data.items() if key == recipient),
                            None
                        )

                        if recipient_url:
                            # Save message with updated recipient
                            message = Message(
                                id=None,
                                created_at=datetime.fromisoformat(msg['metadata']['created_at']),
                                collected_at=datetime.now(),
                                delivered_at=None,
                                from_address=f"{sender_prefix}/{msg['from']}",
                                to_address=f"{recipient_url.split('/')[6]}/{recipient}",
                                data=msg['data']
                            )
                            self.message_repo.save(message)

                            # Deliver message
                            self.external_api.add_to_inbox(recipient_url, msg)

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
