# Sprint 3: Message Extraction Fix

**Sprint:** Week 1
**Duration:** 5 days
**Focus:** Fix Issue #1 - Message extraction from WAKEUP responses
**Approach:** Strict TDD with RED-GREEN-REFACTOR cycles

---

## Sprint Goal

Fix message extraction logic in `src/external_api.py` to correctly parse message data from WAKEUP responses, enabling successful message delivery to recipient inboxes.

**Success Metric:** 100% message extraction success rate with zero `msg_data = None` errors

---

## Day 1: TDD Cycle 1 - Body Field Mapping

### Morning: Setup & Analysis (2-3 hours)

**Tasks:**
1. ☐ Create feature branch: `git checkout -b sprint3-message-extraction`
2. ☐ Add debug logging to understand actual message format
3. ☐ Create test message and run message exchange
4. ☐ Analyze debug output to identify format mismatch

**Debug Setup:**
```python
# Temporary debug logging in src/external_api.py
def _extract_message_data(self, file_entry: Dict) -> Optional[Dict]:
    import json
    print(f"DEBUG: file_entry = {json.dumps(file_entry, indent=2)}")
    # ... rest of method
```

**Test Command:**
```bash
# Create test message
cat > /loops/71/filesystem/agentlife/post/outbox/new/sprint3_day1.json << 'EOF'
{
  "from": "cityhall",
  "to": "padre",
  "body": "Sprint 3 Day 1 test",
  "timestamp": "2025-11-16T16:00:00Z"
}
EOF

# Run with debug output
cd agent_post && docker compose exec -T agent_post python run_message_exchange.py 2>&1 | tee /tmp/sprint3_day1_debug.log
```

**Analysis Deliverable:**
- Document actual message format in comments
- Identify field name mismatches
- Confirm hypothesis from FIXING_PLAN.md

---

### Afternoon: TDD Cycle 1 (3-4 hours)

#### Step 1: RED - Write Failing Test

**File:** `tests/test_external_api.py`

```python
def test_extract_message_with_body_field(self):
    """Test extraction when message uses 'body' instead of 'data'"""
    api = ExternalAPI("token")

    # Based on actual format discovered in morning analysis
    file_entry = {
        "path": "./sprint3_test.json",
        "file_content": {
            "message_id": "msg_sprint3_001",
            "from": "cityhall",
            "to": "padre",
            "body": "Test message body content",
            "timestamp": "2025-11-16T16:00:00Z",
            "priority": "high"
        }
    }

    msg_data = api._extract_message_data(file_entry)

    # Assertions that will FAIL initially
    self.assertIsNotNone(msg_data, "Extraction should not return None")
    self.assertEqual(msg_data['from_address'], 'cityhall')
    self.assertEqual(msg_data['to_address'], 'padre')
    self.assertEqual(msg_data['data'], 'Test message body content')  # Maps 'body' to 'data'
    self.assertEqual(msg_data['id'], 'msg_sprint3_001')  # Maps 'message_id' to 'id'
```

**Run Test:**
```bash
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_body_field -v
```

**Expected Output:**
```
test_extract_message_with_body_field (tests.test_external_api.TestExternalAPI) ... FAIL

AssertionError: Extraction should not return None
```

**Commit:**
```bash
git add tests/test_external_api.py
git commit -m "RED: Test for body field extraction (Sprint 3 Day 1)"
```

---

#### Step 2: GREEN - Minimal Implementation

**File:** `src/external_api.py`

```python
def _extract_message_data(self, file_entry: Dict) -> Optional[Dict]:
    """Extract message data from file_content structure"""

    file_content = file_entry.get('file_content')
    if not file_content:
        return None

    # Handle JSON string
    if isinstance(file_content, str):
        try:
            file_content = json.loads(file_content)
        except json.JSONDecodeError:
            return None

    # Check for nested 'message' key
    if 'message' in file_content:
        msg_data = file_content['message']
    else:
        msg_data = file_content

    # Extract fields - NEW: Map 'body' to 'data'
    extracted = {}
    extracted['from_address'] = msg_data.get('from')
    extracted['to_address'] = msg_data.get('to')
    extracted['data'] = msg_data.get('body')  # NEW: Body field mapping
    extracted['id'] = msg_data.get('message_id')  # NEW: message_id mapping

    # Validate required fields
    if not extracted['from_address'] or not extracted['to_address']:
        return None

    return extracted
```

