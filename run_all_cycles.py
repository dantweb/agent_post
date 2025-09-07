#!/usr/bin/env python3
import json
import os
import sys
import subprocess

from flask.cli import load_dotenv

from src.city_api import CityAPI
import dotenv

load_dotenv()


# Define the base directory of the project, assuming the script is in agent_post/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# Add the 'src' directory to the Python path to allow importing project modules [2]
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)


AGENT_POST_CONFIG_JSON = "agent_post_config.json"

def load_config(config_path: str) -> dict:
    """Load and return configuration from a JSON file."""
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config
    except Exception as e:
        print(f"Error loading configuration from {config_path}: {e}")
        return {}


def run():
    # Extract the cities_url from the config and assign it as api_url (fallback provided)
    api_url = os.getenv("CITY_API_URL",
                        "http://loopai_web:5000/api/agents/cities-data/")
    print(f"Using API URL: {api_url}")
    city_api = CityAPI(api_url)

    try:
        cities_data = city_api.get_cities()
    except Exception as e:
        print(f"Error fetching cities: {e}")
        return

    # Extract addresses (assuming cities_data includes an "addresses" key with a list of dictionaries)
    addresses = {}
    for address_dict in cities_data.get("addresses", []):
        addresses.update(address_dict)

    # Loop through each citizen's address and run the actions
    for citizen_name, recipient_url in addresses.items():
        for action in ["READ_POSTS", "DO_TASK_1"]:
            # Replace "WAKEUP" with "RECEIVE_POST" in the recipient URL
            modified_url = recipient_url.replace("WAKEUP", action)
            print(f"Citizen: {citizen_name}, Action: {action}, URL: {modified_url}")

            # Execute the curl command against the modified URL
            try:
                result = subprocess.run(
                    ["curl", modified_url],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"curl output: {result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Error executing curl on {modified_url}: {e}")


if __name__ == "__main__":
    run()
