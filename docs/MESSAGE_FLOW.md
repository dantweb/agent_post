# Agent Post Service - Message Flow Documentation

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Production

---

## Table of Contents

1. [Overview](#overview)
2. [Complete Message Lifecycle](#complete-message-lifecycle)
3. [Message Collection Flow](#message-collection-flow)
4. [Message Delivery Flow](#message-delivery-flow)
5. [Multi-Recipient Handling](#multi-recipient-handling)
6. [Self-Loop Prevention](#self-loop-prevention)
7. [Error Handling](#error-handling)
8. [Sequence Diagrams](#sequence-diagrams)

---

## Overview

The Agent Post Service orchestrates inter-agent message exchange through a collect-store-deliver workflow:

1. **Collect:** Gather messages from all agent outboxes
2. **Store:** Persist messages to database
3. **Deliver:** Send messages to recipient inboxes

---

## Complete Message Lifecycle

### Phase 1: Message Creation

**Location:** Agent's filesystem at `/loops/{loop_id}/filesystem/agentlife/post/outbox/new/`

**Trigger:** Agent action (SEND_POST, MSG, or custom action)

**Example Message:**
```json
{
  "message_id": "msg_001",
  "from": "cityhall",
  "to": "padre, maria",
  "timestamp": "2025-11-16T14:30:00Z",
  "subject": "Project Status",
  "body": "Need update on backend API development",
  "priority": "high",
  "type": "status_request",
  "metadata": {
    "project": "marketplace_mvp",
    "requires_response": true
  }
}
```

### Phase 2: Message Collection

**Trigger:** Message exchange script execution
```bash
cd agent_post && docker compose exec -T agent_post python run_message_exchange.py
```

**Process:**

1. **Discover Agents**
   ```python
   cities_data = city_api.get_cities()
   # Returns agent configurations
   ```

2. **Build Address Map**
   ```python
   addresses_dict = message_service.get_agent_addresses(cities_data)
   # {"cityhall": "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/", ...}
   ```

3. **Collect From Each Agent**
   ```python
   for agent_name, url in addresses_dict.items():
       messages_data = external_api.collect_from_outbox(url)
   ```

**WAKEUP Action Flow:**

```
1. POST /api/public/agent/{id}/action/WAKEUP/
   → Returns: {"execution_id": "uuid", "success": true}

2. Poll GET /api/public/agent/{id}/action/WAKEUP/execution/{execution_id}/
   → Wait until {"execution": {"status": "completed"}}

3. Extract messages from response:
   {
     "execution": {
       "result": {
         "updated_files": [
           {
             "path": "msg_001.json",
             "file_content": {
               "message": {
                 "from": "cityhall",
                 "to": "padre, maria",
                 "data": "Message content"
               }
             }
           }
         ]
       }
     }
   }

4. Parse message data and create Message objects
```

**File System Effect:**

Message moved from `outbox/new/` to `outbox/sent/`:
```bash
# Before WAKEUP
/loops/71/filesystem/agentlife/post/outbox/new/msg_001.json

# After WAKEUP
/loops/71/filesystem/agentlife/post/outbox/sent/msg_001.json
```

### Phase 3: Message Storage

**Process:**
```python
for msg in messages_data:
    message_repo.save(msg)
```

**Database Record:**
```sql
INSERT INTO messages (id, from_address, to_address, data, created_at)
VALUES ('uuid', 'cityhall', 'padre, maria', 'Message content', '2025-11-16 14:30:00');
```

**Purpose:**
- Persistent message history
- Audit trail
- Recovery mechanism
- Query capability

### Phase 4: Message Delivery

**Recipient Parsing:**
```python
msg.address_list  # ["padre", "maria"]
```

**Delivery Loop:**
```python
for recipient in set(msg.address_list):
    if recipient != msg.from_address:  # Self-loop prevention
        recipient_url = addresses_dict.get(recipient)
        if recipient_url:
            recipient_url = recipient_url.replace("WAKEUP", "RECEIVE_POST")

            # Build payload
            msg_dict = {"message": msg.to_json()}
            blob = {
                "updated_files": [{
                    "path": f"{msg.id}.json",
                    "file_content": msg_dict
                }]
            }

            # Deliver
            response = external_api.add_to_inbox(recipient_url, blob)
```

**RECEIVE_POST Action:**

```
POST /api/public/agent/10/action/RECEIVE_POST/
Content-Type: application/json

{
  "updated_files": [{
    "path": "uuid.json",
    "file_content": {
      "message": {
        "id": "uuid",
        "from_address": "cityhall",
        "to_address": "padre, maria",
        "data": "Message content",
        "created_at": "2025-11-16T14:30:00"
      }
    }
  }]
}
```

**File System Effect:**

Message created in recipient's `inbox/new/`:
```bash
# padre receives
/loops/72/filesystem/agentlife/post/inbox/new/uuid.json

# maria receives
/loops/73/filesystem/agentlife/post/inbox/new/uuid.json
```

**VERIFIED:** Direct curl test confirmed files are created in `inbox/new/`

### Phase 5: Message Reading (Living Agent)

**Trigger:** READ_POSTS action (first action in daily cycle)

**Expected Process:**
```python
# Read messages from inbox/new/
messages = glob("inbox/new/*.json")

# Process each message
for msg_file in messages:
    msg_data = read_json(msg_file)

    # Create task based on message
    create_task(msg_data)

    # Move to inbox/read/
    move(msg_file, "inbox/read/")
```

**Current Status:** ISSUE - READ_POSTS/RECEIVE_POST not generating file operations

---

## Message Collection Flow

### Detailed WAKEUP Process

**Step 1: Initiate WAKEUP**

```python
url = "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/"
response = requests.post(url)
```

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

**Step 2: Poll Execution Status**

```python
execution_url = f"{url}execution/{execution_id}/"

while True:
    execution_response = requests.get(execution_url)
    raw_bc = BroadcastData(execution_response.json())

    if raw_bc['execution']['status'] != 'running':
        break

    sleep(3)  # Wait 3 seconds before next poll
```

**Response During Execution:**
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

**Response When Complete:**
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

**Step 3: Extract Messages**

```python
bc = BroadcastData(execution_response.json())
file_entries = bc.find_value_recursive_by_key('updated_files')

messages = []
for entry in file_entries:
    msg_data = self._extract_message_data(entry)
    if msg_data:
        message = Message(
            id=msg_data.get('id'),
            from_address=msg_data.get('from_address', msg_data.get('from')),
            to_address=msg_data.get('to_address', msg_data.get('to')),
            data=msg_data.get('data')
        )
        messages.append(message)
```

### Message Extraction Logic

The `_extract_message_data()` method handles multiple format variations:

**Format 1: Direct message in file_content**
```json
{
  "path": "msg.json",
  "file_content": {
    "message": {
      "from": "cityhall",
      "to": "padre",
      "data": "content"
    }
  }
}
```

**Format 2: Nested message object**
```json
{
  "path": "msg.json",
  "file_content": {
    "from": "cityhall",
    "to": "padre",
    "data": "content"
  }
}
```

**Format 3: JSON string in file_content**
```json
{
  "path": "msg.json",
  "file_content": "{\"message\": {\"from\": \"cityhall\", \"to\": \"padre\", \"data\": \"content\"}}"
}
```

**Extraction Algorithm:**

```python
def _extract_message_data(self, file_entry):
    file_content = file_entry.get('file_content')

    # Handle string JSON
    if isinstance(file_content, str):
        file_content = json.loads(file_content)

    # Check for nested 'message' key
    if 'message' in file_content:
        msg_data = file_content['message']
    else:
        msg_data = file_content

    # Validate required fields
    if 'from' in msg_data or 'from_address' in msg_data:
        return msg_data

    return None
```

**CURRENT ISSUE:** Extraction returns `msg_data = None` for test messages

---

## Message Delivery Flow

### Single Recipient Delivery

**Input:**
```python
message = Message(
    from_address='cityhall',
    to_address='padre',
    data='Status update'
)
```

**Process:**

1. **Get recipient URL**
   ```python
   recipient_url = addresses_dict['padre']
   # "http://loopai_web:5000/api/public/agent/10/action/WAKEUP/"
   ```

2. **Convert to RECEIVE_POST endpoint**
   ```python
   recipient_url = recipient_url.replace("WAKEUP", "RECEIVE_POST")
   # "http://loopai_web:5000/api/public/agent/10/action/RECEIVE_POST/"
   ```

3. **Build payload**
   ```python
   payload = {
       "updated_files": [{
           "path": f"{message.id}.json",
           "file_content": {
               "message": {
                   "id": message.id,
                   "from_address": message.from_address,
                   "to_address": message.to_address,
                   "data": message.data,
                   "created_at": message.created_at.isoformat()
               }
           }
       }]
   }
   ```

4. **POST to RECEIVE_POST**
   ```python
   response = requests.post(recipient_url, json=payload)
   ```

5. **Response**
   ```json
   {
     "success": true,
     "execution_id": "uuid",
     "message": "Action execution started"
   }
   ```

6. **File created in filesystem**
   ```bash
   /loops/72/filesystem/agentlife/post/inbox/new/uuid.json
   ```

### Multi-Recipient Delivery

**Input:**
```python
message = Message(
    from_address='cityhall',
    to_address='padre, maria, zhou',
    data='Team update'
)
```

**Address Parsing:**
```python
message.address_list  # ["padre", "maria", "zhou"]
```

**Delivery Loop:**
```python
for recipient in set(message.address_list):
    # Skip self-addressing
    if recipient == message.from_address:
        continue

    # Get recipient URL
    recipient_url = addresses_dict.get(recipient)
    if not recipient_url:
        print(f"Warning: No URL found for {recipient}")
        continue

    # Deliver message
    recipient_url = recipient_url.replace("WAKEUP", "RECEIVE_POST")
    payload = build_payload(message)
    response = external_api.add_to_inbox(recipient_url, payload)
```

**Result:**

Three separate deliveries:
```bash
# padre receives
/loops/72/filesystem/agentlife/post/inbox/new/uuid.json

# maria receives
/loops/73/filesystem/agentlife/post/inbox/new/uuid.json

# zhou receives
/loops/74/filesystem/agentlife/post/inbox/new/uuid.json
```

---

## Multi-Recipient Handling

### Address Parsing

**Supported Delimiters:**
- Comma: `"padre, maria, zhou"`
- Semicolon: `"padre; maria; zhou"`
- Space: `"padre maria zhou"`
- Mixed: `"padre, maria; zhou"` (normalized to space-separated)

**Parsing Logic:**
```python
@property
def address_list(self) -> List[str]:
    to_list = [self.to_address]

    for delim in [';', ',', ' ']:
        if delim in self.to_address:
            # Replace all delimiters with space
            normalized = self.to_address.replace(';', ' ').replace(',', ' ')
            # Split and strip whitespace
            to_list = [addr.strip() for addr in normalized.split()]
            break

    return to_list
```

**Examples:**

```python
# Comma-separated
msg = Message(to_address="padre, maria, zhou")
msg.address_list  # ["padre", "maria", "zhou"]

# Semicolon-separated
msg = Message(to_address="padre; maria; zhou")
msg.address_list  # ["padre", "maria", "zhou"]

# Space-separated
msg = Message(to_address="padre maria zhou")
msg.address_list  # ["padre", "maria", "zhou"]

# Single recipient
msg = Message(to_address="padre")
msg.address_list  # ["padre"]
```

### Deduplication

**Problem:** Multiple recipients might include duplicates

**Solution:** Use `set()` to deduplicate

```python
for recipient in set(msg.address_list):
    # Ensures each recipient receives message only once
    deliver_to_recipient(recipient, msg)
```

**Example:**
```python
msg = Message(to_address="padre, maria, padre, zhou, maria")
set(msg.address_list)  # {"padre", "maria", "zhou"}
```

---

## Self-Loop Prevention

### Problem

Agent sending message to itself creates infinite loop:

```
cityhall → cityhall
   ↓
RECEIVE_POST creates message in inbox
   ↓
READ_POSTS reads message
   ↓
Agent responds by sending another message
   ↓
INFINITE LOOP
```

### Solution

**Filter self-addressing during delivery:**

```python
for recipient in set(msg.address_list):
    if recipient != msg.from_address:  # Self-loop prevention
        deliver_to_recipient(recipient, msg)
    else:
        print(f"Skipping self-delivery: {msg.from_address} → {recipient}")
```

### Examples

**Case 1: Explicit self-addressing**
```python
msg = Message(from_address="cityhall", to_address="cityhall, padre")
# Delivers to: padre only
# Skips: cityhall
```

**Case 2: Multi-recipient with self**
```python
msg = Message(from_address="cityhall", to_address="cityhall, padre, maria")
# Delivers to: padre, maria
# Skips: cityhall
```

**Case 3: Only self**
```python
msg = Message(from_address="cityhall", to_address="cityhall")
# Delivers to: none
# Skips: cityhall
# Result: Message stored in DB but not delivered
```

---

## Error Handling

### Network Errors

**Scenario:** LoopAI web service unreachable

**Handling:**
```python
try:
    response = requests.post(url)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
    # Log error
    # Continue with next agent/recipient
```

**Recovery:** Message persists in database for manual retry

### Extraction Errors

**Scenario:** Message format doesn't match expected structure

**Handling:**
```python
msg_data = self._extract_message_data(entry)
if msg_data is None:
    print(f"Warning: Could not extract message from {entry}")
    continue  # Skip this entry
```

**Current Issue:** Test messages returning `msg_data = None`

### Delivery Errors

**Scenario:** RECEIVE_POST action fails

**Handling:**
```python
try:
    response = external_api.add_to_inbox(recipient_url, payload)
    if not response.get('success'):
        print(f"Delivery failed to {recipient}: {response}")
except Exception as e:
    print(f"Error delivering to {recipient}: {e}")
```

**Recovery:** Failed deliveries logged for manual investigation

### Execution Timeout

**Scenario:** WAKEUP execution never completes

**Current:** Infinite polling loop (ISSUE)

**Recommended:**
```python
timeout = 60  # seconds
start_time = time.time()

while True:
    if time.time() - start_time > timeout:
        raise TimeoutError(f"Execution {execution_id} timed out")

    execution_response = requests.get(execution_url)
    if execution_response.json()['execution']['status'] != 'running':
        break

    sleep(3)
```

---

## Sequence Diagrams

### Complete Message Flow

```
Agent (Sender)                Message Exchange                LoopAI Web                Agent (Recipient)
     │                              │                              │                            │
     │ 1. Create message            │                              │                            │
     │    in outbox/new/            │                              │                            │
     │─────────────────────────────►│                              │                            │
     │                              │                              │                            │
     │                              │ 2. POST WAKEUP               │                            │
     │                              │─────────────────────────────►│                            │
     │                              │                              │                            │
     │                              │ 3. Return execution_id       │                            │
     │                              │◄─────────────────────────────│                            │
     │                              │                              │                            │
     │                              │ 4. Poll execution status     │                            │
     │                              │─────────────────────────────►│                            │
     │                              │                              │ 5. Run WAKEUP action       │
     │                              │                              │    - Read outbox/new/      │
     │                              │                              │    - Move to outbox/sent/  │
     │                              │                              │    - Return updated_files  │
     │                              │                              │                            │
     │                              │ 6. Return result with        │                            │
     │                              │    updated_files             │                            │
     │                              │◄─────────────────────────────│                            │
     │                              │                              │                            │
     │                              │ 7. Extract message data      │                            │
     │                              │ 8. Save to database          │                            │
     │                              │                              │                            │
     │                              │ 9. POST RECEIVE_POST         │                            │
     │                              │    with message payload      │                            │
     │                              │─────────────────────────────►│                            │
     │                              │                              │                            │
     │                              │10. Return execution_id       │                            │
     │                              │◄─────────────────────────────│                            │
     │                              │                              │ 11. Run RECEIVE_POST       │
     │                              │                              │     - Write to inbox/new/  │
     │                              │                              │────────────────────────────►│
     │                              │                              │                            │
     │                              │                              │                            │ 12. Message available
     │                              │                              │                            │     in inbox/new/
```

### WAKEUP Action Detail

```
Message Exchange          LoopAI Web                 Filesystem
     │                         │                          │
     │ POST WAKEUP             │                          │
     │────────────────────────►│                          │
     │                         │                          │
     │ execution_id            │                          │
     │◄────────────────────────│                          │
     │                         │                          │
     │ Poll status (loop)      │                          │
     │────────────────────────►│                          │
     │                         │                          │
     │ status: running         │                          │
     │◄────────────────────────│                          │
     │                         │                          │
     │ wait 3 seconds          │                          │
     │                         │                          │
     │ Poll status             │                          │
     │────────────────────────►│                          │
     │                         │ Read outbox/new/         │
     │                         │─────────────────────────►│
     │                         │                          │
     │                         │ Message files            │
     │                         │◄─────────────────────────│
     │                         │                          │
     │                         │ Move to outbox/sent/     │
     │                         │─────────────────────────►│
     │                         │                          │
     │ status: completed       │                          │
     │ updated_files: [...]    │                          │
     │◄────────────────────────│                          │
     │                         │                          │
```

### RECEIVE_POST Action Detail

```
Message Exchange          LoopAI Web                 Filesystem
     │                         │                          │
     │ POST RECEIVE_POST       │                          │
     │ with payload            │                          │
     │────────────────────────►│                          │
     │                         │                          │
     │ execution_id            │                          │
     │◄────────────────────────│                          │
     │                         │                          │
     │ (async execution)       │ Write to inbox/new/      │
     │                         │─────────────────────────►│
     │                         │                          │
     │                         │ File created             │
     │                         │◄─────────────────────────│
     │                         │                          │
     │                         │ Update execution status  │
     │                         │                          │
```

**VERIFIED:** RECEIVE_POST successfully creates files in `inbox/new/` directory

---

## Performance Characteristics

### Timing Breakdown

**Per Agent Collection:**
- POST WAKEUP: ~200ms
- Execution time: 1-3 seconds (depends on outbox size)
- Polling overhead: 3 seconds per poll × N polls
- Total: ~5-10 seconds per agent

**Per Message Delivery:**
- Parse recipients: <1ms
- POST RECEIVE_POST: ~200ms per recipient
- Total: ~200ms × number of recipients

**For 5 Agents with 10 Total Messages:**
- Collection: 5 agents × 7 seconds = 35 seconds
- Delivery: 10 messages × 2 recipients avg × 0.2s = 4 seconds
- Database: 10 inserts × 10ms = 100ms
- **Total: ~40 seconds**

### Optimization Opportunities

1. **Parallel Collection:** Use asyncio to collect from all agents simultaneously
   - Current: 35 seconds for 5 agents
   - With async: ~7 seconds (single longest agent)

2. **Adaptive Polling:** Exponential backoff for execution polling
   - Current: Fixed 3-second intervals
   - With backoff: 0.5s, 1s, 2s, 3s, 3s...

3. **Batch Delivery:** Group deliveries to same agent
   - Current: One POST per message per recipient
   - With batching: One POST with multiple messages

4. **Database Batching:** Insert messages in bulk
   - Current: One INSERT per message
   - With batching: Bulk INSERT for all messages

---

## Troubleshooting

### Message Not Collected

**Symptoms:** Message in `outbox/new/` but not moved to `outbox/sent/`

**Possible Causes:**
1. WAKEUP action not finding message
2. Message file format invalid
3. Filesystem permissions issue

**Debugging:**
```bash
# Check if message is readable
cat /loops/{loop_id}/filesystem/agentlife/post/outbox/new/message.json

# Check WAKEUP logs
docker logs loopai_web | grep WAKEUP

# Run manual WAKEUP
curl -X POST http://localhost:5050/api/public/agent/{id}/action/WAKEUP/
```

### Message Collected But Not Delivered

**Symptoms:** Message in `outbox/sent/` but not in recipient's `inbox/new/`

**Possible Causes:**
1. Message extraction returning None (CURRENT ISSUE)
2. Recipient address not found in cities data
3. RECEIVE_POST action failing
4. Self-loop prevention filtering recipient

**Debugging:**
```bash
# Check message exchange logs
docker exec agent_post python run_message_exchange.py

# Look for:
# "msg_data = None" → extraction failure
# "No URL found for {recipient}" → address mapping issue
# "Skipping self-delivery" → self-loop prevention active
```

### Message Delivered But Not Read

**Symptoms:** Message in recipient's `inbox/new/` but not moved to `inbox/read/`

**Possible Causes:**
1. READ_POSTS action not running
2. READ_POSTS not generating file operations (CURRENT ISSUE)
3. Message format not recognized by READ_POSTS

**Debugging:**
```bash
# Check if READ_POSTS runs
curl -X POST http://localhost:5050/api/public/agent/{id}/action/READ_POSTS/

# Check logs for IndexError
docker logs loopai_web | grep "IndexError: list index out of range"

# Manually check inbox
ls -lh /loops/{loop_id}/filesystem/agentlife/post/inbox/new/
```

---

## References

- **Architecture:** `/agent_post/docs/ARCHITECTURE.md`
- **API Reference:** `/agent_post/docs/API_REFERENCE.md`
- **Testing Guide:** `/agent_post/docs/TESTING_GUIDE.md`
- **Test Results:** `/docs/new_agents/implementation/MESSAGE_EXCHANGE_TEST_RESULTS.md`
- **Source Code:** `/agent_post/src/message_service.py`, `/agent_post/src/external_api.py`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Maintainer:** LoopAI Implementation Team
