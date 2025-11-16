# Agent Collaboration Test Scenarios

This directory contains automated test scenarios for evaluating multi-agent collaboration, decision-making, and project thinking capabilities.

---

## Available Scenarios

### 1. Community Newsletter Project
**File:** `community_newsletter_project.md`
**Duration:** 6 days
**Difficulty:** Medium
**Focus:** Team collaboration, project management, content creation

**Description:**
Multiple agents work together to create a community newsletter. Tests coordination, decision-making about format and content, and ability to integrate work from multiple contributors.

**Key Capabilities Tested:**
- ✓ Multi-agent coordination
- ✓ Project planning and breakdown
- ✓ Decision-making with rationale
- ✓ Content creation and integration
- ✓ Quality review process
- ✓ Retrospective and learning

---

## Running Test Scenarios

### Quick Start

```bash
# Navigate to agent_post directory
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post

# Option 1: Send kick-off message only (manual monitoring)
python run_collaboration_test.py --send-only

# Option 2: Run full automated test (requires 6-day cycle running)
python run_collaboration_test.py --days 6 --output /tmp/collab_test
```

### Running with Custom 6-Day Cycle

```bash
# Start the test and 6-day cycle together
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post

# 1. Send kick-off message
python run_collaboration_test.py --send-only

# 2. Run 6-day agent cycle (from loopai_src directory)
cd /Users/dantweb/dantweb/l-sdk-27a/loopai_src
docker exec agent_post python run_all_cycles.py --days 6

# 3. After cycle completes, evaluate results
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post
python run_collaboration_test.py --output /tmp/collab_test
```

### Command-Line Options

```
--days N          Number of days to run test (default: 6)
--output DIR      Output directory for reports (default: /tmp/collaboration_test)
--interval SEC    Monitoring interval in seconds (default: 3600)
--send-only       Only send kick-off message and exit
```

---

## Scoring System

Tests are scored on a 120-point scale:

- **Team Collaboration (40 pts)**
  - Communication Quality (15 pts)
  - Coordination Effectiveness (15 pts)
  - Responsiveness (10 pts)

- **Decision Making (30 pts)**
  - Planning Decisions (10 pts)
  - Content Decisions (10 pts)
  - Conflict Resolution (10 pts)

- **Project Thinking (30 pts)**
  - Planning & Breakdown (10 pts)
  - Execution Management (10 pts)
  - Reflection & Learning (10 pts)

- **Deliverable Bonus (+20 pts)**
  - Quality of actual outputs created

**Pass Threshold:** 70 points (58%)

---

## Performance Levels

| Score Range | Level | Description |
|-------------|-------|-------------|
| 90-120 | Excellent | Outstanding collaboration and execution |
| 70-89 | Good | Solid teamwork with improvement opportunities |
| 50-69 | Needs Improvement | Basic collaboration but significant gaps |
| 0-49 | Poor | Major collaboration and execution issues |

---

## Test Report

After running a test, you'll receive a comprehensive report including:

- **Executive Summary** - Total score, pass/fail, performance level
- **Communication Analysis** - Messages exchanged, response times, participation
- **Decision Making Analysis** - Decisions identified, rationale quality
- **Project Execution** - Files created, planning evidence, timeline management
- **Deliverables Status** - Checklist of expected outputs
- **Message Timeline** - Chronological communication log
- **Recommendations** - Specific improvement suggestions
- **Conclusion** - Overall assessment

Example report location:
```
/tmp/collaboration_test/collaboration_test_report_20251116_153000.md
```

---

## Creating New Test Scenarios

### Template Structure

1. **Overview** - Purpose and objectives
2. **Scenario Description** - Project or task to be accomplished
3. **Phases** - Clear breakdown of project stages
4. **Participants** - Agent roles and responsibilities
5. **Success Criteria** - Measurable evaluation points
6. **Test Execution** - Initial messages and setup
7. **Evaluation Criteria** - Scoring rubric
8. **Expected Outcomes** - Different performance scenarios

### Best Practices

- Keep scenarios realistic and achievable
- Require multiple agents to coordinate
- Include clear decision points
- Define measurable deliverables
- Test different collaboration patterns
- Include reflection/learning phase

### Scenario Difficulty Levels

**Easy (3-4 days, 2-3 agents)**
- Simple coordination task
- Clear roles and responsibilities
- Minimal decision-making
- Single deliverable

**Medium (5-6 days, 3-5 agents)**
- Multi-phase project
- Multiple decision points
- Integrated deliverables
- Team coordination required

**Hard (7+ days, 4+ agents)**
- Complex project with dependencies
- Ambiguous requirements
- Conflicting priorities
- Multiple integrated deliverables

---

## Monitoring Test Progress

### Manual Monitoring

```bash
# Check message exchanges
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post
docker compose exec -T -w /app agent_post python3 -c "
from src.message_repo import message_repo
msgs = [m for m in message_repo.find_all() if 'newsletter' in m.data.lower()]
print(f'Project messages: {len(msgs)}')
for m in msgs[-5:]:
    print(f'{m.from_address} → {m.to_address}: {m.data[:50]}...')
"

# Check agent file creation
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/*/filesystem/agentlife/work -name "*newsletter*" -mmin -360

# Check agent inboxes
ls -lt /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/71/filesystem/agentlife/post/inbox/new/
```

### Automated Monitoring

The test script provides automated monitoring when run with full test mode:

```bash
python run_collaboration_test.py --days 6 --interval 1800  # Check every 30 min
```

---

## Troubleshooting

### Issue: Kick-off message not delivered

**Check:**
```bash
# Is message in outbox?
ls -l /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/post/outbox/new/

# Run message exchange manually
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post
docker compose exec -T agent_post python run_message_exchange.py
```

### Issue: Agents not responding

**Check:**
- Are agents running? (`docker compose ps`)
- Are daily cycles executing? (check logs)
- Are messages reaching inboxes?
- Are READ_POSTS actions running?

### Issue: No files created

**Check:**
- Agent work directories exist
- Agents have write permissions
- Messages contain clear task descriptions
- Sufficient time given (6 days recommended)

---

## Integration with CI/CD

### Automated Testing

```yaml
# Example GitHub Actions workflow
name: Agent Collaboration Test

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  test-collaboration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start services
        run: docker-compose up -d
      - name: Run collaboration test
        run: |
          cd agent_post
          python run_collaboration_test.py --days 6 --output ./test_results
      - name: Upload report
        uses: actions/upload-artifact@v2
        with:
          name: collaboration-test-report
          path: agent_post/test_results/
```

---

## Future Enhancements

### Planned Features
- [ ] Multiple scenario variants (conflict, partial team, self-organization)
- [ ] Real-time progress dashboard
- [ ] Automated scenario generation from templates
- [ ] Machine learning-based evaluation
- [ ] Comparative analysis across test runs
- [ ] Integration with performance monitoring

### Community Contributions

We welcome new test scenarios! Please include:
- Clear scenario description
- Success criteria
- Expected behaviors
- Evaluation rubric
- Sample messages

---

## References

- [Message Exchange Testing Report](../implementation/message_exchange_testing_report.md)
- [Sprint 3 Dev Status](../implementation/dev_status.md)
- [Agent Post Architecture](../architecture.md)

---

**Last Updated:** 2025-11-16
**Maintainer:** LoopAI Development Team
**Questions?** See [Agent Post README](../../README.md)
