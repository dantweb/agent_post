# Agent Post Service - Architecture Documentation

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Production

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Principles](#architecture-principles)
3. [Component Architecture](#component-architecture)
4. [Data Models](#data-models)
5. [Integration Points](#integration-points)
6. [Technology Stack](#technology-stack)
7. [Deployment Architecture](#deployment-architecture)

---

## System Overview

### Purpose

Agent Post is a **microservice for inter-agent message processing** within the LoopAI ecosystem. It acts as a centralized message broker that:

- Collects messages from agent outboxes
- Stores messages in a persistent repository
- Delivers messages to recipient agent inboxes
- Integrates with LoopAI's main application via API calls

### Design Philosophy

The system follows **Test-Driven Development (TDD)** principles with:
- Comprehensive unit tests for all components
- Integration tests for end-to-end message flow
- Mock-based testing for external dependencies
- Real API integration tests for validation

### Key Characteristics

- **Microservice Architecture:** Independent service communicating via REST APIs
- **Stateless Design:** No session state between requests
- **Asynchronous Processing:** Polls for message completion
- **Multi-Recipient Support:** Parses and delivers to multiple recipients
- **Self-Loop Prevention:** Filters out self-addressing to prevent message loops

---

## Architecture Principles

### 1. Separation of Concerns

Each component has a single, well-defined responsibility:

```
MessageService      → Orchestration & business logic
ExternalAPI         → LoopAI web service communication
CityAPI             → Agent address discovery
MessageRepository   → Data persistence
Message             → Data model & validation
```

### 2. Dependency Injection

Components receive dependencies through constructors, enabling:
- Easy testing with mocks
- Flexible configuration
- Clear dependency relationships

Example:
```python
class MessageService:
    def __init__(self, city_api: CityAPI, external_api: ExternalAPI):
        self.city_api = city_api
        self.external_api = external_api
```

### 3. Test-First Development

All features developed with TDD approach:
1. Write failing test
2. Implement minimal code to pass
3. Refactor while keeping tests green

Test coverage includes:
- Unit tests with mocked dependencies
- Integration tests with real APIs
- End-to-end delivery validation

### 4. Data Immutability

Message objects are immutable after creation:
- Created with `dataclass` decorator
- ID auto-generated on instantiation
- Timestamp frozen at creation time

---

## Component Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      LoopAI Web Service                      │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  Agent Loops   │  │  CityAPI       │  │  Filesystem  │  │
│  │  (70-74)       │  │  /cities-data  │  │  Adapter     │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└───────────┬──────────────────┬──────────────────┬───────────┘
            │                  │                  │
            │ WAKEUP/          │ GET              │ READ/WRITE
            │ RECEIVE_POST     │ cities-data      │ files
            │                  │                  │
┌───────────▼──────────────────▼──────────────────▼───────────┐
│                   Agent Post Service                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              MessageService (Orchestrator)            │   │
│  │  - Collect messages from outboxes                     │   │
│  │  - Save to repository                                 │   │
│  │  - Deliver to recipient inboxes                       │   │
│  └───┬─────────────┬──────────────────┬──────────────┬──┘   │
│      │             │                  │              │       │
│  ┌───▼────┐  ┌─────▼───────┐  ┌──────▼──────┐  ┌───▼────┐ │
│  │CityAPI │  │ ExternalAPI │  │   Message   │  │  Repo  │ │
│  │        │  │             │  │   Model     │  │        │ │
│  └────────┘  └─────────────┘  └─────────────┘  └────────┘ │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           SQLite Database (messages table)            │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. MessageService (src/message_service.py)

**Role:** Central orchestrator for message processing workflow

**Responsibilities:**
- Discover agent addresses from CityAPI
- Collect messages from all agent outboxes
- Save messages to repository
- Parse multi-recipient addresses
- Filter self-addressing
- Deliver messages to recipient inboxes

**Key Methods:**
```python
def get_agent_addresses(cities_data: Dict) -> Dict[str, str]:
    """Extract agent name → URL mapping from cities data"""

def process_messages() -> None:
    """Main workflow: collect → save → deliver"""
```

**Dependencies:**
- CityAPI: For agent address discovery
- ExternalAPI: For outbox/inbox communication
- MessageRepository: For persistence (implicit)

#### 2. ExternalAPI (src/external_api.py)

**Role:** Communication layer with LoopAI web service

**Responsibilities:**
- Call agent WAKEUP actions to collect outbox messages
- Poll execution status until completion
- Extract messages from nested response structures
- Deliver messages via RECEIVE_POST actions

**Key Methods:**
```python
def collect_from_outbox(url: str) -> List[Message]:
    """
    1. POST to WAKEUP action
    2. Poll execution until complete
    3. Parse updated_files from response
    4. Extract message data
    5. Return Message objects
    """

def add_to_inbox(url: str, payload: Dict) -> bool:
    """
    POST message to recipient's RECEIVE_POST action
    Payload format: {"updated_files": [{"path": "...", "file_content": {...}}]}
    """
```

**Complex Extraction Logic:**

The `_extract_message_data()` method handles multiple message format variations:

```python
# Format 1: Direct message object
{"from": "sender", "to": "recipient", "data": "content"}

# Format 2: Nested in file_content
{"file_content": {"message": {"from": "...", "to": "...", "data": "..."}}}

# Format 3: JSON string in file_content
{"file_content": '{"message": {"from": "...", "to": "...", "data": "..."}}'}
```

#### 3. CityAPI (src/city_api.py)

**Role:** Agent address discovery service

**Responsibilities:**
- Fetch agent configuration from LoopAI web service
- Parse cities data structure
- Provide agent metadata

**Key Methods:**
```python
def get_cities() -> Dict:
    """
    GET /api/agents/cities-data/
    Returns: {"data": {...agent configurations...}}
    """
```

**Data Structure:**
```json
{
  "data": {
    "addresses": [
      {"agent1": "http://loopai_web:5000/api/public/agent/8/action/WAKEUP/"},
      {"agent2": "http://loopai_web:5000/api/public/agent/9/action/WAKEUP/"}
    ]
  }
}
```

#### 4. Message (src/message.py)

**Role:** Data model representing inter-agent messages

**Attributes:**
```python
@dataclass
class Message:
    from_address: str              # Sender agent name
    to_address: str                # Recipient(s) - comma/semicolon/space separated
    data: str                      # Message content/payload
    id: Optional[str] = None       # UUID auto-generated
    created_at: Optional[datetime] # Timestamp auto-generated
```

**Key Properties:**
```python
@property
def address_list(self) -> List[str]:
    """
    Parse to_address into list of recipients
    Supports: "agent1, agent2" or "agent1; agent2" or "agent1 agent2"
    """
```

**Methods:**
```python
def to_dict() -> Dict:
    """Convert to dictionary for JSON serialization"""

def to_json() -> str:
    """Convert to JSON string"""

@classmethod
def from_dict(cls, data: Dict) -> Message:
    """Create Message from dictionary"""
```

#### 5. MessageRepository (src/message_repo.py)

**Role:** Data persistence layer using SQLAlchemy ORM

**Database Schema:**
```sql
CREATE TABLE messages (
    id VARCHAR PRIMARY KEY,
    from_address VARCHAR NOT NULL,
    to_address VARCHAR NOT NULL,
    data TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

**Key Methods:**
```python
def save(message: Message) -> None:
    """Persist message to database"""

def find_all() -> List[Message]:
    """Retrieve all messages"""

def get_messages_for_the_given_agents(
    sender_list: List[str],
    recipient_list: List[str]
) -> List[Message]:
    """Filter messages by sender/recipient"""
```

#### 6. BroadcastData (src/broadcast_data.py)

**Role:** Recursive JSON parser utility

**Purpose:** Navigate complex nested response structures from LoopAI API

**Key Methods:**
```python
def find_value_recursive_by_key(key: str) -> Any:
    """
    Recursively search nested dict/list structures for key
    Example: Find all 'updated_files' entries anywhere in response
    """
```

**Use Case:**
```python
response = {
    "data": [
        {"result": {"updated_files": []}},
        {"result": {"updated_files": [{"path": "...", "file_content": {...}}]}}
    ]
}

bc = BroadcastData(response)
all_updated_files = bc.find_value_recursive_by_key('updated_files')
# Returns all 'updated_files' arrays found in nested structure
```

#### 7. JsonHelper (src/json_helper.py)

**Role:** JSON normalization and error recovery

**Purpose:** Handle inconsistent JSON formatting from various sources

**Key Methods:**
```python
def normalize_json(data_str: str) -> Dict:
    """
    Normalize JSON with inconsistent escaping
    Handles: double-serialized JSON, Python dict strings, trailing commas
    """

def process_nested_json(data: Any) -> Any:
    """
    Recursively parse nested JSON strings in data structures
    """

def debug_json_string(json_str: str) -> Dict:
    """
    Debug problematic JSON by showing context around error position
    """
```

**Error Recovery Strategies:**
1. Try standard json.loads()
2. Try ast.literal_eval() for Python dict strings
3. Fix common issues: single quotes → double quotes
4. Fix Python literals: None → null, True → true, False → false
5. Remove trailing commas
6. Return detailed error info if all attempts fail

---

## Data Models

### Message Data Model

**Purpose:** Represent inter-agent messages with multi-recipient support

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from_address` | str | Yes | Sender agent name (e.g., "cityhall") |
| `to_address` | str | Yes | Recipient(s) - comma/semicolon/space separated |
| `data` | str | Yes | Message content/payload |
| `id` | str | No | UUID auto-generated if not provided |
| `created_at` | datetime | No | Timestamp auto-generated if not provided |

**Address Parsing Logic:**

```python
# Single recipient
to_address = "padre"
address_list = ["padre"]

# Multiple recipients (comma)
to_address = "padre, maria, zhou"
address_list = ["padre", "maria", "zhou"]

# Multiple recipients (semicolon)
to_address = "padre; maria; zhou"
address_list = ["padre", "maria", "zhou"]

# Multiple recipients (space)
to_address = "padre maria zhou"
address_list = ["padre", "maria", "zhou"]
```

**Validation Rules:**
- `from_address` cannot be empty
- `to_address` cannot be empty
- `data` can be empty string
- `id` must be valid UUID if provided
- `created_at` must be valid datetime if provided

**Serialization Formats:**

```python
# To Dictionary
message.to_dict()
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "from_address": "cityhall",
    "to_address": "padre, maria",
    "data": "Status update request",
    "created_at": "2025-11-16T14:30:00.000000"
}

# To JSON
message.to_json()
'{"id": "...", "from_address": "cityhall", ...}'
```

### Message Repository Model

**ORM Mapping:**

```python
class MessageModel(Base):
    __tablename__ = 'messages'

    id = Column(String, primary_key=True)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    data = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
```

**Indexes:**
- Primary key on `id`
- Consider adding indexes on `from_address`, `to_address` for query performance

---

## Integration Points

### 1. LoopAI Web Service Integration

**Base URL:** `http://loopai_web:5000`

**Endpoints Used:**

#### GET /api/agents/cities-data/

**Purpose:** Retrieve agent configuration and addresses

**Response:**
```json
{
  "data": {
    "addresses": [
      {"agent_name": "http://loopai_web:5000/api/public/agent/{id}/action/WAKEUP/"}
    ]
  }
}
```

#### POST /api/public/agent/{agent_id}/action/WAKEUP/

**Purpose:** Trigger agent to check outbox and return messages

**Request:** Empty body

**Response:**
```json
{
  "success": true,
  "execution_id": "uuid",
  "message": "Action execution started"
}
```

#### GET /api/public/agent/{agent_id}/action/WAKEUP/execution/{execution_id}/

**Purpose:** Poll execution status and retrieve results

**Response (Running):**
```json
{
  "execution": {
    "status": "running"
  }
}
```

**Response (Complete):**
```json
{
  "execution": {
    "status": "completed",
    "result": {
      "updated_files": [
        {
          "path": "message_id.json",
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
  }
}
```

#### POST /api/public/agent/{agent_id}/action/RECEIVE_POST/

**Purpose:** Deliver message to recipient's inbox

**Request:**
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
  "execution_id": "uuid",
  "message": "Action execution started"
}
```

**VERIFIED:** Direct curl test confirmed RECEIVE_POST creates files in `/agentlife/post/inbox/new/`

### 2. Filesystem Integration

**Structure:**
```
/loops/{loop_id}/filesystem/agentlife/post/
├── outbox/
│   ├── new/         # Outgoing messages waiting to be sent
│   └── sent/        # Messages that have been collected
└── inbox/
    ├── new/         # Incoming messages waiting to be read
    └── read/        # Messages that have been processed
```

**Message File Format:**
```json
{
  "message_id": "unique_id",
  "from": "sender_agent",
  "to": "recipient_agent",
  "timestamp": "2025-11-16T14:30:00Z",
  "subject": "Message subject",
  "body": "Message content",
  "priority": "high|normal|low",
  "type": "status_request|task|response",
  "metadata": {
    "project": "project_name",
    "requires_response": true,
    "cc": ["agent1", "agent2"]
  }
}
```

### 3. Database Integration

**Database:** SQLite (default) or PostgreSQL (production)

**Connection String (SQLite):**
```
DATABASE_URL=sqlite:///./agent_post.db
```

**Connection String (PostgreSQL):**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

**Schema Management:** SQLAlchemy ORM with automatic table creation

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.9+ | Core programming language |
| Web Framework | Flask | 2.3+ | REST API server |
| ORM | SQLAlchemy | 2.0+ | Database abstraction |
| Database | SQLite / PostgreSQL | - | Message persistence |
| HTTP Client | requests | 2.31+ | External API calls |
| Testing | unittest | Built-in | Test framework |
| Container | Docker | 24+ | Containerization |

### Dependencies

**Core:**
```txt
flask>=2.3.0
sqlalchemy>=2.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

**Testing:**
```txt
pytest>=7.4.0
pytest-mock>=3.11.0
```

### Development Tools

- **Docker Compose:** Multi-container orchestration
- **Make:** Task automation
- **Git:** Version control

---

## Deployment Architecture

### Docker Container Structure

```yaml
services:
  agent_post:
    build: ./agent_post
    container_name: agent_post
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=sqlite:///./agent_post.db
      - EXTERNAL_API_TOKEN=${EXTERNAL_API_TOKEN}
      - CITY_API_URL=http://loopai_web:5000/api/agents/cities-data/
    volumes:
      - ./agent_post:/app
    networks:
      - loopai_network
    depends_on:
      - loopai_web
```

### Network Communication

```
┌──────────────┐     Docker Network     ┌──────────────┐
│  agent_post  │◄───────────────────────►│ loopai_web   │
│  :8080       │   loopai_network        │  :5000       │
└──────────────┘                         └──────────────┘
       │                                        │
       │                                        │
       ▼                                        ▼
┌──────────────┐                         ┌──────────────┐
│  SQLite DB   │                         │  PostgreSQL  │
│  (local)     │                         │  (shared)    │
└──────────────┘                         └──────────────┘
```

### Environment Configuration

**Required Environment Variables:**

```bash
# Database
DATABASE_URL=sqlite:///./agent_post.db

# LoopAI Integration
CITY_API_URL=http://loopai_web:5000/api/agents/cities-data/
EXTERNAL_API_TOKEN=your_api_token_here

# Optional: Telegram Integration
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHANNEL_ID=your_channel_id
```

### Scaling Considerations

**Current State:** Single container deployment

**Future Scaling Options:**
1. **Horizontal Scaling:** Multiple agent_post containers with shared database
2. **Load Balancing:** Nginx/HAProxy in front of multiple instances
3. **Message Queue:** Redis/RabbitMQ for asynchronous processing
4. **Database Replication:** PostgreSQL read replicas for query performance

---

## Security Considerations

### Authentication

- API token-based authentication for external API calls
- Token stored in environment variables, not in code
- Docker secrets for production deployments

### Data Privacy

- Messages stored in isolated database
- No sensitive data logged
- Agent-to-agent communication encrypted in transit (HTTPS)

### Input Validation

- Message fields validated before persistence
- JSON parsing with error handling
- Protection against injection attacks via ORM

---

## Performance Characteristics

### Message Processing

- **Collection Rate:** ~1-2 seconds per agent (depends on WAKEUP execution time)
- **Delivery Rate:** ~0.5-1 second per recipient
- **Database Operations:** <10ms per insert/query (SQLite)

### Bottlenecks

1. **Polling Delay:** 3-second sleep between execution status checks
2. **Sequential Processing:** Agents processed one at a time
3. **Synchronous Delivery:** Each recipient delivery is blocking

### Optimization Opportunities

1. Parallel agent collection with asyncio
2. Batch database inserts
3. Asynchronous message delivery with queue
4. Execution status polling with exponential backoff

---

## Error Handling

### Network Errors

- Retry logic with exponential backoff
- Graceful degradation if agent unavailable
- Comprehensive logging for debugging

### Data Errors

- JSON parsing errors caught and logged
- Invalid message formats skipped with warning
- Database constraint violations handled

### Recovery Strategies

- Failed deliveries logged for manual retry
- Messages persist in database even if delivery fails
- Dead letter queue for permanently failed messages (future enhancement)

---

## Monitoring and Logging

### Logging Strategy

- **Level:** INFO for normal operations, DEBUG for troubleshooting
- **Format:** Structured logging with timestamps and context
- **Output:** Console (Docker logs) and file

### Key Metrics to Monitor

- Messages collected per cycle
- Messages delivered successfully
- Failed deliveries
- API response times
- Database query performance

### Health Checks

```python
GET /health
{
  "status": "healthy",
  "database": "connected",
  "loopai_web": "reachable"
}
```

---

## Future Enhancements

### Short-Term (1-2 months)

1. Fix message extraction from complex nested structures
2. Add retry mechanism for failed deliveries
3. Implement message read receipts
4. Add message priority queue

### Medium-Term (3-6 months)

1. Implement asynchronous message processing with Celery
2. Add Redis cache for agent addresses
3. Implement message threading and conversation tracking
4. Add web dashboard for message monitoring

### Long-Term (6-12 months)

1. Support for attachments and file transfers
2. End-to-end message encryption
3. Message routing with complex rules
4. Federation with external message systems

---

## References

- **Source Code:** `/agent_post/src/`
- **Tests:** `/agent_post/tests/`
- **Test Results:** `/docs/new_agents/implementation/MESSAGE_EXCHANGE_TEST_RESULTS.md`
- **CLAUDE Guide:** `/agent_post/CLAUDE.md`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Maintainer:** LoopAI Implementation Team