**Run Test:**
```bash
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_body_field -v
```

**Expected Output:**
```
test_extract_message_with_body_field (tests.test_external_api.TestExternalAPI) ... ok

Ran 1 test in 0.001s

OK
```

**Commit:**
```bash
git add src/external_api.py
git commit -m "GREEN: Implement body field extraction (Sprint 3 Day 1)"
```

---

### End of Day 1 Deliverables

- ✅ Feature branch created
- ✅ Actual message format documented
- ✅ 1 new test written and passing
- ✅ Body → data field mapping implemented
- ✅ message_id → id field mapping implemented

**Sprint Progress:** 20% complete

---

## Day 2: TDD Cycle 2 - Field Aliases

### Morning: TDD Cycle 2A - from_address Alias (2-3 hours)

#### Step 1: RED - Test for Field Aliases

**File:** `tests/test_external_api.py`

```python
def test_extract_message_with_from_address_field(self):
    """Test extraction handles both 'from' and 'from_address'"""
    api = ExternalAPI("token")

    # Test with 'from_address' variant
    file_entry = {
        "path": "./test_from_address.json",
        "file_content": {
            "from_address": "cityhall",
            "to_address": "padre",
            "data": "Using from_address field"
        }
    }

    msg_data = api._extract_message_data(file_entry)

    self.assertIsNotNone(msg_data)
    self.assertEqual(msg_data['from_address'], 'cityhall')
    self.assertEqual(msg_data['to_address'], 'padre')
    self.assertEqual(msg_data['data'], 'Using from_address field')
```

**Run Test (Should FAIL):**
```bash
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_from_address_field -v
```

**Commit:**
```bash
git add tests/test_external_api.py
git commit -m "RED: Test for from_address field alias (Sprint 3 Day 2)"
```

---

#### Step 2: GREEN - Implement Field Aliasing

**File:** `src/external_api.py`

```python
def _extract_message_data(self, file_entry: Dict) -> Optional[Dict]:
    # ... previous code ...

    # Handle field aliases - NEW
    extracted = {}
    extracted['from_address'] = msg_data.get('from_address') or msg_data.get('from')
    extracted['to_address'] = msg_data.get('to_address') or msg_data.get('to')
    extracted['data'] = msg_data.get('data') or msg_data.get('body')
    extracted['id'] = msg_data.get('id') or msg_data.get('message_id')
    extracted['created_at'] = msg_data.get('created_at') or msg_data.get('timestamp')

    # Validate
    if not extracted['from_address'] or not extracted['to_address']:
        return None

    return extracted
```

**Run Test (Should PASS):**
```bash
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_from_address_field -v
```

**Run All Tests:**
```bash
python -m unittest tests.test_external_api -v
```

**Commit:**
```bash
git add src/external_api.py
git commit -m "GREEN: Implement field aliasing (Sprint 3 Day 2)"
```

---

### Afternoon: TDD Cycle 2B - Additional Test Cases (3-4 hours)

#### Write Multiple Format Tests

```python
def test_extract_message_with_data_field(self):
    """Test extraction with 'data' instead of 'body'"""
    # ...

def test_extract_message_with_nested_message_key(self):
    """Test extraction with nested 'message' key"""
    file_entry = {
        "path": "./test.json",
        "file_content": {
            "message": {
                "from": "cityhall",
                "to": "padre",
                "body": "Nested message"
            }
        }
    }
    # ...

def test_extract_message_with_json_string(self):
    """Test extraction when file_content is JSON string"""
    file_entry = {
        "path": "./test.json",
        "file_content": '{"from": "cityhall", "to": "padre", "body": "JSON string"}'
    }
    # ...
```

**Process for Each Test:**
1. Write test (RED)
2. Run test - verify FAIL
3. Implement (GREEN)
4. Run test - verify PASS
5. Run all tests - verify all PASS
6. Commit

**End of Day 2 Deliverables:**

