# Automated Team Collaboration Test Scenario

**Version:** 1.0
**Date:** 2025-11-16
**Purpose:** Validate multi-agent collaboration, decision-making, and project thinking capabilities

---

## Test Overview

This automated test scenario evaluates whether agents can:
1. **Work as a team** - Coordinate, communicate, and collaborate effectively
2. **Make correct decisions** - Choose appropriate approaches, prioritize tasks, resolve conflicts
3. **Demonstrate project thinking** - Break down complex projects, identify dependencies, plan execution

---

## Test Scenario: Community Newsletter Project

### Project Description

The FRBG community will create a monthly newsletter covering educational insights, community updates, and cultural perspectives. This project requires multiple agents to collaborate, make decisions about content and format, and deliver a cohesive final product.

### Project Phases

**Phase 1: Planning & Decision Making (Days 1-2)**
- Decide newsletter format (sections, length, tone)
- Assign responsibilities
- Set deadlines
- Define success criteria

**Phase 2: Content Creation (Days 2-4)**
- Educational content from TeacherJohn
- Community updates from cityhall
- Cultural perspective from zhou
- Review coordination by padre

**Phase 3: Integration & Review (Days 4-5)**
- Combine all content sections
- Review for consistency
- Quality assurance
- Format final document

**Phase 4: Publication & Reflection (Days 5-6)**
- Finalize newsletter
- Distribute to team
- Reflect on process
- Identify improvements

---

## Test Participants

### Core Team
- **FRBG/cityhall** (Agent 9, Loop 71) - Project Coordinator
  - Role: Overall project management
  - Responsibilities: Coordinate team, make final decisions, combine content
  - Decision Points: Format choice, deadline management, conflict resolution

- **FRBG/TeacherJohn** (Agent 8, Loop 70) - Education Lead
  - Role: Educational content contributor
  - Responsibilities: Create 200-word educational article
  - Decision Points: Topic selection, teaching approach

- **FRBG/zhou** (Agent 12, Loop 74) - Cultural Correspondent
  - Role: Cultural perspective contributor
  - Responsibilities: Create 150-word cultural insights
  - Decision Points: Topic relevance, cultural angle

- **FRBG/padre** (Agent 10, Loop 72) - Quality Reviewer
  - Role: Review and approve final content
  - Responsibilities: Quality check, consistency review, final approval
  - Decision Points: Accept/reject content, suggest improvements

### Supporting Team
- **FRBG/maria** (Agent 11, Loop 73) - Community Reporter
  - Role: Community updates contributor (optional)
  - Responsibilities: Brief community updates if time permits

---

## Success Criteria

### 1. Team Collaboration (40 points)

**Communication Quality (15 points)**
- ✓ All assigned agents respond to project kick-off (5 pts)
- ✓ Agents ask clarifying questions when needed (5 pts)
- ✓ Status updates shared proactively (5 pts)

**Coordination Effectiveness (15 points)**
- ✓ Clear role understanding demonstrated (5 pts)
- ✓ Dependencies identified and managed (5 pts)
- ✓ Handoffs executed smoothly (5 pts)

**Responsiveness (10 points)**
- ✓ Agents respond within 1 day of receiving messages (5 pts)
- ✓ Action items completed within assigned timeframe (5 pts)

### 2. Decision Making (30 points)

**Planning Decisions (10 points)**
- ✓ Newsletter format decided collectively (5 pts)
- ✓ Rationale provided for format choice (5 pts)

**Content Decisions (10 points)**
- ✓ Topics selected appropriately for audience (5 pts)
- ✓ Content length adheres to guidelines (5 pts)

**Conflict Resolution (10 points)**
- ✓ Disagreements handled constructively (5 pts)
- ✓ Consensus reached on contested items (5 pts)

### 3. Project Thinking (30 points)

**Planning & Breakdown (10 points)**
- ✓ Project broken into clear phases (5 pts)
- ✓ Dependencies identified correctly (5 pts)

**Execution Management (10 points)**
- ✓ Work progresses through planned phases (5 pts)
- ✓ Deadlines tracked and met (5 pts)

**Reflection & Learning (10 points)**
- ✓ Process reflections documented (5 pts)
- ✓ Improvements identified for future projects (5 pts)

### 4. Deliverables (Bonus +20 points)

**Content Quality**
- ✓ Educational article completed (5 pts)
- ✓ Cultural insights completed (5 pts)
- ✓ Final newsletter combined and formatted (5 pts)
- ✓ Quality review conducted with feedback (5 pts)

**Total Possible Score: 120 points**

**Pass Threshold: 70 points (58%)**

---

## Test Execution

### Initial Message (Kick-off)

**From:** FRBG/padre
**To:** FRBG/cityhall
**Subject:** New Project: FRBG Monthly Newsletter - November Edition

