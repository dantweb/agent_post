# Implementation Plan - Message Exchange System Fixes

**Version:** 1.0
**Date:** 2025-11-16
**Status:** Planning
**Duration:** 2 weeks (Sprint 3 & 4)

---

## Overview

This implementation plan breaks down the TDD-first fixing strategy from [FIXING_PLAN.md](../FIXING_PLAN.md) into actionable sprints with concrete tasks, acceptance criteria, and deliverables.

---

## Sprint Structure

### Sprint 3: Message Extraction Fix (Week 1)
**Duration:** 5 days
**Focus:** Fix Issue #1 - Message extraction from WAKEUP responses
**Approach:** Strict TDD with RED-GREEN-REFACTOR cycles

**Deliverables:**
- ✅ Message extraction working for all format variations
- ✅ Comprehensive unit tests
- ✅ Integration tests passing
- ✅ Messages successfully delivered to recipients

**Document:** [SPRINT_3_MESSAGE_EXTRACTION.md](SPRINT_3_MESSAGE_EXTRACTION.md)

---

### Sprint 4: RECEIVE_POST Configuration Fix (Week 2)
**Duration:** 5 days
**Focus:** Fix Issue #2 - RECEIVE_POST/READ_POSTS file operations
**Approach:** Test-driven configuration with integration validation

**Deliverables:**
- ✅ READ_POSTS generating updated_files response
- ✅ Messages moving from inbox/new to inbox/read
- ✅ Tasks created for agents
- ✅ End-to-end message flow working

**Document:** [SPRINT_4_RECEIVE_POST_CONFIG.md](SPRINT_4_RECEIVE_POST_CONFIG.md)

---

## Sprint Timeline

```
Week 1: Sprint 3 - Message Extraction Fix
├── Day 1: TDD Cycle 1 - Body field mapping
├── Day 2: TDD Cycle 2 - Field aliases
├── Day 3: TDD Cycle 3 - Validation + Refactor
├── Day 4: Integration testing
└── Day 5: Documentation + Buffer

Week 2: Sprint 4 - RECEIVE_POST Config Fix
├── Day 1-2: Configuration analysis & TDD setup
├── Day 3: READ_POSTS implementation
├── Day 4: Integration testing
└── Day 5: End-to-end validation + Documentation
```

---

## Success Metrics

### Sprint 3 Success Criteria

- [ ] All unit tests passing (10+ new tests)
- [ ] Message extraction success rate: 100%
- [ ] No `msg_data = None` errors in logs
- [ ] Messages delivered to recipient inboxes
- [ ] Database contains extracted messages

### Sprint 4 Success Criteria

- [ ] No IndexError on empty updated_files
- [ ] Messages moved from inbox/new to inbox/read
- [ ] Tasks created in agent task directories
- [ ] End-to-end message exchange working
- [ ] Round-trip communication successful

### Overall Success Criteria

- [ ] cityhall sends message to padre ✅
- [ ] padre receives message in inbox ✅
- [ ] padre reads message and creates task ✅
- [ ] padre responds to cityhall ✅
- [ ] cityhall receives response ✅

---

## Team Capacity

**Developers:** 1-2 developers
**Estimated Hours:**
- Sprint 3: 20-30 hours (4-6 hours/day)
- Sprint 4: 20-30 hours (4-6 hours/day)
- Total: 40-60 hours

**Buffer:** 20% for unexpected issues

---

## Risk Management

### High Risk Items

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Unknown message format variations | Extensive debug logging first | Manual format analysis |
| RECEIVE_POST config complexity | Study existing working actions | Simplify to minimal working config |
| Breaking existing functionality | Comprehensive test suite | Git rollback plan |

### Medium Risk Items

| Risk | Mitigation | Contingency |
|------|------------|-------------|
| Integration test failures | Isolated testing environment | Mock-based testing fallback |
| Performance degradation | Performance benchmarks | Optimize after functionality works |

---

## Dependencies

### Technical Dependencies

- LoopAI web service running
- All 5 Living Agents configured (Loops 70-74)
- Database accessible
- Docker environment operational

### Process Dependencies

- Code review approval
- Test coverage requirements (>80%)
- Documentation updates
- Regression testing

---

## Daily Standup Format

**What was completed yesterday?**
- Tests written
- Tests passing
- Integration status

**What will be done today?**
- Next TDD cycle
- Specific test to write
- Expected outcome

**Any blockers?**
- Technical issues
- Dependency problems
- Unclear requirements

---

## Sprint Documents

1. **[SPRINT_3_MESSAGE_EXTRACTION.md](SPRINT_3_MESSAGE_EXTRACTION.md)**
   - Day-by-day TDD cycles
   - Specific test cases
   - Implementation steps
   - Acceptance criteria

2. **[SPRINT_4_RECEIVE_POST_CONFIG.md](SPRINT_4_RECEIVE_POST_CONFIG.md)**
   - Configuration analysis
   - Test-driven configuration approach
   - Integration validation
   - End-to-end testing

3. **[TESTING_CHECKLIST.md](TESTING_CHECKLIST.md)**
   - Unit test checklist
   - Integration test checklist
   - Manual test scripts
   - Regression test suite

4. **[DEFINITION_OF_DONE.md](DEFINITION_OF_DONE.md)**
   - Code complete criteria
   - Test coverage requirements
   - Documentation requirements
   - Review approval process

---

## TDD Principles Reminder

### RED-GREEN-REFACTOR Cycle

1. **RED:** Write failing test
   - Test describes desired behavior
   - Test fails (no implementation yet)
   - Commit: "RED: Test for feature X"

2. **GREEN:** Minimal implementation
   - Write simplest code to pass test
   - Test passes
   - Commit: "GREEN: Implement feature X"

3. **REFACTOR:** Improve code
   - Clean up implementation
   - All tests still pass
   - Commit: "REFACTOR: Clean up feature X"

### TDD Best Practices

- ✅ Write test before code
- ✅ One test at a time
- ✅ Minimal implementation
- ✅ Run tests frequently
- ✅ Refactor continuously
- ❌ Don't skip tests
- ❌ Don't write production code without failing test
- ❌ Don't refactor without green tests

---

## Communication Plan

### Daily Updates

- Commit messages follow TDD convention
- Push to feature branch daily
- Update sprint progress tracker

### Weekly Review

- Sprint retrospective
- Demo working features
- Adjust next sprint plan

### Documentation Updates

- Update docs after feature complete
- Keep examples synchronized with code
- Document known issues and workarounds

---

## Rollback Strategy

### Git Strategy

```bash
# Feature branches
git checkout -b sprint3-message-extraction
git checkout -b sprint4-receive-post-config

# Rollback if needed
git checkout main
git revert <commit-hash>
```

### Testing Before Merge

1. All unit tests pass
2. All integration tests pass
3. Manual smoke test
4. Code review approved
5. Documentation updated

---

## Reference Documents

- **Main Fixing Plan:** [../FIXING_PLAN.md](../FIXING_PLAN.md)
- **Architecture:** [../ARCHITECTURE.md](../ARCHITECTURE.md)
- **Message Flow:** [../MESSAGE_FLOW.md](../MESSAGE_FLOW.md)
- **Testing Guide:** [../TESTING_GUIDE.md](../TESTING_GUIDE.md)
- **API Reference:** [../API_REFERENCE.md](../API_REFERENCE.md)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-16
**Sprint Start Date:** TBD
**Maintainer:** LoopAI Implementation Team
