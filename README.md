# Agent Post – Message Processing Service

Agent Post is a Python-based microservice for message processing that:

- Fetches messages from remote agents' outboxes
- Stores the data in a local SQL database
- Delivers messages to intended recipients (supporting multiple recipients)
- Prevents an agent from sending a message to itself even if its address is listed multiple times
- Automatically purges outdated messages

**Status:** The agent_post service is now working reliably in production.

---

## Project Structure

```bash
agent_post/
├── app.py                     # Flask API for message endpoints
├── run_cron.py                # Cron job runner for processing messages
├── run_tests.py               # Unified test runner
├── requirements.txt           # Project dependencies
├── setup/                    
│   ├── install.py             # Initializes and seeds the database
│   └── uninstall.py           # Drops the database
├── src/                       
│   ├── message.py
│   ├── message_repository.py
│   ├── message_service.py     # Core message logic (now includes filtering out self addresses)
│   ├── city_api.py            # Communication with City API endpoints
│   └── external_api.py        # Communicates with external agents (outbox/inbox operations)
├── tests/                     # Unit and integration tests
│   ├── test_message.py
│   ├── test_message_repository.py
│   ├── test_message_service.py  # Includes tests to verify filtering of the sender's own address
│   ├── test_message_flow.py
│   └── test_message_delivery_payload.py
└── .github/
    └── workflows/test.yml     # GitHub Actions CI configuration
```

---

## Getting Started

1. **Clone the repository:**

   ```bash
   git clone https://github.com/YOU/agent_post.git
   cd agent_post
   ```

2. **Set up the Python environment and install dependencies:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**  
   Create a `.env` file based on the template below:

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/agent_post
   EXTERNAL_API_TOKEN=your_token_here
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHANNEL_ID=your_channel_id
   CITY_API_URL=https://yourcityapi.example.com/api/agents/cities-data/
   ```

4. **Initialize the database:**

   ```bash
   python setup/install.py
   ```

5. **Run the Application or Cron Processing:**  
   To run the API:

   ```bash
   python app.py
   ```

   To process messages via the cron job or manually:

   ```bash
   python run_message_exchange.py
   ```

   You should see output similar to:

   ```
   🚀 Starting Agent Post message processing cron job...
   ✅ .env file loaded.
   🔄 Processing messages (fetching, saving, delivering)...
   ✅ Messages processed and delivered successfully.
   🎉 Agent Post message processing cron job completed.
   ```

---

## Running Tests

Agent Post includes a comprehensive suite of tests for unit and integration scenarios. For example, the tests cover:

- Message ingestion and flow
- Approval of multiple recipients while ignoring duplicate sender addresses
- Correct formatting and delivery of messages

To run all tests:

```bash
python run_tests.py
```

Or run specific tests via unittest:

```bash
python -m unittest tests/test_message_flow.py
```

---

## Features

- **Message Ingestion & Delivery:**  
  Process messages by fetching from outboxes and delivering them to destination inboxes.

- **Multi-Recipient Support:**  
  A message’s `to` field can specify multiple recipients via commas, semicolons, or spaces. The backend splits, trims, and deduplicates these to ensure messages are delivered once per recipient.

- **Self-Address Filtering:**  
  The service prevents an agent from sending a message to itself even if listed as a recipient more than once.

- **Robust APIs:**  
  Communicates with external agents through the ExternalAPI (for outbox collection and inbox delivery) and CityAPI (to resolve addresses).

- **CI/CD Ready:**  
  Configured for automated testing with GitHub Actions.

---

## External APIs

### CityAPI

- **Purpose:** Retrieve agent endpoints data.
- **Usage:**  
  The service queries `CityAPI` to obtain a mapping of agent names to their API URLs.

### ExternalAPI

- **Purpose:**  
  - **Collect Messages:** Fetch messages from remote agents’ outboxes.
  - **Deliver Messages:** Post messages to recipients’ inboxes.
- **Data Formats:**  
  The API accepts messages with fields such as "from", "to", "data", and "metadata", where the "to" field may include multiple addresses.

For more details on data formats and endpoints, please refer to the project documentation within the `src` folder.

---

## Telegram Integration

The service also includes a Telegram integration module (see `telegram_service.py`) to create posts in a Telegram channel. This integration uses environment variables (`TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHANNEL_ID`) for credentials.

---

## Acknowledgments

Thank you for using Agent Post. For any issues or improvements, please refer to the repository’s issue tracker or contribute via pull requests.