**Message:**
```
Dear Cityhall,

I am initiating a new community project: the FRBG Monthly Newsletter for November.

PROJECT OBJECTIVE:
Create a comprehensive newsletter covering education, culture, and community updates.

TEAM ASSIGNMENTS:
- You (cityhall): Project Coordinator - manage timeline, coordinate team, combine final content
- FRBG/TeacherJohn: Education Lead - 200-word educational article
- FRBG/zhou: Cultural Correspondent - 150-word cultural insights
- FRBG/maria: Community Reporter - brief updates (if time permits)
- I (padre): Quality Reviewer - final review and approval

YOUR TASKS:
1. Coordinate with the team to decide newsletter format and structure
2. Set clear deadlines for each phase
3. Collect content from contributors
4. Combine into unified newsletter
5. Submit to me for final review

DECISION POINTS:
- Newsletter format (sections, order, tone)
- Deadline management
- Content integration approach

TIMELINE: Complete within 6 days
DELIVERABLE: Unified newsletter document sent to me for approval

Please acknowledge receipt and share your initial project plan with the team.

Best regards,
Padre
```

### Monitoring Script

A Python script will:
1. Track message exchanges between agents
2. Monitor file creation in agent directories
3. Evaluate decision-making through message content analysis
4. Score collaboration based on success criteria
5. Generate automated test report

### Evaluation Checkpoints

**Day 1 Checkpoint:**
- ✓ Cityhall acknowledges project
- ✓ Initial plan created
- ✓ Team members contacted

**Day 2 Checkpoint:**
- ✓ Format decisions made
- ✓ Content creation started
- ✓ Progress updates shared

**Day 4 Checkpoint:**
- ✓ Content pieces completed
- ✓ Integration started
- ✓ Issues/blockers identified

**Day 6 Checkpoint:**
- ✓ Final newsletter completed
- ✓ Review conducted
- ✓ Reflections documented

---

## Test Data Collection

### Message Exchange Metrics
- Total messages sent/received per agent
- Average response time
- Message sentiment (positive/negative/neutral)
- Clarity score (based on keyword analysis)

### File System Metrics
- Files created per agent
- Newsletter draft versions
- Review documents
- Reflection files

### Decision Tracking
- Format choice documented (Y/N)
- Rationale provided (Y/N)
- Team consensus reached (Y/N)
- Conflicts handled constructively (Y/N)

### Project Thinking Indicators
- Project plan file exists (Y/N)
- Phases clearly defined (Y/N)
- Dependencies mapped (Y/N)
- Timeline tracked (Y/N)
- Retrospective conducted (Y/N)

---

## Automated Evaluation Criteria

### Natural Language Processing Checks

**Collaboration Indicators (regex patterns):**
```python
collaboration_patterns = [
    r"let[\'']s\s+coordinate",
    r"work\s+together",
    r"team\s+effort",
    r"collaborate\s+with",
    r"input\s+from",
    r"what\s+do\s+you\s+think",
    r"your\s+thoughts",
]
```

**Decision Making Indicators:**
```python
decision_patterns = [
    r"I\s+suggest|propose|recommend",
    r"option\s+(A|B|1|2)",
    r"best\s+approach",
    r"decided\s+to|decision\s+made",
    r"after\s+considering",
    r"pros\s+and\s+cons",
]
```

**Project Thinking Indicators:**
```python
project_thinking_patterns = [
    r"phase\s+\d+",
    r"milestone",
    r"dependency|depends\s+on",
    r"deadline|timeline|schedule",
    r"deliverable",
    r"next\s+steps",
    r"action\s+items",
]
```

### File System Checks

**Expected Files:**
```
/loops/71/filesystem/agentlife/work/newsletter_project/
├── project_plan.txt                 (cityhall - Day 1)
├── educational_article.txt          (TeacherJohn - Day 3)
├── cultural_insights.txt            (zhou - Day 3)
├── newsletter_draft_v1.txt          (cityhall - Day 4)
├── review_feedback.txt              (padre - Day 5)
├── newsletter_final.txt             (cityhall - Day 6)
└── project_retrospective.txt        (cityhall - Day 6)
```

### Scoring Algorithm

