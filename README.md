Here’s a `README.md` tailored to your `agent_post` project, summarizing purpose, usage, setup, and testing:

---

## 📨 Agent Post – Message Processing Service

Agent Post is a Python-based message exchange microservice that:

* Fetches outbox messages from citizen endpoints.
* Stores them into a local SQL database.
* Delivers those messages to the intended recipients.
* Handles multi-recipient delivery.
* Automatically purges outdated messages.

Built using:

* Flask
* SQLAlchemy
* Alembic
* Unittest (with mocking)
* Docker-ready

---

### 📦 Project Structure

```bash
agent_post/
├── app.py                     # Simple Flask API
├── run_tests.py              # Unified test runner
├── requirements.txt          # All dependencies
├── setup/                    # Setup and teardown scripts
│   ├── install.py            # Initializes DB and inserts demo data
│   └── uninstall.py          # Destroys the database
├── src/                      # Main source code
│   ├── message.py
│   ├── message_repository.py
│   ├── message_service.py
│   ├── city_api.py
│   └── external_api.py
├── tests/                    # Unit and integration tests
│   ├── test_message.py
│   ├── test_message_repository.py
│   ├── test_message_service.py
│   ├── test_message_flow.py
│   ├── test_message_delivery_payload.py
│   └── ...
└── .github/
    └── workflows/test.yml   # GitHub Actions CI
```

---

### 🚀 Getting Started

1. **Clone the repo:**

   ```bash
   git clone https://github.com/YOU/agent_post.git
   cd agent_post
   ```

2. **Install Python & dependencies:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   Create `.env` file:

   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/agent_post
   ```

4. **Initialize the database:**

   ```bash
   python setup/install.py
   ```

5. **Run the app:**

   ```bash
   python app.py
   ```

---

### 🧪 Running Tests

To run all tests:

```bash
python run_tests.py
```

To run a specific test file:

```bash
python -m unittest tests.test_message_flow
```

---


### 🔁 Features

* Message ingestion from remote agents
* SQLAlchemy + Alembic migrations
* Full unit + integration test coverage
* Auto-delivery to multiple recipients
* Cleanup of old messages

---

### 🤖 CI/CD

All pushes and pull requests trigger:

* Unit testing via GitHub Actions
* Artifacts upload on failure

Check `.github/workflows/test.yml`.

Here’s an updated `README.md` section that documents how the `external_api` and `city_api` components work, including their data formats:

---

### 🛰️ External API and City API Interfaces

This project uses two main external interfaces:

---

Here is the updated `README.md` section with **examples for multiple recipients**, covering how `ExternalAPI` handles `to` fields with multiple addresses separated by `space`, `comma`, or `semicolon`:

---

### 🛰️ External API and City API Interfaces

This project uses two primary external interfaces to coordinate message passing between agents in a simulated smart city:

---

#### 🌆 `CityAPI`

**Class**: `src.city_api.CityAPI`

**Method**: `get_cities()`

**Purpose**: Retrieve cloud agent endpoints.

**Example Return**:

```json
{
  "city_name": "Loopland",
  "cloud_id": "cloud_test",
  "addresses": [
    { "citizen_1": "https://cloud.mock/loopland/api/v1/agent/1234/msg" },
    { "citizen_2": "https://cloud.mock/loopland/api/v1/agent/5678/msg" }
  ]
}
```

---

#### ✉️ `ExternalAPI`

**Class**: `src.external_api.ExternalAPI`

Handles:

* Pulling messages from the outbox of other agents
* Delivering messages to the inboxes of recipients

---

### 📤 `collect_from_outbox(url: str)`

* **Request**:
  `GET <url>?token=TOKEN&action=collect_from_outbox`

* **Example Response**:

```json
{
  "messages": [
    {
      "from": "citizen_1",
      "to": "citizen_2",
      "data": "Hello!",
      "metadata": {
        "created_at": "2025-06-26T17:51:36"
      }
    }
  ]
}
```

---

### 🧑‍🤝‍🧑 Multiple Recipients Support

The `to` field **can include multiple recipients** separated by:

* Commas: `"citizen_2,citizen_3"`
* Semicolons: `"citizen_2; citizen_3"`
* Spaces: `"citizen_2 citizen_3"`

**Example message with multiple recipients**:

```json
{
  "from": "citizen_1",
  "to": "citizen_2, citizen_3; citizen_4 citizen_5",
  "data": "Hello all!",
  "metadata": {
    "created_at": "2025-06-26T17:51:36"
  }
}
```

**Behavior**:

* The message is **split** and **delivered individually** to each recipient.
* The backend trims whitespace and deduplicates recipient URLs using data from the `CityAPI`.

---

### 📥 `add_to_inbox(url: str, message: Dict)`

* **Request**:
  `POST <url>?token=TOKEN&action=add_to_inbox`

* **Request Payload**:

```json
{
  "from": "citizen_1",
  "to": "citizen_2",
  "data": "Hello!",
  "metadata": {
    "created_at": "2025-06-26T17:51:36"
  }
}
```

If multiple recipients are specified, this call is made once per resolved recipient address.
