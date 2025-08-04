from datetime import datetime, timedelta
from city_api import CityAPI
from external_api import ExternalAPI
from message import Message
from message_repository import MessageRepository
from typing import Dict


class MessageService:
    def __init__(self, city_api: CityAPI, external_api: ExternalAPI, message_repo: MessageRepository):
        self.city_api = city_api
        self.external_api = external_api
        self.message_repo = message_repo


    def get_agent_addresses(self, cities_data: Dict) -> Dict[str, str]:
        """
        Creates a dictionary mapping agent names to their URLs from cities data.

        Args:
            cities_data: The cities data dictionary

        Returns:
            Dictionary mapping agent public names to their API URLs with WAKEUP replaced by RECEIVE_MSG
        """
        # Create a single dictionary from all addresses dictionaries
        addresses = {}
        for city_dict in cities_data.get('addresses', []):
            addresses.update(city_dict)

        for agent_name, url in addresses.items():
            addresses[agent_name] = url.replace("WAKEUP", "RECEIVE_POST")

        return addresses


    def process_messages(self) -> None:
        cities_data = self.city_api.get_cities()
        addresses_dict = self.get_agent_addresses(cities_data)

        for agent_name, url in addresses_dict.items():
            try:
                messages_data = self.external_api.collect_from_outbox(url)
                for msg in messages_data:
                    for recipient in set(msg.address_list):
                        recipient_url = addresses_dict.get(recipient)
                        if recipient_url:
                            self.external_api.add_to_inbox(recipient_url, msg)

            except Exception as e:
                print(f"Error processing messages from {url}: {str(e)}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Message details: {msg if 'msg' in locals() else 'No message available'}")
                import traceback

                traceback.print_exc()

        self.remove_old_messages()


    def remove_old_messages(self) -> None:
        messages = self.message_repo.find_all()
        old_messages = [msg for msg in messages if msg.is_old()]
        for msg in old_messages:
            try:
                self.message_repo.delete(msg)
            except Exception as e:
                print(f"Error deleting old message {msg.id}: {e}")
