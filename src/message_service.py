from datetime import datetime, timedelta
from city_api import CityAPI
from external_api import ExternalAPI
from typing import Dict

from src.message import Message


class MessageService:
    def __init__(self, city_api: CityAPI, external_api: ExternalAPI):
        self.city_api = city_api
        self.external_api = external_api
        self.recipient_list = []
        self.sender_list = []


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
            addresses[agent_name] = url

        return addresses

    def process_messages(self) -> None:
        cities_data = self.city_api.get_cities()
        addresses_dict = self.get_agent_addresses(cities_data)

        for agent_name, url in addresses_dict.items():
            try:
                print(f"\n\n url for collect = {url}")
                messages_data = self.external_api.collect_from_outbox(url)
                for msg in messages_data:
                    print(f"msg = {msg}")
                    for recipient in set(msg.address_list):
                        print(f"recipient = {recipient}")
                        self.recipient_list.append(recipient)
                        recipient_url = addresses_dict.get(recipient)
                        print(f"recipient_url = {recipient_url}")
                        if recipient_url:
                            recipient_url = recipient_url.replace("WAKEUP", "RECEIVE_POST")

                            # Mark the message as delivered
                            msg.delivered_at = datetime.now()
                            filepath = f"./{msg.delivered_at}.json"
                            blob = {
                                "updated_files": [{
                                    "path": filepath,
                                    "file_content": msg.to_json()
                                }]
                            }
                            response = self.external_api.add_to_inbox(recipient_url, blob)

                            print(f"response = {response}")

                            self.sender_list.append(msg.from_address)


            except Exception as e:
                print(f"Error processing messages from {url}: {str(e)}")
                print(f"Exception type: {type(e).__name__}")
                print(f"Message details: {msg if 'msg' in locals() else 'No message available'}")
                import traceback
                traceback.print_exc()