- ✅ Field aliasing implemented
- ✅ 4+ new tests written and passing
- ✅ All format variations handled
- ✅ Nested message key supported
- ✅ JSON string parsing working

**Sprint Progress:** 40% complete

---

## Day 3: TDD Cycle 3 - Validation & Refactor

### Morning: TDD Cycle 3 - Validation (2-3 hours)

#### Step 1: RED - Test for Missing Fields

```python
def test_extract_message_returns_none_for_missing_from(self):
    """Test extraction returns None when 'from' field missing"""
    api = ExternalAPI("token")

    file_entry = {
        "path": "./test.json",
        "file_content": {
            "to": "padre",
            "body": "No sender"
        }
    }

    result = api._extract_message_data(file_entry)
    self.assertIsNone(result, "Should return None when 'from' field missing")

def test_extract_message_returns_none_for_missing_to(self):
    """Test extraction returns None when 'to' field missing"""
    # ...

def test_extract_message_allows_empty_data(self):
    """Test extraction succeeds even with empty data field"""
    api = ExternalAPI("token")

    file_entry = {
        "path": "./test.json",
        "file_content": {
            "from": "cityhall",
            "to": "padre"
            # No data or body field
        }
    }

    result = api._extract_message_data(file_entry)
    self.assertIsNotNone(result, "Should extract even without data field")
    self.assertIsNone(result.get('data'), "data should be None if not provided")
```

**Run Tests:**
```bash
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_returns_none_for_missing_from -v
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_returns_none_for_missing_to -v
python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_allows_empty_data -v
```

**Commit:**
```bash
git add tests/test_external_api.py
git commit -m "RED: Tests for field validation (Sprint 3 Day 3)"
```

---

#### Step 2: GREEN - Validation Already Implemented

Validation logic is already in place from Day 1:
```python
if not extracted['from_address'] or not extracted['to_address']:
    return None
```

Tests should already PASS. If not, add validation logic.

**Commit:**
```bash
git commit -m "GREEN: Validation tests passing (Sprint 3 Day 3)"
```

---

### Afternoon: REFACTOR - Clean Up & Add Logging (3-4 hours)

#### Step 1: Refactor Extraction Logic

```python
def _extract_message_data(self, file_entry: Dict) -> Optional[Dict]:
    """
    Extract message data from file_content structure.

    Handles multiple format variations:
    - Nested 'message' key
    - Direct fields in file_content
    - JSON string in file_content
    - Field aliases: from/from_address, to/to_address, body/data, etc.

    Returns:
        Dict with standardized field names, or None if required fields missing
    """

    file_content = file_entry.get('file_content')
    if not file_content:
        print(f"WARNING: No file_content in entry")
        return None

    # Parse JSON string if needed
    if isinstance(file_content, str):
        try:
            file_content = json.loads(file_content)
        except json.JSONDecodeError as e:
            print(f"ERROR: Failed to parse JSON: {e}")
            return None

    # Handle nested 'message' key
    msg_data = file_content.get('message', file_content)

    # Extract with field aliasing
    extracted = {
        'from_address': msg_data.get('from_address') or msg_data.get('from'),
        'to_address': msg_data.get('to_address') or msg_data.get('to'),
        'data': msg_data.get('data') or msg_data.get('body'),
        'id': msg_data.get('id') or msg_data.get('message_id'),
        'created_at': msg_data.get('created_at') or msg_data.get('timestamp')
    }

    # Validate required fields
    if not extracted['from_address'] or not extracted['to_address']:
        print(f"ERROR: Missing required fields - from: {extracted['from_address']}, to: {extracted['to_address']}")
        return None

    print(f"SUCCESS: Extracted message from {extracted['from_address']} to {extracted['to_address']}")
    return extracted
```

**Run All Tests:**
```bash
python -m unittest tests.test_external_api -v
```

**All tests should still PASS after refactoring**

**Commit:**
```bash
git add src/external_api.py
git commit -m "REFACTOR: Clean up extraction logic and add logging (Sprint 3 Day 3)"
```

---

### End of Day 3 Deliverables