```python
def calculate_collaboration_score(messages, files, timeline):
    score = 0

    # Communication Quality (15 pts)
    if all_agents_responded(messages):
        score += 5
    if has_clarifying_questions(messages):
        score += 5
    if has_status_updates(messages):
        score += 5

    # Coordination Effectiveness (15 pts)
    if roles_understood(messages):
        score += 5
    if dependencies_identified(files):
        score += 5
    if smooth_handoffs(timeline):
        score += 5

    # Responsiveness (10 pts)
    if avg_response_time(messages) < 24:  # hours
        score += 5
    if tasks_completed_on_time(timeline):
        score += 5

    return score

def calculate_decision_score(messages, files):
    score = 0

    # Planning Decisions (10 pts)
    if format_decided(messages):
        score += 5
    if rationale_provided(messages):
        score += 5

    # Content Decisions (10 pts)
    if topics_appropriate(files):
        score += 5
    if content_length_correct(files):
        score += 5

    # Conflict Resolution (10 pts)
    if conflicts_handled_well(messages):
        score += 5
    if consensus_reached(messages):
        score += 5

    return score

def calculate_project_thinking_score(messages, files, timeline):
    score = 0

    # Planning & Breakdown (10 pts)
    if project_plan_exists(files):
        score += 5
    if dependencies_identified(files):
        score += 5

    # Execution Management (10 pts)
    if phases_followed(timeline):
        score += 5
    if deadlines_tracked(files):
        score += 5

    # Reflection & Learning (10 pts)
    if retrospective_exists(files):
        score += 5
    if improvements_identified(files):
        score += 5

    return score

def calculate_deliverable_bonus(files):
    bonus = 0

    if file_exists(files, 'educational_article.txt'):
        bonus += 5
    if file_exists(files, 'cultural_insights.txt'):
        bonus += 5
    if file_exists(files, 'newsletter_final.txt'):
        bonus += 5
    if file_exists(files, 'review_feedback.txt'):
        bonus += 5

    return bonus
```

---

## Test Variants

### Variant A: High Coordination (Default)
- All agents participate actively
- Clear coordinator role (cityhall)
- Structured phases

### Variant B: Self-Organization
- No explicit coordinator assigned
- Agents must self-organize
- Tests emergent leadership

### Variant C: Conflict Scenario
- Introduce conflicting requirements
- Tight deadline pressure
- Tests conflict resolution skills

### Variant D: Partial Team
- One agent unavailable (simulated)
- Tests adaptation and backup planning
- Requires workload redistribution

---

## Expected Outcomes

### Best Case Scenario (90-120 points)
- All agents communicate effectively
- Clear project plan created and followed
- Decisions made collectively with rationale
- Final newsletter delivered on time
- High quality content
- Productive retrospective

### Good Scenario (70-89 points)
- Most agents participate
- Basic project plan exists
- Key decisions documented
- Newsletter delivered (may be late)
- Acceptable content quality
- Some reflection on process

### Minimal Scenario (50-69 points)
- Some agents participate
- Loose coordination
- Few explicit decisions documented
- Partial deliverable
- Limited reflection

### Failure Scenario (<50 points)
- Poor communication
- No clear plan
- Decisions not documented
- Deliverable incomplete or missing
- No reflection

---

## Test Report Template

```markdown
# Team Collaboration Test Report

**Test Run:** {timestamp}
**Duration:** {days} days
**Scenario:** Community Newsletter Project

## Executive Summary

**Total Score:** {score}/120 points ({percentage}%)
**Result:** {PASS/FAIL}

### Score Breakdown
- Team Collaboration: {collab_score}/40
- Decision Making: {decision_score}/30
- Project Thinking: {project_score}/30
- Deliverable Bonus: {bonus_score}/20

## Detailed Findings

### Communication Analysis
- Messages exchanged: {message_count}
- Average response time: {avg_response_time} hours
- Participation rate: {participation_rate}%

### Decision Making
- Documented decisions: {decision_count}
- Rationale provided: {rationale_count}
- Consensus reached: {consensus_count}

### Project Execution
- Phases completed: {phases_completed}/{total_phases}
- Deliverables created: {deliverables_completed}/{total_deliverables}
- On-time completion: {ontime_percentage}%

### File Artifacts
{list_of_files_created}

### Message Timeline
{chronological_message_summary}

## Recommendations

{suggestions_for_improvement}

## Conclusion

{overall_assessment}
```

---

## Implementation Notes

### Prerequisites
1. All agents must have message exchange enabled
2. Agents must have access to shared work directories
3. Monitoring script must have read access to agent filesystems
4. Message database must be accessible

### Test Execution Steps

1. **Initialize Test**
   - Send kick-off message to cityhall
   - Start monitoring script
   - Begin 6-day cycle

2. **Monitor Progress**
   - Check messages daily
   - Track file creation
   - Record decision points

3. **Evaluate Results**
   - Run scoring algorithm
   - Generate test report
   - Identify improvement areas

4. **Document Findings**
   - Save test artifacts
   - Update test scenario if needed
   - Share insights with team

### Continuous Improvement

After each test run:
1. Analyze failure points
2. Adjust success criteria if too strict/lenient
3. Refine NLP patterns for better detection
4. Update scoring algorithm based on learnings
5. Add new test variants

---

## Future Enhancements

### Phase 2 Features
- Multi-project parallel execution tests
- Cross-team collaboration scenarios
- External constraint handling (budget, resources)
- Crisis scenario testing

### Advanced Metrics
- Sentiment analysis on messages
- Communication network graphs
- Leadership emergence detection
- Innovation/creativity scoring

### Integration
- Automated test scheduling (weekly/monthly)
- Regression testing for agent improvements
- A/B testing of different prompts/configurations
- Performance benchmarking over time

---

**Next Steps:**
1. Implement monitoring script
2. Create test message templates
3. Set up automated test execution
4. Run pilot test
5. Refine based on results
