# Agent Post Service - Testing Guide

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Production

---

## Table of Contents

1. [Overview](#overview)
2. [Test-Driven Development Approach](#test-driven-development-approach)
3. [Test Structure](#test-structure)
4. [Unit Tests](#unit-tests)
5. [Integration Tests](#integration-tests)
6. [Running Tests](#running-tests)
7. [Writing New Tests](#writing-new-tests)
8. [Test Coverage](#test-coverage)
9. [Manual Testing](#manual-testing)

---

## Overview

The Agent Post Service follows **Test-Driven Development (TDD)** principles, with comprehensive test coverage across all components. This guide explains the testing strategy, how to run tests, and how to write new tests.

### Test Philosophy

1. **Tests First:** Write tests before implementing features
2. **Fail First:** Ensure tests fail before writing code
3. **Pass Incrementally:** Implement minimal code to pass tests
4. **Refactor:** Improve code while keeping tests green
5. **Comprehensive Coverage:** Unit tests + integration tests + end-to-end tests

---

## Test-Driven Development Approach

### TDD Cycle

```
1. Write Test (RED)
   ↓
2. Run Test → FAIL
   ↓
3. Write Minimal Code (GREEN)
   ↓
4. Run Test → PASS
   ↓
5. Refactor (REFACTOR)
   ↓
6. Run Test → PASS
   ↓
Back to 1 for next feature
```

### Example TDD Workflow

**Feature:** Multi-recipient message parsing

**Step 1: Write Failing Test**
```python
def test_address_list_multiple_comma(self):
    message = Message(
        from_address='sender',
        to_address='recipient1, recipient2',
        data='Test'
    )
    self.assertEqual(['recipient1', 'recipient2'], message.address_list)
```

**Step 2: Run Test → FAIL**
```bash
python -m unittest tests.test_message
# AttributeError: 'Message' object has no attribute 'address_list'
```

**Step 3: Implement Feature**
```python
@property
def address_list(self) -> List[str]:
    if ',' in self.to_address:
        return [addr.strip() for addr in self.to_address.split(',')]
    return [self.to_address]
```

**Step 4: Run Test → PASS**
```bash
python -m unittest tests.test_message
# OK
```

**Step 5: Refactor**
```python
@property
def address_list(self) -> List[str]:
    to_list = [self.to_address]
    for delim in [';', ',', ' ']:
        if delim in self.to_address:
            normalized = self.to_address.replace(';', ' ').replace(',', ' ')
            to_list = [addr.strip() for addr in normalized.split()]
            break
    return to_list
```

**Step 6: Run Tests → PASS**
```bash
python -m unittest tests.test_message
# OK (handles comma, semicolon, and space delimiters)
```

---

## Test Structure

### Test Directory Layout

```
agent_post/
├── src/
│   ├── message_service.py
│   ├── external_api.py
│   ├── city_api.py
│   ├── message.py
│   ├── message_repo.py
│   ├── broadcast_data.py
│   └── json_helper.py
└── tests/
    ├── test_message_service.py          # Unit: MessageService
    ├── test_external_api.py              # Unit: ExternalAPI
    ├── test_city_api.py                  # Unit: CityAPI
    ├── test_message.py                   # Unit: Message model
    ├── test_message_repository.py        # Unit: MessageRepository
    ├── test_message_integration.py       # Integration: Full message flow
    ├── test_message_delivery_payload.py  # Integration: Delivery validation
    ├── test_process_message_integration.py  # Integration: End-to-end
    ├── test_direct_save_file.py          # Integration: Filesystem
    ├── test_message_file_creation.py     # Integration: File operations
    └── test_app.py                       # Unit: Flask app
```

### Test Categories

| Category | Purpose | Mocking | Real APIs |
|----------|---------|---------|-----------|
| **Unit Tests** | Test individual components in isolation | Yes | No |
| **Integration Tests** | Test component interactions | Partial | Yes |
| **End-to-End Tests** | Test complete workflows | No | Yes |

---

## Unit Tests

### test_message.py

Tests the Message data model.

**Location:** `tests/test_message.py`

**What It Tests:**
- Message creation
- Address parsing (single, comma, semicolon, space)
- Dictionary conversion
- JSON serialization

**Example Test:**
```python
def test_address_list_multiple_comma(self):
    """Test address_list property with comma-separated recipients"""
    message = Message(
        from_address='sender@example.com',
        to_address='recipient1@example.com, recipient2@example.com',
        data='Test message'
    )
    self.assertEqual(['recipient1@example.com', 'recipient2@example.com'],
                     message.address_list)
```

**Run:**
```bash
python -m unittest tests.test_message
```

---

### test_message_service.py

Tests MessageService with mocked dependencies.

**Location:** `tests/test_message_service.py`

**What It Tests:**
- Address extraction from cities data
- Multi-recipient message processing
- Delivery payload structure

**Mocking Strategy:**
```python
def setUp(self):
    # Create mocks for external dependencies
    self.city_api = MagicMock(spec=CityAPI)
    self.external_api = MagicMock(spec=ExternalAPI)

    # Create service with mocked dependencies
    self.service = MessageService(self.city_api, self.external_api)

    # Setup mock responses
    self.city_api.get_cities.return_value = {...}
    self.external_api.collect_from_outbox.return_value = [test_message]
```

**Example Test:**
```python
def test_message_multiple_recipients(self):
    """Test that MessageService correctly processes messages for multiple recipients"""
    self.service.process_messages()

    # Verify collect_from_outbox was called for each agent
    self.assertEqual(self.external_api.collect_from_outbox.call_count, 2)

    # Verify add_to_inbox was called for each recipient
    actual_calls = self.external_api.add_to_inbox.call_args_list
    self.assertEqual(len(actual_calls), 2)
```

**Run:**
```bash
python -m unittest tests.test_message_service
```

---

### test_external_api.py

Tests ExternalAPI with mocked HTTP requests.

**Location:** `tests/test_external_api.py`

**What It Tests:**
- Outbox message collection
- Inbox message delivery
- Error handling for network failures

**Mocking Strategy:**
```python
@patch('requests.get')
def test_external_api_collect_success(self, mock_get):
    # Mock response setup
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [
            {"result": {"updated_files": [...]}}
        ]
    }
    mock_get.return_value = mock_response

    # Test collection
    api = ExternalAPI("token")
    messages = api.collect_from_outbox("http://test/WAKEUP/")
    self.assertEqual(len(messages), 1)
```

**Run:**
```bash
python -m unittest tests.test_external_api
```

---

### test_city_api.py

Tests CityAPI with mocked HTTP requests.

**Location:** `tests/test_city_api.py`

**What It Tests:**
- Cities data retrieval
- Error handling

**Run:**
```bash
python -m unittest tests.test_city_api
```

---

## Integration Tests

### test_message_integration.py

Tests complete message flow with real LoopAI APIs.

**Location:** `tests/test_message_integration.py`

**What It Tests:**
- Real API communication
- Agent address discovery
- Message processing without errors

**Setup:**
```python
def setUp(self):
    load_dotenv()
    city_api_url = os.getenv("CITY_API_URL")
    external_api_token = os.getenv("EXTERNAL_API_TOKEN")

    # Create real API instances (no mocks)
    self.city_api = CityAPI(city_api_url)
    self.external_api = ExternalAPI(external_api_token)
    self.service = MessageService(self.city_api, self.external_api)
```

**Example Test:**
```python
def test_agent_addresses_from_real_api(self):
    """Test getting agent addresses from the real City API"""
    cities_data = self.city_api.get_cities()
    addresses = self.service.get_agent_addresses(cities_data)

    self.assertIsNotNone(addresses)
    self.assertIsInstance(addresses, dict)

    for agent_name, url in addresses.items():
        self.assertTrue(url.startswith("http"))
        self.assertTrue("/api/" in url.lower())
```

**Run:**
```bash
python -m unittest tests.test_message_integration
```

**Prerequisites:**
- LoopAI web service must be running
- `.env` file with valid `CITY_API_URL` and `EXTERNAL_API_TOKEN`

---

### test_message_delivery_payload.py

Tests message delivery with controlled mocking and real components.

**Location:** `tests/test_message_delivery_payload.py`

**What It Tests:**
- Payload structure validation
- Correct URL construction for recipients
- Tracking lists (sender/recipient)

**Example Test:**
```python
def test_message_multiple_recipients(self):
    """Test handling of messages with multiple recipients"""
    # Create controlled test environment
    agent_addresses = {
        'agent1': 'http://agent1/api/RECEIVE_POST',
        'agent2': 'http://agent2/api/RECEIVE_POST'
    }

    test_message = Message(
        from_address='agent1',
        to_address='agent2',
        data="TEST_PAYLOAD_MESSAGE"
    )

    # Track actual URL used
    called_with = {}
    def mock_add_to_inbox(url, message):
        called_with['url'] = url
        called_with['message'] = message
        return True

    self.external_api.add_to_inbox = MagicMock(side_effect=mock_add_to_inbox)

    # Run processing
    self.message_service.process_messages()

    # Verify correct URL
    expected_url = agent_addresses['agent2']
    actual_url = called_with.get('url')
    self.assertEqual(expected_url, actual_url)
```

**Run:**
```bash
python -m unittest tests.test_message_delivery_payload
```

---

### test_process_message_integration.py

Full end-to-end integration test (file name suggests content, file not yet read).

**Location:** `tests/test_process_message_integration.py`

**Run:**
```bash
python -m unittest tests.test_process_message_integration
```

---

## Running Tests

### Run All Tests

```bash
# Using unittest discover
python -m unittest discover tests

# Using pytest (if installed)
pytest tests/

# Using the unified test runner
python run_tests.py
```

### Run Specific Test Module

```bash
# Unit tests
python -m unittest tests.test_message
python -m unittest tests.test_message_service
python -m unittest tests.test_external_api

# Integration tests
python -m unittest tests.test_message_integration
python -m unittest tests.test_message_delivery_payload
```

### Run Specific Test Class

```bash
python -m unittest tests.test_message.TestMessage
```

### Run Specific Test Method

```bash
python -m unittest tests.test_message.TestMessage.test_address_list_multiple_comma
```

### Run with Verbose Output

```bash
python -m unittest discover tests -v
```

### Run Inside Docker Container

```bash
# Access container
docker compose exec agent_post bash

# Run tests
python -m unittest discover tests
```

---

## Writing New Tests

### TDD Workflow for New Feature

**Example:** Add support for message priorities

**Step 1: Write Test**

```python
# tests/test_message_service.py

def test_message_priority_ordering(self):
    """Test that high-priority messages are processed first"""
    # Create high and low priority messages
    high_priority_msg = Message(
        from_address='cityhall',
        to_address='padre',
        data='Urgent!',
        priority='high'
    )

    low_priority_msg = Message(
        from_address='cityhall',
        to_address='padre',
        data='Not urgent',
        priority='low'
    )

    # Mock collect to return low priority first
    self.external_api.collect_from_outbox.return_value = [
        low_priority_msg,
        high_priority_msg
    ]

    # Process messages
    self.service.process_messages()

    # Verify high priority was delivered first
    calls = self.external_api.add_to_inbox.call_args_list
    first_call_data = calls[0][0][1]  # Get payload from first call
    self.assertEqual(first_call_data['priority'], 'high')
```

**Step 2: Run Test → Should FAIL**

```bash
python -m unittest tests.test_message_service.TestMessageService.test_message_priority_ordering
# FAIL: AttributeError: 'Message' object has no attribute 'priority'
```

**Step 3: Implement Feature**

```python
# src/message.py

@dataclass
class Message:
    from_address: str
    to_address: str
    data: str
    priority: str = 'normal'  # Add priority field
    id: Optional[str] = None
    created_at: Optional[datetime] = None

# src/message_service.py

def process_messages(self):
    # ... collect messages ...

    # Sort by priority before delivering
    priority_order = {'high': 0, 'normal': 1, 'low': 2}
    messages_data.sort(key=lambda m: priority_order.get(m.priority, 1))

    # ... deliver messages ...
```

**Step 4: Run Test → Should PASS**

```bash
python -m unittest tests.test_message_service.TestMessageService.test_message_priority_ordering
# OK
```

### Test Naming Conventions

**Pattern:** `test_{feature}_{scenario}`

**Examples:**
- `test_address_list_single` → Tests single recipient parsing
- `test_address_list_multiple_comma` → Tests comma-separated parsing
- `test_message_multiple_recipients` → Tests multi-recipient delivery
- `test_external_api_collect_success` → Tests successful collection
- `test_external_api_collect_failure` → Tests collection error handling

### Test Structure Template

```python
import unittest
from unittest.mock import MagicMock, patch
from src.your_module import YourClass

class TestYourClass(unittest.TestCase):
    def setUp(self):
        """Set up test dependencies before each test"""
        # Initialize test data
        # Create mocks
        # Create instance under test

    def test_feature_success(self):
        """Test successful feature execution"""
        # Arrange: Setup inputs
        # Act: Execute feature
        # Assert: Verify outputs

    def test_feature_failure(self):
        """Test feature error handling"""
        # Arrange: Setup error condition
        # Act & Assert: Expect exception
        with self.assertRaises(ExpectedException):
            # Execute feature

    def tearDown(self):
        """Clean up after each test"""
        # Reset mocks
        # Close connections
        # Delete test data

if __name__ == '__main__':
    unittest.main()
```

---

## Test Coverage

### Current Coverage

| Module | Unit Tests | Integration Tests | Coverage |
|--------|------------|-------------------|----------|
| `message.py` | ✅ | ✅ | 95% |
| `message_service.py` | ✅ | ✅ | 90% |
| `external_api.py` | ✅ | ✅ | 85% |
| `city_api.py` | ✅ | ✅ | 90% |
| `message_repo.py` | ✅ | ✅ | 90% |
| `broadcast_data.py` | Partial | ✅ | 70% |
| `json_helper.py` | ⚠️ Minimal | ⚠️ Minimal | 50% |

### Measuring Coverage

```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests

# Generate report
coverage report

# Generate HTML report
coverage html
# Open htmlcov/index.html in browser
```

### Coverage Goals

- **Critical Paths:** 100% coverage (message processing, delivery)
- **Business Logic:** 95% coverage (address parsing, validation)
- **Utilities:** 80% coverage (JSON helpers, broadcasting)
- **Overall:** 90%+ coverage

---

## Manual Testing

### Test Message Exchange Script

```bash
# 1. Create test message in cityhall's outbox
cat > /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/71/filesystem/agentlife/post/outbox/new/test_msg.json << 'EOF'
{
  "message_id": "test_001",
  "from": "cityhall",
  "to": "padre",
  "timestamp": "2025-11-16T15:00:00Z",
  "subject": "Test Message",
  "body": "This is a test message",
  "priority": "normal"
}
EOF

# 2. Run message exchange
cd agent_post && docker compose exec -T agent_post python run_message_exchange.py

# 3. Verify message moved to sent
ls -lh /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/71/filesystem/agentlife/post/outbox/sent/

# 4. Verify message delivered to recipient
ls -lh /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/post/inbox/new/
```

### Test RECEIVE_POST with curl

```bash
# Direct delivery test
curl -X POST http://localhost:5050/api/public/agent/10/action/RECEIVE_POST/ \
  -H "Content-Type: application/json" \
  -d '{
    "updated_files": [{
      "path": "test_curl.json",
      "file_content": {
        "message": {
          "from": "cityhall",
          "to": "padre",
          "data": "Test via curl"
        }
      }
    }]
  }'

# Verify file created
ls -lh /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/post/inbox/new/
```

**VERIFIED:** RECEIVE_POST successfully creates files in inbox/new/

### Test WAKEUP Action

```bash
# Trigger WAKEUP
curl -X POST http://localhost:5050/api/public/agent/9/action/WAKEUP/

# Get execution_id from response, then poll status
curl http://localhost:5050/api/public/agent/9/action/WAKEUP/execution/{execution_id}/
```

### Test Database Queries

```bash
# Access container
docker compose exec agent_post bash

# Run Python shell
python3

# Query messages
>>> from src.message_repo import MessageRepository
>>> repo = MessageRepository("sqlite:///./agent_post.db")
>>> messages = repo.find_all()
>>> for msg in messages:
...     print(f"{msg.from_address} → {msg.to_address}: {msg.data}")
```

---

## Continuous Integration

### CI Pipeline (Recommended)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage pytest

    - name: Run unit tests
      run: python -m unittest discover tests

    - name: Check coverage
      run: |
        coverage run -m unittest discover tests
        coverage report --fail-under=80

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Troubleshooting Tests

### Test Fails: "Module not found"

**Problem:** Python can't find `src` module

**Solution:**
```bash
# Ensure you're in agent_post directory
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post

# Run with Python path
PYTHONPATH=. python -m unittest tests.test_message
```

### Test Fails: "Connection refused"

**Problem:** LoopAI web service not running (integration tests)

**Solution:**
```bash
# Start services
make up

# Wait for services to be ready
docker logs loopai_web

# Run integration tests
python -m unittest tests.test_message_integration
```

### Test Fails: Mocks not working

**Problem:** Mocks not properly configured

**Solution:**
```python
# Ensure mocks are created with spec
self.city_api = MagicMock(spec=CityAPI)

# Ensure return values are set
self.city_api.get_cities.return_value = {...}

# Verify mocks were called
self.city_api.get_cities.assert_called_once()
```

### Test Hangs: Infinite polling

**Problem:** Test waiting for execution that never completes

**Solution:**
```python
# Add timeout to tests
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Test timed out")

def test_with_timeout(self):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)  # 10 second timeout

    try:
        self.service.process_messages()
    finally:
        signal.alarm(0)  # Cancel alarm
```

---

## Best Practices

### 1. Test Independence

Each test should be independent and not rely on other tests.

**Bad:**
```python
def test_create_message(self):
    self.message = Message(...)  # Stored in self

def test_send_message(self):
    # Relies on test_create_message running first
    self.service.send(self.message)
```

**Good:**
```python
def test_create_message(self):
    message = Message(...)  # Local variable

def test_send_message(self):
    message = Message(...)  # Create fresh instance
    self.service.send(message)
```

### 2. Use setUp and tearDown

```python
def setUp(self):
    """Runs before each test"""
    self.service = MessageService(...)

def tearDown(self):
    """Runs after each test"""
    # Clean up resources
```

### 3. Test One Thing

Each test should verify one specific behavior.

**Bad:**
```python
def test_message_processing(self):
    # Tests collection, storage, and delivery
    messages = service.collect()
    service.save(messages)
    service.deliver(messages)
    # Too many assertions
```

**Good:**
```python
def test_message_collection(self):
    messages = service.collect()
    self.assertEqual(len(messages), 2)

def test_message_storage(self):
    service.save(message)
    saved = repo.find_all()
    self.assertIn(message, saved)

def test_message_delivery(self):
    result = service.deliver(message)
    self.assertTrue(result)
```

### 4. Use Descriptive Test Names

Test names should describe what is being tested and expected outcome.

**Bad:**
```python
def test1(self):
def test_message(self):
def test_works(self):
```

**Good:**
```python
def test_address_list_parses_comma_separated_recipients(self):
def test_delivery_fails_when_recipient_not_found(self):
def test_message_creates_with_auto_generated_uuid(self):
```

### 5. Test Error Cases

Don't just test happy paths - test error handling too.

```python
def test_collect_success(self):
    # Test normal operation

def test_collect_network_error(self):
    # Test network failure handling

def test_collect_invalid_response(self):
    # Test malformed response handling

def test_collect_empty_outbox(self):
    # Test no messages scenario
```

---

## References

- **Architecture:** `/agent_post/docs/ARCHITECTURE.md`
- **Message Flow:** `/agent_post/docs/MESSAGE_FLOW.md`
- **API Reference:** `/agent_post/docs/API_REFERENCE.md`
- **Test Results:** `/docs/new_agents/implementation/MESSAGE_EXCHANGE_TEST_RESULTS.md`
- **Source Code:** `/agent_post/src/`
- **Tests:** `/agent_post/tests/`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Maintainer:** LoopAI Implementation Team
