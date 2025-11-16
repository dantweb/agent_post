# Calculator Web App Project - Team Collaboration Test

**Version:** 1.0 (Negotiated)
**Date:** 2025-11-16
**Purpose:** Test 3-agent collaboration on simple software project
**Duration:** 3 days
**Pass Threshold:** 70/120 points

---

## Test Overview

This test validates whether agents can collaborate on a simple software development project, demonstrating:
1. **Team Collaboration** - Clear communication and coordination
2. **Correct Decisions** - Appropriate task division and working results
3. **Project Thinking** - Task breakdown, dependencies, timeline management

---

## Project Description

**Objective:** Build a simple calculator web application

**Components:**
- **Backend:** REST API with mathematical operation endpoints (add, subtract, multiply, divide)
- **Frontend:** HTML page with number inputs, operation buttons, and result display
- **Integration:** Combined project folder with both components working together

**Complexity Level:** Simple
- Clear requirements
- Well-defined interfaces (REST API)
- Verifiable outcome (calculator works or doesn't)
- Suitable for 3-day timeline

---

## Team Structure

### **3-Agent Core Team**

**FRBG/padre (Agent 10, Loop 72) - Project Manager**
- **Role:** Project initiator, coordinator, integrator
- **Responsibilities:**
  - Send project kick-off message
  - Define requirements and timeline
  - Coordinate between backend and frontend developers
  - Integrate both components into unified project
  - Test the integrated calculator
  - Document usage instructions
  - Conduct brief retrospective

**FRBG/TeacherJohn (Agent 8, Loop 70) - Backend Developer**
- **Role:** API developer
- **Responsibilities:**
  - Design and implement REST API
  - Create endpoints: `/add`, `/subtract`, `/multiply`, `/divide`
  - Define request/response format
  - Handle basic error cases (division by zero, invalid input)
  - Document API usage
  - Communicate API spec to frontend developer

**FRBG/zhou (Agent 12, Loop 74) - Frontend Developer**
- **Role:** UI developer
- **Responsibilities:**
  - Create HTML user interface
  - Implement input fields for numbers
  - Create operation buttons (+, -, ×, ÷)
  - Display calculation results
  - Call backend API endpoints
  - Handle user interactions
  - Coordinate with backend on API format

---

## Timeline (3 Days)

### **Day 1: Planning & Design**
**Objectives:**
- Project kick-off
- Requirements clarification
- Architecture decisions
- Task assignment
- API design agreement

**Expected Activities:**
- Padre sends project brief to team
- Team discusses technical approach
- Backend and frontend agree on API format
- Roles and deadlines confirmed

**Day 1 Success Criteria:**
- All 3 agents exchange messages
- Clear task division communicated
- Technical decisions documented (language, approach)
- Basic plan or task list created

---

### **Day 2: Development**
**Objectives:**
- Backend API implementation
- Frontend UI implementation
- Parallel development with coordination

**Expected Activities:**
- TeacherJohn creates backend code file
- Zhou creates frontend code file
- Status updates shared between developers
- API format confirmed/adjusted if needed

**Day 2 Success Criteria:**
- Backend code file exists with API endpoints
- Frontend code file exists with UI elements
- Progress updates shared
- No major blockers reported

---

### **Day 3: Integration & Testing**
**Objectives:**
- Combine backend and frontend
- Test integrated calculator
- Document usage
- Reflect on process

**Expected Activities:**
- Padre integrates both components
- Team tests calculator functionality
- Usage instructions created
- Brief retrospective documented

**Day 3 Success Criteria:**
- Combined project folder exists
- Integration attempted by padre
- Testing evidence present
- Retrospective notes created

---

## Success Criteria (70/120 points to pass)

### **1. Team Collaboration (40 points)**

**Communication Quality (15 points)**
- ✓ All 3 agents respond to project kick-off (5 pts)
- ✓ Agents ask clarifying questions when needed (5 pts)
- ✓ Status updates shared during development (5 pts)

**Coordination Effectiveness (15 points)**
- ✓ Clear role understanding demonstrated (5 pts)
- ✓ Dependencies identified (frontend needs backend API) (5 pts)
- ✓ Smooth handoffs (backend spec → frontend, code → integration) (5 pts)

**Responsiveness (10 points)**
- ✓ Agents respond within 1 day (5 pts)
- ✓ Code files created on schedule (5 pts)

---

### **2. Decision Making - Outcome Focused (30 points)**

**Task Division Decisions (15 points)**
- ✓ Clear assignment of backend/frontend roles (5 pts)
- ✓ Timeline/deadlines mentioned (5 pts)
- ✓ Dependencies communicated (5 pts)

**Technical Decisions (10 points)**
- ✓ Technology choices made (language, framework) (5 pts)
- ✓ API format agreed upon (5 pts)

**Working Result (5 points)**
- ✓ Integrated calculator produces correct results (5 pts)

---

### **3. Project Thinking (30 points)**

**Task Breakdown (10 points)**
- ✓ Project divided into clear tasks (5 pts)
- ✓ Task list or plan document created (5 pts)

**Dependency Management (10 points)**
- ✓ Frontend-backend dependency identified (5 pts)
- ✓ Coordination on API format (5 pts)

**Timeline Management (10 points)**
- ✓ Milestones mentioned (e.g., "backend done by Day 2") (5 pts)
- ✓ Progress tracking evident (status updates) (5 pts)

**Bonus: Risk Awareness (+5 points)**
- ✓ Potential blockers identified (e.g., "need API spec first")
- ✓ Solutions proposed

---

### **4. Deliverables - Complete Set Required (20 points bonus)**

**Required Files:**
1. **Project Plan** (5 pts)
   - `project_plan.txt` or similar
   - Lists tasks, roles, timeline

2. **Backend Code** (5 pts)
   - `calculator_api.py`, `server.js`, or similar
   - Contains API endpoint implementations
   - Located in backend/ or similar folder

3. **Frontend Code** (5 pts)
   - `calculator.html` and optional `calculator.js`
   - Contains UI elements and API calls
   - Located in frontend/ or similar folder

4. **Integration/README** (5 pts)
   - Combined project folder by padre
   - Usage instructions or README
   - Evidence of testing

**Optional Files (no points, but good to have):**
- Test results document
- Retrospective notes
- API documentation
- Code comments

---

## Test Execution Plan

### **Phased Approach with Daily Checkpoints**

This test uses active monitoring rather than passive observation, allowing us to:
- Learn about agent capabilities in real-time
- Debug issues as they occur
- Adjust if agents get stuck
- Document lessons for future config improvements

---

### **Day 1 Checkpoint**

**Time:** End of Day 1 (after message exchange cycle runs)

**What to Check:**
```bash
# 1. Check messages exchanged
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post
docker compose exec -T -w /app agent_post python3 -c "
from src.message_repo import message_repo
msgs = [m for m in message_repo.find_all() if 'calculator' in m.data.lower()]
print(f'Calculator project messages: {len(msgs)}')
for m in msgs:
    print(f'{m.from_address} → {m.to_address}: {m.data[:80]}...')
"

# 2. Check if padre sent kick-off
ls -lt /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/post/outbox/

# 3. Check if TeacherJohn and zhou received messages
ls -lt /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/70/filesystem/agentlife/post/inbox/
ls -lt /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/74/filesystem/agentlife/post/inbox/

# 4. Check for any planning documents
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/*/filesystem/agentlife/work -name "*plan*" -o -name "*calculator*" -mmin -1440
```

**Success Indicators:**
- ✓ At least 3-5 messages exchanged
- ✓ TeacherJohn and zhou acknowledged their roles
- ✓ Some mention of tasks or timeline
- ✓ Technical approach discussed (even if basic)

**Red Flags:**
- ❌ No responses from TeacherJohn or zhou
- ❌ No mention of planning or tasks
- ❌ Confusion about roles

**Actions if Red Flags:**
- Check message delivery (are inboxes empty?)
- Check READ_POSTS action ran successfully
- Consider sending follow-up from padre if no responses

---

### **Day 2 Checkpoint**

**Time:** End of Day 2 (after development should start)

**What to Check:**
```bash
# 1. Check for backend code file
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/70/filesystem/agentlife/work -type f -name "*.py" -o -name "*.js" -mtime -1

# 2. Check for frontend code file
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/74/filesystem/agentlife/work -type f -name "*.html" -o -name "*.js" -mtime -1

# 3. Check for status update messages
# (same message check as Day 1, look for progress mentions)

# 4. Check file contents (sample)
cat /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/70/filesystem/agentlife/work/calculator* 2>/dev/null | head -20
cat /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/74/filesystem/agentlife/work/calculator* 2>/dev/null | head -20
```

**Success Indicators:**
- ✓ Backend code file exists with some content
- ✓ Frontend code file exists with some content
- ✓ Status updates shared ("finished endpoints", "UI is done")
- ✓ Coordination messages about API format

**Red Flags:**
- ❌ No code files created
- ❌ Empty or stub files only
- ❌ No communication between developers
- ❌ One agent went silent

**Actions if Red Flags:**
- Check if agents are running (docker ps)
- Check if DO_ACTION is executing
- Verify agents have write permissions to work directory
- Consider extending timeline by 1 day

---

### **Day 3 Checkpoint & Final Evaluation**

**Time:** End of Day 3

**What to Check:**
```bash
# 1. Check for integration by padre
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/work -type f -mtime -1

# 2. Check for combined project folder
ls -R /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/work/calculator*

# 3. Check for README or usage instructions
find /Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/72/filesystem/agentlife/work -name "README*" -o -name "*instruction*"

# 4. Verify all required files exist
echo "Checking deliverables..."
test -f /path/to/project_plan.txt && echo "✓ Project plan" || echo "✗ Missing project plan"
test -f /path/to/backend_code && echo "✓ Backend code" || echo "✗ Missing backend"
test -f /path/to/frontend_code && echo "✓ Frontend code" || echo "✗ Missing frontend"
test -f /path/to/README && echo "✓ Integration docs" || echo "✗ Missing docs"
```

**Success Indicators:**
- ✓ Backend code complete with API endpoints
- ✓ Frontend code complete with UI
- ✓ Padre created combined project folder
- ✓ README or usage instructions present
- ✓ Evidence of testing

**Score Calculation:**
- Run automated scoring script (checks messages, files, content)
- Manual review of code quality
- Test if calculator actually works (if possible)

---

## Evaluation Rubric Details

### **Communication Analysis**

**Automated Checks:**
```python
# Count messages with calculator project keywords
project_messages = [m for m in messages if 'calculator' in m.data.lower()]

# Check agent participation
agents_who_responded = set(m.from_address for m in project_messages)
participation_score = len(agents_who_responded) * 5  # 5 pts per agent

# Check for questions (clarifying)
has_questions = any('?' in m.data for m in project_messages)
question_score = 5 if has_questions else 0

# Check for status updates
status_keywords = ['progress', 'done', 'finished', 'completed', 'working on']
has_updates = any(kw in m.data.lower() for m in project_messages for kw in status_keywords)
update_score = 5 if has_updates else 0
```

### **Code Quality Assessment**

**Backend Code Check:**
- Contains function/endpoint definitions
- Has 4 operations (add, subtract, multiply, divide)
- Basic structure is correct (even if not runnable)

**Frontend Code Check:**
- Contains HTML form elements
- Has input fields and buttons
- Attempts to call backend API
- Basic structure is correct

**Integration Check:**
- Files are in same directory or related structure
- README mentions both components
- Some attempt at connecting them

---

## Expected Outcomes by Performance Level

### **Excellent (90-120 points)**
- All agents communicate actively
- Detailed project plan created
- Complete, well-structured code for both components
- Successful integration with working calculator
- Clear documentation
- Productive retrospective

### **Good (70-89 points) - PASS**
- Most agents participate
- Basic project plan evident
- Code files created for both components
- Integration attempted, may have issues
- Basic documentation
- Some reflection

### **Needs Improvement (50-69 points) - FAIL**
- Limited participation
- Minimal planning
- Incomplete code files
- No integration
- Little documentation

### **Poor (<50 points) - FAIL**
- Poor communication
- No clear plan
- Missing or stub code only
- No integration attempt
- No documentation

---

## Initial Kick-off Message

**From:** FRBG/padre
**To:** FRBG/TeacherJohn, FRBG/zhou
**Subject:** New Project: Simple Calculator Web Application

```
Hello team,

I'm initiating a new 3-day project to build a simple calculator web application.

PROJECT OBJECTIVE:
Create a working calculator with backend API and frontend UI that can perform basic mathematical operations.

TEAM ROLES:
- FRBG/TeacherJohn: Backend Developer - Create REST API with calculation endpoints
- FRBG/zhou: Frontend Developer - Create HTML UI with buttons and display
- Me (FRBG/padre): Project Manager - Coordinate team, integrate components, test result

REQUIREMENTS:

Backend (TeacherJohn):
- Build REST API with endpoints for: add, subtract, multiply, divide
- Accept two numbers as input
- Return calculation result
- Handle basic errors (division by zero, invalid input)
- Document API format for frontend

Frontend (zhou):
- Create HTML page with:
  - Two number input fields
  - Operation buttons (+, -, ×, ÷)
  - Result display area
- Call backend API when user clicks button
- Display result to user

Integration (padre):
- Combine backend and frontend into one project
- Test that calculator works end-to-end
- Create usage instructions

TIMELINE:
- Day 1: Planning, design decisions, API format agreement
- Day 2: Development (backend and frontend in parallel)
- Day 3: Integration, testing, documentation

SUCCESS CRITERIA:
- Working calculator that can add, subtract, multiply, and divide
- Clean, understandable code
- Documentation of how to run/use it

FIRST STEPS:
1. Please acknowledge receipt and confirm your role
2. TeacherJohn: Propose API format (endpoints, request/response structure)
3. Zhou: Once API format is clear, start frontend design
4. Both: Share progress updates and any blockers

Let's build something great together!

Best regards,
Padre
Project Manager
```

---

## Post-Test Analysis Plan

### **If Test Passes (70+ points):**

**Document successes:**
- Which communication patterns worked
- How agents divided tasks
- What decisions were made well
- Code quality observations

**Share findings:**
- Update test report with results
- Identify best practices observed
- Note any surprising capabilities

---

### **If Test Fails (<70 points):**

**Analyze failure points:**

1. **Communication Breakdown**
   - Did agents respond to messages?
   - Were messages clear and actionable?
   - Did READ_POSTS action work correctly?

2. **Task Execution Issues**
   - Did agents understand their roles?
   - Were tasks too complex?
   - Did agents create files in correct locations?

3. **Coordination Problems**
   - Did agents wait for dependencies?
   - Was there confusion about API format?
   - Did integration not happen?

**Potential Adjustments:**

**Agent Configuration Changes:**
```yaml
# Example: Enhance agent prompts to emphasize collaboration

# In TeacherJohn's config (Loop 70)
GET_WORK:
  action:
    executor: gpt
    system_prompt: |
      You are a backend developer working on a team project.

      COLLABORATION GUIDELINES:
      - Check your inbox for project assignments
      - Communicate your progress to the team
      - Ask clarifying questions if requirements unclear
      - Document your work for other team members
      - Share technical decisions and rationale

      When assigned a backend task:
      1. Confirm you understand the requirements
      2. Design API structure and share with frontend team
      3. Implement the API code
      4. Test your endpoints
      5. Document usage for integration
```

**Message Template Changes:**
- Make kick-off message more explicit
- Add example API format
- Include file location instructions
- Provide code templates

**Test Adjustments:**
- Simplify to 2-agent test first
- Reduce scope (just add/subtract)
- Extend timeline to 4-5 days
- Lower pass threshold temporarily

---

## Lessons Learned Template

After test completion, document:

**What Worked:**
- [Successful behaviors observed]

**What Didn't Work:**
- [Failed or problematic behaviors]

**Surprises:**
- [Unexpected agent capabilities or limitations]

**Recommendations:**
- [Changes to make for future tests]

**Agent Config Changes Needed:**
- [Specific YAML or prompt modifications]

---

**Test Created:** 2025-11-16
**Status:** Ready for execution
**Next Steps:** Create kick-off message, monitor Day 1 checkpoint

---

## Quick Reference Commands

```bash
# Send kick-off message
cd /Users/dantweb/dantweb/l-sdk-27a/agent_post
python run_collaboration_test.py --send-only --scenario calculator

# Check Day 1 progress
python run_collaboration_test.py --checkpoint 1 --scenario calculator

# Check Day 2 progress
python run_collaboration_test.py --checkpoint 2 --scenario calculator

# Final evaluation
python run_collaboration_test.py --evaluate --scenario calculator
```
