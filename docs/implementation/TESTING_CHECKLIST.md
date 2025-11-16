# Testing Checklist - Message Exchange System

**Version:** 1.0
**Date:** 2025-11-16
**Sprints:** Sprint 3 & 4

---

## Overview

Comprehensive testing checklist for message exchange system fixes. Use this checklist to ensure complete test coverage before marking sprints as complete.

---

## Sprint 3: Message Extraction - Unit Tests

### Message Format Variations

- [ ] **Test:** Extract message with 'body' field
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_body_field
  ```

- [ ] **Test:** Extract message with 'data' field
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_data_field
  ```

- [ ] **Test:** Extract message with 'from' field
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_from_field
  ```

- [ ] **Test:** Extract message with 'from_address' field
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_from_address_field
  ```

- [ ] **Test:** Extract message with nested 'message' key
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_nested_message_key
  ```

- [ ] **Test:** Extract message from JSON string
  ```bash
  python -m unittest tests.test_external_api.TestExternalAPI.test_extract_message_with_json_string
  ```

### Field Mapping

- [ ] **Test:** body → data mapping
- [ ] **Test:** message_id → id mapping
- [ ] **Test:** timestamp → created_at mapping
- [ ] **Test:** All aliases handled correctly

### Validation

- [ ] **Test:** Returns None when 'from' missing
- [ ] **Test:** Returns None when 'to' missing
- [ ] **Test:** Accepts empty data field
- [ ] **Test:** Returns None for completely invalid structure

### Run All Unit Tests

```bash
# Run all external_api tests
python -m unittest tests.test_external_api -v

# Check coverage
coverage run -m unittest tests.test_external_api
coverage report -m src/external_api.py