- ✅ Validation tests written and passing
- ✅ Code refactored with clear structure
- ✅ Logging added for debugging
- ✅ Documentation strings updated
- ✅ All tests passing (10+ tests)

**Sprint Progress:** 60% complete

---

## Day 4: Integration Testing

### Morning: Unit Test Review (1-2 hours)

**Tasks:**
1. ☐ Run full test suite
2. ☐ Check test coverage
3. ☐ Add any missing edge case tests
4. ☐ Verify all tests documented

**Commands:**
```bash
# Run all tests with verbose output
python -m unittest discover tests -v

# Check coverage
coverage run -m unittest discover tests
coverage report -m
coverage html

# Review coverage report
open htmlcov/index.html
```

**Target:** >90% coverage for `src/external_api.py`

---

### Afternoon: Integration Testing (4-5 hours)

#### Integration Test 1: Real Message Extraction

```bash
# 1. Create test message with actual format
cat > /loops/71/filesystem/agentlife/post/outbox/new/integration_test_day4.json << 'EOF'
{
  "from": "cityhall",
  "to": "padre",
  "body": "Sprint 3 Day 4 integration test",
  "subject": "Integration Test",
  "timestamp": "2025-11-16T17:00:00Z",
  "priority": "high"
}
EOF

# 2. Run message exchange
cd agent_post && docker compose exec -T agent_post python run_message_exchange.py 2>&1 | tee /tmp/sprint3_integration.log

# 3. Verify extraction succeeded
grep "SUCCESS: Extracted message from cityhall to padre" /tmp/sprint3_integration.log
# Expected: Found

# 4. Verify message moved to sent
ls -lh /loops/71/filesystem/agentlife/post/outbox/sent/integration_test_day4.json
# Expected: File exists

# 5. Verify message delivered to inbox
ls -lh /loops/72/filesystem/agentlife/post/inbox/new/
# Expected: New message file present

# 6. Read delivered message
cat /loops/72/filesystem/agentlife/post/inbox/new/<uuid>.json
# Expected: Contains message data
```

**Expected Results:**
- ✅ Extraction log shows SUCCESS
- ✅ Message moved from outbox/new to outbox/sent
- ✅ Message delivered to padre's inbox/new
- ✅ Message content preserved

---

#### Integration Test 2: Multi-Recipient Delivery

```bash
# Create multi-recipient message
cat > /loops/71/filesystem/agentlife/post/outbox/new/multi_recipient_day4.json << 'EOF'
{
  "from": "cityhall",
  "to": "padre, maria, zhou",
  "body": "Multi-recipient integration test",
  "timestamp": "2025-11-16T17:30:00Z"
}
EOF

# Run exchange
cd agent_post && docker compose exec -T agent_post python run_message_exchange.py

# Verify all three recipients received
ls -lh /loops/72/filesystem/agentlife/post/inbox/new/  # padre
ls -lh /loops/73/filesystem/agentlife/post/inbox/new/  # maria
ls -lh /loops/74/filesystem/agentlife/post/inbox/new/  # zhou
```

**Expected Results:**
- ✅ Message extracted once
- ✅ Delivered to 3 separate inboxes
- ✅ No duplicate deliveries

---

#### Integration Test 3: Database Persistence

```bash
# Access database
docker compose exec agent_post python3 << 'PYTHON'
from src.message_repo import MessageRepository

repo = MessageRepository("sqlite:///./agent_post.db")
messages = repo.find_all()

print(f"Total messages in DB: {len(messages)}")

# Find today's messages
from datetime import date
today = date.today()
today_messages = [m for m in messages if m.created_at.date() == today]

print(f"Today's messages: {len(today_messages)}")

for msg in today_messages[-5:]:  # Last 5 messages
    print(f"  {msg.from_address} → {msg.to_address}: {msg.data[:50]}...")
PYTHON
```

**Expected Results:**
- ✅ All extracted messages in database
- ✅ Correct field values
- ✅ Timestamps accurate

---

### End of Day 4 Deliverables

- ✅ All unit tests passing
- ✅ Test coverage >90%
- ✅ Real message extraction working
- ✅ Multi-recipient delivery working
- ✅ Database persistence verified

**Sprint Progress:** 80% complete

---

