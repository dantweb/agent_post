import os
import sys
from dotenv import load_dotenv

# Define the base directory of the project, assuming the script is in agent_post/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
# Add the 'src' directory to the Python path to allow importing project modules [2]
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)

# Import the necessary classes from the 'src' directory [1]
from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_repository import MessageRepository
from src.message_service import MessageService

def run_message_processing_job():
    """
    Executes the message processing and cleanup logic for the Agent Post service.
    This function is designed to be run as a scheduled cron job.
    """
    print("🚀 Starting Agent Post message processing cron job...")

    # **1. Read the .env file**
    # This loads environment variables from the .env file into the script's environment [3-5].
    load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))
    print("✅ .env file loaded.")

    # Get necessary environment variables
    # The DATABASE_URL is explicitly defined in the provided .env excerpt and used by setup scripts [5-7].
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL environment variable not set in .env. Exiting.")
        sys.exit(1)

    # **Retrieve CITY_API_URL and EXTERNAL_API_TOKEN:**
    # The sources show these are required for `CityAPI` and `ExternalAPI` initialization [8, 9].
    # While they are not explicitly present in the provided `agent_post/.env` [7],
    # they are typically configured as environment variables in a production setup.
    # For this script to work, you would need to add these to your `.env` file.
    # Example placeholder values are used in tests [10-14].
    city_api_url = os.getenv('CITY_API_URL')
    external_api_token = os.getenv('EXTERNAL_API_TOKEN')

    if not city_api_url:
        print("⚠️ CITY_API_URL not set in .env. Using a placeholder 'http://mocked-city-api-url'. Please configure it in .env for production environments.")
        city_api_url = "http://mocked-city-api-url" # Placeholder, replace with actual URL in .env
    if not external_api_token:
        print("⚠️ EXTERNAL_API_TOKEN not set in .env. Using a placeholder 'default_token'. Please configure it in .env for production environments.")
        external_api_token = "default_token" # Placeholder, replace with actual token in .env

    try:
        # **Initialize core components:**
        # The `MessageRepository` handles database interactions for messages [15].
        repo = MessageRepository(db_url=db_url)
        # The `CityAPI` is used to retrieve cloud agent endpoints for citizens [9, 16].
        city_api = CityAPI(api_url=city_api_url)
        # The `ExternalAPI` handles pulling messages from outboxes and delivering them to inboxes [7, 8, 17-19].
        external_api = ExternalAPI(token=external_api_token)

        # **Instantiate MessageService:**
        # `MessageService` orchestrates the entire message flow, using the above components [1].
        service = MessageService(city_api=city_api, external_api=external_api, message_repo=repo)

        print("🔄 Processing messages (fetching, saving, delivering)...")
        # **Get list of API endpoints of citizens, receive, and send messages:**
        # The `process_messages` method within `MessageService` performs these exact steps:
        # 1. Calls `city_api.get_cities()` to get all citizen addresses (API endpoints) [1].
        # 2. Iterates through these URLs [20].
        # 3. For each URL, it calls `external_api.collect_from_outbox()` to **receive** messages [18, 20].
        # 4. It then saves these collected messages to the local database using `message_repo.save()` [21].
        # 5. Finally, it calls `external_api.add_to_inbox()` for each resolved recipient to **send** messages [7, 19, 21].
        # It also handles multi-recipient delivery by splitting the 'to' field [18, 19, 22].
        service.process_messages()
        print("✅ Messages processed and delivered successfully.")

        print("🧹 Removing old messages...")
        # The `MessageService` also has a method to automatically purge outdated messages [22, 23].
        service.remove_old_messages()
        print("✅ Old messages removed from the repository.")

    except Exception as e:
        print(f"❌ An unexpected error occurred during the cron job: {e}")
        sys.exit(1)

    print("🎉 Agent Post message processing cron job completed.")

if __name__ == "__main__":
    run_message_processing_job()