# Target: >90% coverage
```

**Coverage Target:** >90% for `src/external_api.py`

**Result:** [ ] PASS / [ ] FAIL

---

## Sprint 3: Message Extraction - Integration Tests

### Real Message Extraction

- [ ] **Test:** Create message in outbox/new
  ```bash
  cat > /loops/71/filesystem/agentlife/post/outbox/new/integration_test.json << 'EOF'
  {
    "from": "cityhall",
    "to": "padre",
    "body": "Integration test message",
    "timestamp": "2025-11-16T17:00:00Z"
  }
  EOF
  ```

- [ ] **Test:** Run message exchange
  ```bash
  cd agent_post && docker compose exec -T agent_post python run_message_exchange.py
  ```

- [ ] **Test:** Verify extraction in logs
  ```bash
  grep "SUCCESS: Extracted message from cityhall to padre" /tmp/sprint3_integration.log
  ```
  **Expected:** Found

- [ ] **Test:** Verify message moved to sent
  ```bash
  ls -lh /loops/71/filesystem/agentlife/post/outbox/sent/integration_test.json
  ```
  **Expected:** File exists

- [ ] **Test:** Verify message delivered to inbox
  ```bash
  ls -lh /loops/72/filesystem/agentlife/post/inbox/new/
  ```
  **Expected:** New message file present

### Multi-Recipient Delivery

- [ ] **Test:** Create multi-recipient message
  ```bash
  cat > /loops/71/filesystem/agentlife/post/outbox/new/multi_test.json << 'EOF'
  {
    "from": "cityhall",
    "to": "padre, maria, zhou",
    "body": "Multi-recipient test"
  }
  EOF
  ```

- [ ] **Test:** Run message exchange

- [ ] **Test:** Verify all three recipients received
  ```bash
  ls -lh /loops/72/filesystem/agentlife/post/inbox/new/  # padre
  ls -lh /loops/73/filesystem/agentlife/post/inbox/new/  # maria
  ls -lh /loops/74/filesystem/agentlife/post/inbox/new/  # zhou
  ```
  **Expected:** Each has message file

### Database Persistence

- [ ] **Test:** Verify messages saved to database
  ```python
  from src.message_repo import MessageRepository
  repo = MessageRepository("sqlite:///./agent_post.db")
  messages = repo.find_all()
  print(f"Total messages: {len(messages)}")
  ```
  **Expected:** All extracted messages present

**Result:** [ ] PASS / [ ] FAIL

---

## Sprint 4: RECEIVE_POST Config - Configuration Tests

### Configuration File Existence

- [ ] **Test:** READ_POSTS.yaml exists for Loop 70
  ```bash
  ls -lh /loops/70/config/READ_POSTS.yaml
  ```

- [ ] **Test:** READ_POSTS.yaml exists for Loop 71
- [ ] **Test:** READ_POSTS.yaml exists for Loop 72
- [ ] **Test:** READ_POSTS.yaml exists for Loop 73
- [ ] **Test:** READ_POSTS.yaml exists for Loop 74

- [ ] **Test:** READ_POSTS.py exists and executable for all loops
  ```bash
  for loop_id in 70 71 72 73 74; do
      test -x /loops/$loop_id/config/READ_POSTS.py && echo "Loop $loop_id: OK" || echo "Loop $loop_id: FAIL"
  done
  ```

### Python Script Standalone Execution

- [ ] **Test:** READ_POSTS.py runs without errors
  ```bash
  cd /loops/72/filesystem/agentlife
  python3 ../../config/READ_POSTS.py
  ```
  **Expected:** JSON output with updated_files

- [ ] **Test:** Returns valid JSON structure
- [ ] **Test:** Handles empty inbox gracefully
- [ ] **Test:** Processes test message correctly

**Result:** [ ] PASS / [ ] FAIL

---

## Sprint 4: RECEIVE_POST Config - API Integration Tests

### Basic Action Execution

- [ ] **Test:** Create test message in inbox
  ```bash
  cat > /loops/72/filesystem/agentlife/post/inbox/new/api_test.json << 'EOF'
  {
    "message": {
      "from": "cityhall",
      "to": "padre",
      "subject": "API Test",
      "body": "Testing READ_POSTS via API"
    }
  }
  EOF
  ```

- [ ] **Test:** Trigger READ_POSTS via API
  ```bash
  curl -X POST http://localhost:5050/api/public/agent/10/action/READ_POSTS/
  ```
  **Expected:** {"success": true, "execution_id": "..."}

- [ ] **Test:** Wait for completion
  ```bash
  sleep 5
  ```

- [ ] **Test:** Check for IndexError in logs
  ```bash
  docker logs loopai_web --tail=50 | grep "IndexError"
  ```
  **Expected:** No IndexError found

### File Operations Verification

- [ ] **Test:** Message moved from inbox/new
  ```bash
  ls -lh /loops/72/filesystem/agentlife/post/inbox/new/api_test.json
  ```
  **Expected:** File NOT found

- [ ] **Test:** Message moved to inbox/read
  ```bash
  ls -lh /loops/72/filesystem/agentlife/post/inbox/read/api_test.json
  ```
  **Expected:** File found

- [ ] **Test:** Task file created
  ```bash
  ls -lh /loops/72/filesystem/agentlife/tasks/respond_to_*
  ```
  **Expected:** New task file exists

- [ ] **Test:** Task content correct
  ```bash
  cat /loops/72/filesystem/agentlife/tasks/respond_to_cityhall_*.txt
  ```
  **Expected:** Contains message subject and body

**Result:** [ ] PASS / [ ] FAIL

---

## Sprint 4: RECEIVE_POST Config - Edge Cases

### Empty Inbox

- [ ] **Test:** Remove all messages from inbox
  ```bash
  rm -f /loops/72/filesystem/agentlife/post/inbox/new/*
  ```

- [ ] **Test:** Run READ_POSTS
  ```bash
  curl -X POST http://localhost:5050/api/public/agent/10/action/READ_POSTS/
  ```

- [ ] **Test:** Verify no errors
  ```bash
  docker logs loopai_web --tail=20 | grep -i error
  ```
  **Expected:** No errors (empty updated_files is OK)

### Malformed Message

- [ ] **Test:** Create invalid JSON
  ```bash
  echo "not valid json" > /loops/72/filesystem/agentlife/post/inbox/new/invalid.json
  ```

- [ ] **Test:** Run READ_POSTS

- [ ] **Test:** Verify error logged
  ```bash
  docker logs loopai_web --tail=20 | grep "Invalid JSON"
  ```
  **Expected:** Error logged, processing continues

- [ ] **Test:** Valid messages still processed
  **Expected:** Other messages not affected

### Concurrent Messages

- [ ] **Test:** Create 5 messages quickly
  ```bash
  for i in {1..5}; do
      cat > /loops/72/filesystem/agentlife/post/inbox/new/concurrent_$i.json << EOF
  {
    "message": {
      "from": "test",
      "to": "padre",
      "subject": "Concurrent $i",
      "body": "Testing concurrent processing"
    }
  }
  EOF
  done
  ```

- [ ] **Test:** Run READ_POSTS once

- [ ] **Test:** Verify all 5 processed
  ```bash
  ls -lh /loops/72/filesystem/agentlife/post/inbox/read/ | grep concurrent | wc -l
  ```
  **Expected:** 5 messages in read folder

- [ ] **Test:** Verify all 5 tasks created
  ```bash
  ls -lh /loops/72/filesystem/agentlife/tasks/ | wc -l
  ```
  **Expected:** 5 task files

**Result:** [ ] PASS / [ ] FAIL

---

## End-to-End Integration Tests

### Complete Message Cycle

- [ ] **Step 1:** Create message in cityhall's outbox
  ```bash
  cat > /loops/71/filesystem/agentlife/post/outbox/new/e2e_final.json << 'EOF'
  {
    "from": "cityhall",
    "to": "padre",
    "subject": "E2E Test",
    "body": "Complete end-to-end test",
    "timestamp": "2025-11-16T19:00:00Z"
  }
  EOF
  ```

- [ ] **Step 2:** Run message exchange
  ```bash
  cd agent_post && docker compose exec -T agent_post python run_message_exchange.py
  ```

- [ ] **Step 3:** Verify extraction
  **Expected:** SUCCESS message in logs

- [ ] **Step 4:** Verify delivery
  **Expected:** Message in padre's inbox/new

- [ ] **Step 5:** Run READ_POSTS
  ```bash
  curl -X POST http://localhost:5050/api/public/agent/10/action/READ_POSTS/
  sleep 5
  ```

- [ ] **Step 6:** Verify processing
  - Message moved to inbox/read: [ ]
  - Task created: [ ]
  - No errors: [ ]

### Round-Trip Communication

- [ ] **Test:** cityhall sends to padre
- [ ] **Test:** padre receives and reads
- [ ] **Test:** padre sends reply to cityhall
- [ ] **Test:** cityhall receives reply

**Result:** [ ] PASS / [ ] FAIL

---

## Daily Cycle Integration

### Orchestration Test

- [ ] **Test:** Run 1-day cycle
  ```bash
  docker exec agent_post python run_all_cycles.py --days 1 2>&1 | tee /tmp/daily_cycle_test.log
  ```

- [ ] **Test:** Verify READ_POSTS executed
  ```bash
  grep "READ_POSTS" /tmp/daily_cycle_test.log
  ```
  **Expected:** Found for all agents

- [ ] **Test:** Verify all inboxes processed
  ```bash
  for loop_id in 70 71 72 73 74; do
      echo "Loop $loop_id:"
      ls /loops/$loop_id/filesystem/agentlife/post/inbox/new/ | wc -l
  done
  ```
  **Expected:** All empty or processed

- [ ] **Test:** No errors in cycle
  ```bash
  grep -i "error\|exception" /tmp/daily_cycle_test.log | grep -v "No error"
  ```
  **Expected:** No critical errors

**Result:** [ ] PASS / [ ] FAIL

---

## Regression Tests

### Verify No Breaking Changes

- [ ] **Test:** All existing tests still pass
  ```bash
  python -m unittest discover tests -v
  ```
  **Expected:** All pass

- [ ] **Test:** Message creation still works
- [ ] **Test:** WAKEUP action still works
- [ ] **Test:** Database operations still work
- [ ] **Test:** Multi-recipient parsing still works

**Result:** [ ] PASS / [ ] FAIL

---

## Performance Tests

### Message Processing Speed

- [ ] **Test:** Time for 10 message extraction
  ```bash
  time docker compose exec -T agent_post python run_message_exchange.py
  ```
  **Target:** <30 seconds

- [ ] **Test:** Time for READ_POSTS with 10 messages
  ```bash
  # Create 10 messages
  # ...
  time curl -X POST http://localhost:5050/api/public/agent/10/action/READ_POSTS/
  ```
  **Target:** <10 seconds

**Result:** [ ] PASS / [ ] FAIL

---

## Security Tests

### Input Validation

- [ ] **Test:** SQL injection attempts in message data
- [ ] **Test:** Path traversal attempts in file paths
- [ ] **Test:** Extremely large message payloads
- [ ] **Test:** Special characters in message fields

**Result:** [ ] PASS / [ ] FAIL

---

## Final Checklist

### Code Quality

- [ ] All unit tests passing (15+ tests)
- [ ] Test coverage >90% for modified files
- [ ] No debug print statements in production code
- [ ] Code follows project style guide
- [ ] No linting errors
- [ ] No security vulnerabilities

### Functionality

- [ ] Message extraction working
- [ ] Message delivery working
- [ ] Message reading working
- [ ] Task creation working
- [ ] No IndexError exceptions
- [ ] No msg_data = None errors

### Documentation

- [ ] API_REFERENCE.md updated
- [ ] MESSAGE_FLOW.md updated
- [ ] TESTING_GUIDE.md updated
- [ ] Code comments added
- [ ] Troubleshooting section added

### Integration

- [ ] Works with all 5 agents
- [ ] Works in daily cycle
- [ ] Works with message exchange
- [ ] Database persistence working
- [ ] No breaking changes

---

## Sign-Off

**Sprint 3 Testing Complete:**
- Tester: _____________ Date: _______
- Result: [ ] PASS / [ ] FAIL

**Sprint 4 Testing Complete:**
- Tester: _____________ Date: _______
- Result: [ ] PASS / [ ] FAIL

**Overall Testing Complete:**
- Tech Lead: _____________ Date: _______
- QA Lead: _____________ Date: _______
- Result: [ ] APPROVED / [ ] REJECTED

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Status:** Ready for Use