## Day 5: Documentation & Buffer

### Morning: Documentation (2-3 hours)

**Tasks:**
1. ☐ Update API_REFERENCE.md with new field mappings
2. ☐ Update MESSAGE_FLOW.md with extraction details
3. ☐ Add troubleshooting section
4. ☐ Document all format variations supported

**Documentation Updates:**

```markdown
# API_REFERENCE.md - Add section:

### Message Format Variations Supported

The `_extract_message_data()` method handles multiple format variations:

**Field Aliases:**
- `from` or `from_address` → `from_address`
- `to` or `to_address` → `to_address`
- `body` or `data` → `data`
- `message_id` or `id` → `id`
- `timestamp` or `created_at` → `created_at`

**Structure Variations:**
1. Direct fields in file_content
2. Nested under 'message' key
3. JSON string in file_content

**Example formats supported:**
...
```

---

### Afternoon: Code Review & Merge Prep (2-3 hours)

**Tasks:**
1. ☐ Self code review
2. ☐ Remove debug logging
3. ☐ Clean up commits (optional squash)
4. ☐ Create pull request
5. ☐ Buffer for any issues

**Code Review Checklist:**
- [ ] All tests passing
- [ ] Test coverage >90%
- [ ] No debug print statements in final code (only logging)
- [ ] Code follows project style guide
- [ ] Documentation updated
- [ ] Commit messages clear
- [ ] No merge conflicts

**Pull Request:**
```bash
# Push branch
git push origin sprint3-message-extraction

# Create PR
gh pr create --title "Sprint 3: Fix message extraction from WAKEUP responses" \
  --body "$(cat <<'EOF'
## Summary

Fixes Issue #1: Message extraction from WAKEUP responses

## Changes

- Updated `_extract_message_data()` to handle multiple field name variations
- Added field aliasing: body→data, from→from_address, message_id→id, etc.
- Comprehensive validation of required fields
- Added logging for debugging

## Tests

- 10+ new unit tests covering all format variations
- Integration tests with real messages
- Test coverage: 95%

## Verification

- ✅ Messages successfully extracted from outboxes
- ✅ Messages delivered to recipient inboxes
- ✅ Database persistence working
- ✅ Multi-recipient delivery working

## TDD Approach

- All tests written before implementation
- Strict RED-GREEN-REFACTOR cycles
- Continuous refactoring with green tests

🤖 Developed using Test-Driven Development
EOF
)"
```

---

### End of Day 5 / Sprint 3 Deliverables

**Code:**
- ✅ Message extraction fully working
- ✅ All format variations supported
- ✅ Comprehensive unit test suite
- ✅ Integration tests passing

**Documentation:**
- ✅ API reference updated
- ✅ Message flow documentation updated
- ✅ Troubleshooting guide added

**Quality:**
- ✅ Test coverage >90%
- ✅ All tests passing
- ✅ Code reviewed
- ✅ Pull request created

**Sprint Progress:** 100% complete ✅

---

## Sprint 3 Retrospective

### What Went Well

- [ ] TDD approach kept focus clear
- [ ] Tests caught regressions immediately
- [ ] Field aliasing handles all variations
- [ ] Integration tests validated real-world usage

### What Could Be Improved

- [ ] Initial format analysis took longer than expected
- [ ] More format variations than anticipated
- [ ] Need better logging strategy from start

### Lessons Learned

- [ ] Debug logging essential for understanding external data
- [ ] Field aliasing more flexible than format conversion
- [ ] Integration tests find issues unit tests miss

### Carryover to Sprint 4

- [ ] Logging patterns established
- [ ] Testing approach validated
- [ ] Integration test framework ready

---

## References

- **Fixing Plan:** [../FIXING_PLAN.md](../FIXING_PLAN.md)
- **Testing Guide:** [../TESTING_GUIDE.md](../TESTING_GUIDE.md)
- **Sprint 4 Plan:** [SPRINT_4_RECEIVE_POST_CONFIG.md](SPRINT_4_RECEIVE_POST_CONFIG.md)

---

**Sprint Status:** ✅ READY TO START
**Estimated Velocity:** 8-10 story points
**Actual Velocity:** TBD after completion
