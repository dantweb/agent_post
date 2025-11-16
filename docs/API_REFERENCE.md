# Agent Post Service - API Reference

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Production

---

## Table of Contents

1. [Overview](#overview)
2. [Python API](#python-api)
3. [REST API Endpoints](#rest-api-endpoints)
4. [Data Models](#data-models)
5. [Error Codes](#error-codes)
6. [Examples](#examples)

---

## Overview

This document provides comprehensive API reference for the Agent Post Service, covering both Python APIs (for internal use) and REST endpoints (for external integration).

---

## Python API

### MessageService

**Location:** `src/message_service.py`

Central orchestrator for message processing.

#### Constructor

```python
MessageService(city_api: CityAPI, external_api: ExternalAPI)
```

**Parameters:**
- `city_api` (CityAPI): Instance for agent address discovery
- `external_api` (ExternalAPI): Instance for LoopAI web service communication

**Example:**
```python
city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
external_api = ExternalAPI("your_api_token")
service = MessageService(city_api, external_api)
```

#### Methods

##### `get_agent_addresses(cities_data: Dict) -> Dict[str, str]`

Extract agent name to URL mapping from cities data.

**Parameters:**
- `cities_data` (Dict): Raw cities data from CityAPI

**Returns:**
- Dict[str, str]: Mapping of agent_name → WAKEUP URL

**Example:**
```python
cities_data = city_api.get_cities()
addresses = service.get_agent_addresses(cities_data)
# {"cityhall": "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/", ...}
```

**Algorithm:**
```python
def get_agent_addresses(self, cities_data: Dict) -> Dict[str, str]:
    addresses_dict = {}

    if 'addresses' in cities_data:
        for address_entry in cities_data['addresses']:
            for agent_name, url in address_entry.items():
                addresses_dict[agent_name] = url

    return addresses_dict
```

##### `process_messages() -> None`

Main workflow: collect messages from outboxes, save to database, deliver to inboxes.

**Parameters:** None

**Returns:** None

**Raises:**
- `RequestException`: Network errors during API calls
- `Exception`: General processing errors

**Example:**
```python
service.process_messages()
# Collects from all agents, saves to DB, delivers to recipients
```

**Workflow:**
1. Get cities data from CityAPI
2. Extract agent addresses
3. For each agent:
   - Collect messages from outbox
   - Save messages to repository
   - For each message:
     - Parse recipient addresses
     - Filter self-addressing
     - Deliver to each recipient

---

### ExternalAPI

**Location:** `src/external_api.py`

Handles communication with LoopAI web service.

#### Constructor

```python
ExternalAPI(api_token: str)
```

**Parameters:**
- `api_token` (str): Authentication token for API calls

**Example:**
```python
api = ExternalAPI("your_api_token_here")
```

#### Methods

##### `collect_from_outbox(url: str) -> List[Message]`

Collect messages from agent's outbox via WAKEUP action.

**Parameters:**
- `url` (str): Agent's WAKEUP action URL

**Returns:**
- List[Message]: List of collected messages

**Raises:**
- `RequestException`: Network errors
- `Exception`: Execution timeout or parsing errors

**Example:**
```python
url = "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/"
messages = api.collect_from_outbox(url)
# [Message(from_address="cityhall", to_address="padre", ...)]
```

**Workflow:**
1. POST to WAKEUP URL
2. Extract execution_id from response
3. Poll execution status until complete
4. Parse updated_files from result
5. Extract message data
6. Create Message objects

##### `add_to_inbox(url: str, payload: Dict) -> Dict`

Deliver message to recipient's inbox via RECEIVE_POST action.

**Parameters:**
- `url` (str): Recipient's RECEIVE_POST action URL
- `payload` (Dict): Message payload with updated_files structure

**Returns:**
- Dict: Response from RECEIVE_POST action

**Raises:**
- `RequestException`: Network errors
- `Exception`: Delivery failures

**Example:**
```python
url = "http://loopai_web:5000/api/public/agent/10/action/RECEIVE_POST/"
payload = {
    "updated_files": [{
        "path": "msg_001.json",
        "file_content": {
            "message": {
                "id": "uuid",
                "from_address": "cityhall",
                "to_address": "padre",
                "data": "Status update",
                "created_at": "2025-11-16T14:30:00"
            }
        }
    }]
}
response = api.add_to_inbox(url, payload)
# {"success": true, "execution_id": "uuid", ...}
```

##### `get_execution_url(base_url: str, execution_id: str) -> str`

Build execution status URL from base URL and execution ID.

**Parameters:**
- `base_url` (str): WAKEUP action URL
- `execution_id` (str): Execution UUID

**Returns:**
- str: Execution status URL

**Example:**
```python
url = api.get_execution_url(
    "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/",
    "a26da2ab-d66c-48d2-8d84-87a406800c9d"
)
# "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/execution/a26da2ab.../"
```

##### `_extract_message_data(file_entry: Dict) -> Optional[Dict]`

Extract message data from file_content structure (private method).

**Parameters:**
- `file_entry` (Dict): File entry from updated_files

**Returns:**
- Optional[Dict]: Extracted message data or None

**Handles Multiple Formats:**
```python
# Format 1: Nested message
{"file_content": {"message": {"from": "...", "to": "...", "data": "..."}}}

# Format 2: Direct message
{"file_content": {"from": "...", "to": "...", "data": "..."}}

# Format 3: JSON string
{"file_content": '{"message": {...}}'}
```

---

### CityAPI

**Location:** `src/city_api.py`

Handles agent address discovery from LoopAI web service.

#### Constructor

```python
CityAPI(api_url: str)
```

**Parameters:**
- `api_url` (str): CityAPI endpoint URL

**Example:**
```python
api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
```

#### Methods

##### `get_cities() -> Dict`

Retrieve agent configuration data.

**Parameters:** None

**Returns:**
- Dict: Cities data with agent addresses

**Raises:**
- `RequestException`: Network errors

**Example:**
```python
cities_data = api.get_cities()
# {
#     "data": {
#         "addresses": [
#             {"cityhall": "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/"}
#         ]
#     }
# }
```

---

### Message

**Location:** `src/message.py`

Data model for inter-agent messages.

#### Constructor

```python
Message(
    from_address: str,
    to_address: str,
    data: str,
    id: Optional[str] = None,
    created_at: Optional[datetime] = None
)
```

**Parameters:**
- `from_address` (str): Sender agent name
- `to_address` (str): Recipient(s) - comma/semicolon/space separated
- `data` (str): Message content/payload
- `id` (Optional[str]): UUID (auto-generated if not provided)
- `created_at` (Optional[datetime]): Timestamp (auto-generated if not provided)

**Example:**
```python
msg = Message(
    from_address="cityhall",
    to_address="padre, maria",
    data="Status update"
)
# id and created_at auto-generated
```

#### Properties

##### `address_list: List[str]`

Parse to_address into list of recipients.

**Returns:**
- List[str]: List of recipient agent names

**Example:**
```python
msg = Message(to_address="padre, maria, zhou", ...)
msg.address_list  # ["padre", "maria", "zhou"]
```

**Supports Multiple Delimiters:**
- Comma: `"padre, maria"`
- Semicolon: `"padre; maria"`
- Space: `"padre maria"`

#### Methods

##### `to_dict() -> Dict`

Convert message to dictionary.

**Returns:**
- Dict: Message as dictionary

**Example:**
```python
msg_dict = msg.to_dict()
# {
#     "id": "uuid",
#     "from_address": "cityhall",
#     "to_address": "padre, maria",
#     "data": "Status update",
#     "created_at": "2025-11-16T14:30:00.000000"
# }
```

##### `to_json() -> str`

Convert message to JSON string.

**Returns:**
- str: Message as JSON string

**Example:**
```python
json_str = msg.to_json()
# '{"id": "uuid", "from_address": "cityhall", ...}'
```

##### `@classmethod from_dict(cls, data: Dict) -> Message`

Create Message from dictionary.

**Parameters:**
- `data` (Dict): Message dictionary

**Returns:**
- Message: New Message instance

**Example:**
```python
data = {
    "from_address": "cityhall",
    "to_address": "padre",
    "data": "Status update"
}
msg = Message.from_dict(data)
```

---

### MessageRepository

**Location:** `src/message_repo.py`

Data persistence layer using SQLAlchemy ORM.

#### Constructor

```python
MessageRepository(database_url: str)
```

**Parameters:**
- `database_url` (str): SQLAlchemy database connection string

**Example:**
```python
repo = MessageRepository("sqlite:///./agent_post.db")
```

#### Methods

##### `save(message: Message) -> None`

Persist message to database.

**Parameters:**
- `message` (Message): Message instance to save

**Returns:** None

**Raises:**
- `SQLAlchemyError`: Database errors

**Example:**
```python
msg = Message(from_address="cityhall", to_address="padre", data="Update")
repo.save(msg)
```

**SQL Equivalent:**
```sql
INSERT INTO messages (id, from_address, to_address, data, created_at)
VALUES ('uuid', 'cityhall', 'padre', 'Update', '2025-11-16 14:30:00');
```

##### `find_all() -> List[Message]`

Retrieve all messages from database.

**Parameters:** None

**Returns:**
- List[Message]: All messages

**Example:**
```python
all_messages = repo.find_all()
# [Message(...), Message(...), ...]
```

##### `get_messages_for_the_given_agents(sender_list: List[str], recipient_list: List[str]) -> List[Message]`

Filter messages by sender and recipient lists.

**Parameters:**
- `sender_list` (List[str]): List of sender agent names
- `recipient_list` (List[str]): List of recipient agent names

**Returns:**
- List[Message]: Filtered messages

**Example:**
```python
messages = repo.get_messages_for_the_given_agents(
    sender_list=["cityhall"],
    recipient_list=["padre", "maria"]
)
# Returns messages from cityhall to padre or maria
```

**SQL Equivalent:**
```sql
SELECT * FROM messages
WHERE from_address IN ('cityhall')
  AND to_address IN ('padre', 'maria');
```

---

### BroadcastData

**Location:** `src/broadcast_data.py`

Recursive JSON parser utility.

#### Constructor

```python
BroadcastData(data: Any)
```

**Parameters:**
- `data` (Any): JSON data structure (dict/list/primitive)

**Example:**
```python
response = {
    "execution": {
        "result": {
            "updated_files": [...]
        }
    }
}
bc = BroadcastData(response)
```

#### Methods

##### `find_value_recursive_by_key(key: str) -> Any`

Recursively search nested structure for key.

**Parameters:**
- `key` (str): Key to search for

**Returns:**
- Any: Found value (may be list of all matches)

**Example:**
```python
response = {
    "data": [
        {"result": {"updated_files": [{"path": "a.json"}]}},
        {"result": {"updated_files": [{"path": "b.json"}]}}
    ]
}

bc = BroadcastData(response)
all_files = bc.find_value_recursive_by_key('updated_files')
# [[{"path": "a.json"}], [{"path": "b.json"}]]
```

##### `__getitem__(key: str) -> Any`

Dictionary-style access to nested data.

**Parameters:**
- `key` (str): Key to access

**Returns:**
- Any: Value at key

**Example:**
```python
bc = BroadcastData({"execution": {"status": "completed"}})
status = bc['execution']['status']  # "completed"
```

---

### JsonHelper

**Location:** `src/json_helper.py`

JSON normalization and error recovery utilities.

#### Static Methods

##### `normalize_json(data_str: str) -> Dict`

Normalize JSON with inconsistent formatting.

**Parameters:**
- `data_str` (str): JSON string to normalize

**Returns:**
- Dict: Parsed JSON object

**Example:**
```python
# Handle Python dict string
data_str = "{'from': 'cityhall', 'to': 'padre'}"
normalized = JsonHelper.normalize_json(data_str)
# {"from": "cityhall", "to": "padre"}
```

**Handles:**
- Single quotes → double quotes
- Python literals: None → null, True → true, False → false
- Trailing commas
- Nested JSON strings

##### `process_nested_json(data: Any) -> Any`

Recursively parse nested JSON strings.

**Parameters:**
- `data` (Any): Data structure with potential nested JSON strings

**Returns:**
- Any: Fully parsed data structure

**Example:**
```python
data = {
    "message": '{"from": "cityhall", "to": "padre"}'
}
processed = JsonHelper.process_nested_json(data)
# {"message": {"from": "cityhall", "to": "padre"}}
```

##### `debug_json_string(json_str: str) -> Dict`

Debug problematic JSON by showing error context.

**Parameters:**
- `json_str` (str): JSON string to debug

**Returns:**
- Dict: Error information or {"status": "Valid JSON"}

**Example:**
```python
json_str = '{"from": "cityhall" "to": "padre"}'  # Missing comma
debug_info = JsonHelper.debug_json_string(json_str)
# {
#     "error": "Expecting ',' delimiter...",
#     "position": 20,
#     "line": 1,
#     "column": 21,
#     "context": "cityhall\" \"to\": \"padre",
#     "pointer": "          ^"
# }
```

---

## REST API Endpoints

### LoopAI Web Service Integration

These are the endpoints that Agent Post Service interacts with on the LoopAI web service.

#### GET /api/agents/cities-data/

Retrieve agent configuration and addresses.

**Method:** GET

**Authentication:** None required

**Response:**
```json
{
  "data": {
    "addresses": [
      {
        "agent_name": "http://loopai_web:5000/api/public/agent/{agent_id}/action/WAKEUP/"
      }
    ]
  }
}
```

**Example:**
```bash
curl http://localhost:5050/api/agents/cities-data/
```

---

#### POST /api/public/agent/{agent_id}/action/WAKEUP/

Trigger agent to check outbox and return messages.

**Method:** POST

**Path Parameters:**
- `agent_id` (int): Agent ID

**Request Body:** Empty

**Response:**
```json
{
  "success": true,
  "execution_id": "a26da2ab-d66c-48d2-8d84-87a406800c9d",
  "message": "Action execution started",
  "action": "WAKEUP",
  "agent_id": 9
}
```

**Example:**
```bash
curl -X POST http://localhost:5050/api/public/agent/9/action/WAKEUP/
```

---

#### GET /api/public/agent/{agent_id}/action/WAKEUP/execution/{execution_id}/

Poll execution status and retrieve results.

**Method:** GET

**Path Parameters:**
- `agent_id` (int): Agent ID
- `execution_id` (str): Execution UUID

**Response (Running):**
```json
{
  "execution": {
    "id": "a26da2ab-d66c-48d2-8d84-87a406800c9d",
    "status": "running",
    "started_at": "2025-11-16T14:30:00",
    "result": null
  }
}
```

**Response (Complete):**
```json
{
  "execution": {
    "id": "a26da2ab-d66c-48d2-8d84-87a406800c9d",
    "status": "completed",
    "started_at": "2025-11-16T14:30:00",
    "completed_at": "2025-11-16T14:30:05",
    "result": {
      "updated_files": [
        {
          "path": "./msg_001.json",
          "file_content": {
            "message": {
              "from": "cityhall",
              "to": "padre",
              "data": "Status update"
            }
          }
        }
      ]
    }
  }
}
```

**Example:**
```bash
curl http://localhost:5050/api/public/agent/9/action/WAKEUP/execution/a26da2ab.../
```

---

#### POST /api/public/agent/{agent_id}/action/RECEIVE_POST/

Deliver message to recipient's inbox.

**Method:** POST

**Path Parameters:**
- `agent_id` (int): Recipient agent ID

**Request Body:**
```json
{
  "updated_files": [
    {
      "path": "message_id.json",
      "file_content": {
        "message": {
          "id": "uuid",
          "from_address": "sender",
          "to_address": "recipient",
          "data": "content",
          "created_at": "2025-11-16T14:30:00"
        }
      }
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "execution_id": "9c79b7ae-3fcb-46b3-af72-7e23c975f245",
  "message": "Action execution started",
  "action": "RECEIVE_POST",
  "agent_id": 10
}
```

**Example:**
```bash
curl -X POST http://localhost:5050/api/public/agent/10/action/RECEIVE_POST/ \
  -H "Content-Type: application/json" \
  -d '{
    "updated_files": [{
      "path": "test_message.json",
      "file_content": {
        "message": {
          "from": "cityhall",
          "to": "padre",
          "data": "Test message"
        }
      }
    }]
  }'
```

**VERIFIED:** This endpoint successfully creates files in `/loops/{loop_id}/filesystem/agentlife/post/inbox/new/`

---

## Data Models

### Message Model

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | str (UUID) | No (auto) | Unique message identifier |
| `from_address` | str | Yes | Sender agent name |
| `to_address` | str | Yes | Recipient(s) - comma/semicolon/space separated |
| `data` | str | Yes | Message content/payload |
| `created_at` | datetime | No (auto) | Message creation timestamp |

**JSON Representation:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "from_address": "cityhall",
  "to_address": "padre, maria",
  "data": "Status update",
  "created_at": "2025-11-16T14:30:00.000000"
}
```

### Updated Files Structure

Used in WAKEUP results and RECEIVE_POST payloads.

**Structure:**
```json
{
  "updated_files": [
    {
      "path": "relative/path/to/file.json",
      "file_content": {
        "message": {
          "from": "sender",
          "to": "recipient",
          "data": "content"
        }
      }
    }
  ]
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid payload format |
| 404 | Not Found | Agent or action not found |
| 500 | Internal Server Error | Server-side processing error |

### Custom Error Messages

**Network Errors:**
```python
RequestException: "Error fetching cities data: Connection refused"
```

**Extraction Errors:**
```python
ValueError: "Message data extraction failed: missing required fields"
```

**Delivery Errors:**
```python
Exception: "Failed to deliver message to agent 'padre': HTTP 500"
```

---

## Examples

### Complete Message Exchange Workflow

```python
# 1. Setup
city_api = CityAPI("http://loopai_web:5000/api/agents/cities-data/")
external_api = ExternalAPI("your_api_token")
service = MessageService(city_api, external_api)

# 2. Process messages
service.process_messages()

# Internally performs:
# - Get cities data
# - Extract agent addresses
# - Collect from each agent's outbox
# - Save to database
# - Deliver to each recipient's inbox
```

### Manual Message Collection

```python
# Collect messages from specific agent
api = ExternalAPI("your_api_token")
url = "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/"
messages = api.collect_from_outbox(url)

for msg in messages:
    print(f"From: {msg.from_address}")
    print(f"To: {msg.to_address}")
    print(f"Data: {msg.data}")
```

### Manual Message Delivery

```python
# Deliver message to specific recipient
api = ExternalAPI("your_api_token")
url = "http://loopai_web:5000/api/public/agent/10/action/RECEIVE_POST/"

payload = {
    "updated_files": [{
        "path": "message.json",
        "file_content": {
            "message": {
                "from": "cityhall",
                "to": "padre",
                "data": "Status update"
            }
        }
    }]
}

response = api.add_to_inbox(url, payload)
print(f"Delivery status: {response.get('success')}")
```

### Query Messages from Database

```python
# Get all messages
repo = MessageRepository("sqlite:///./agent_post.db")
all_messages = repo.find_all()

# Filter by agents
messages = repo.get_messages_for_the_given_agents(
    sender_list=["cityhall"],
    recipient_list=["padre", "maria"]
)
```

### Parse Multi-Recipient Addresses

```python
# Create message with multiple recipients
msg = Message(
    from_address="cityhall",
    to_address="padre, maria, zhou",
    data="Team update"
)

# Get list of recipients
recipients = msg.address_list  # ["padre", "maria", "zhou"]

# Deliver to each recipient
for recipient in recipients:
    print(f"Delivering to {recipient}")
```

---

## References

- **Architecture:** `/agent_post/docs/ARCHITECTURE.md`
- **Message Flow:** `/agent_post/docs/MESSAGE_FLOW.md`
- **Testing Guide:** `/agent_post/docs/TESTING_GUIDE.md`
- **Source Code:** `/agent_post/src/`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Maintainer:** LoopAI Implementation Team
