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
            # Update the main addresses dictionary with each city's agent mappings
            addresses.update(city_dict)

        # Replace WAKEUP with RECEIVE_MSG in all URLs
        for agent_name, url in addresses.items():
            addresses[agent_name] = url.replace("WAKEUP", "RECEIVE_POST")

        return addresses


    def process_messages(self) -> None:
        cities_data = self.city_api.get_cities()

        # Get the agent_name -> URL mapping with WAKEUP replaced by RECEIVE_MSG
        addresses_dict = self.get_agent_addresses(cities_data)

        # Use all URLs for collecting from outboxes
        for agent_name, url in addresses_dict.items():
            try:
                messages_data = self.external_api.collect_from_outbox(url)
                for msg in messages_data:
                    # Split the 'to' field by common delimiters
                    raw_to_field = msg['message']['to']
                    to_parts = [raw_to_field]  # fallback

                    for delim in [';', ',', ' ']:
                        if delim in raw_to_field:
                            to_parts = [addr.strip() for addr in
                                        raw_to_field.replace(';', ' ').replace(',', ' ').split()]
                            break

                    for recipient in set(to_parts):  # remove duplicates
                        # Look up recipient URL directly from our addresses dictionary
                        recipient_url = addresses_dict.get(recipient)

                        if recipient_url:
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
