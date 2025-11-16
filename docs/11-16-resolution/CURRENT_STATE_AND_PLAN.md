# LoopAI Agent Collaboration: Current State & Implementation Plan
**Date**: 2025-11-16
**Focus**: Achieve project-aware, self-sufficient agent behavior using existing LoopAI infrastructure

---

## Current State

### Test Results
**Collaboration Test Score**: 35/120 (29% success rate)
- Collaboration: 15/40
- Decision Making: 5/30
- Project Thinking: 15/30
- Deliverables: 0/20

**Root Cause**: Agents receive project messages but create no task files or deliverables.

### What's Working
✅ Message delivery system (agents receive messages)
✅ YAML loop execution (actions trigger successfully)
✅ Agent infrastructure (step_model, adapters, executors)
✅ Web API (execution endpoints respond)
✅ Basic protocols (READ_POSTS protocol is well-defined v2.0)

### What's Not Working
❌ **PRIMARY ISSUE**: Protocol output → file operations (LLM responses don't create task files)
❌ **SECONDARY**: Agents don't produce deliverables (0/20 points)

**Note**: Other potential issues (project awareness, dependencies, collaboration) are unverified. The test failure is specifically about **file creation from LLM responses**.

### Architecture Strengths
✅ **step_model** - Flexible workflow step definition
✅ **Adapters** - LLM, filesystem, HTTP integrations work
✅ **Executors** - LLM, bash, custom code execution functional
✅ **YAML loops** - Agent-agnostic, shared structure
✅ **Web API** - Async execution with progress tracking

**Conclusion**: Infrastructure is sufficient. Problem is in orchestration and context provision.

---

## What We Need to Build

### Gap Analysis

| Required Capability | Current State | What We Know | What's Missing |
|-------------------|---------------|--------------|----------------|
| **LLM Response → Files** | LlmExecutor exists, validates JSON, returns BroadcastData. FilesystemAdapter exists, expects `updated_files` array | ✅ Parsing works<br>✅ File executor exists<br>❌ No visibility into responses<br>❌ Unknown if LLM generates correct format | Logging (Phase 1 - done)<br>Protocol prompt verification<br>Response format validation |
| **Project Awareness** | Agents receive messages, read protocols, have self_identity.json files | ✅ Message delivery works<br>✅ Identity files exist<br>❌ No project state context<br>❌ No phase awareness | Context files system<br>Project state analyzer<br>Context injection in prompts |
| **Dependencies** | All agents run on same schedule, no blocking logic | ✅ All agents execute<br>❌ No wait/block mechanism<br>❌ No artifact tracking | Dependency detector<br>Artifact watcher<br>Blocking logic |
| **Smart Scheduling** | run_all_cycles.py triggers all actions for all agents | ✅ Reliable execution<br>❌ No state-based triggers<br>❌ Runs even when idle | State detection<br>Execution planner<br>Trigger conditions |
| **Collaboration** | Agents send/receive messages, READ_POSTS protocol exists | ✅ Messaging infrastructure works<br>❌ No collaboration-specific protocols<br>❌ No peer awareness | ASK_QUESTION protocol<br>SHARE_ARTIFACT protocol<br>Peer discovery |

### Differential Definition: What to Build

#### 1. IMMEDIATE PRIORITY: Fix File Creation (Week 1)

**Verified Problem**: Agents receive messages but create zero task files (0/20 deliverables).

**Phase 1: Visibility** (✅ COMPLETE)
- ✅ Add LLM response logging (step_model.py:309-326)
- ✅ Add file operation logging (step_model.py:355-388)
- ✅ Create diagnostic script (diagnostic_phase1.py)

**Phase 1b: Diagnosis** (NEXT)
- ⬜ Rebuild containers with logging
- ⬜ Run test to generate logs
- ⬜ Run diagnostic script
- ⬜ Identify exact failure point

**Phase 1c: Fix** (AFTER DIAGNOSIS)
Will be determined by diagnostic results. Possible fixes:
- **If LLM not generating `updated_files`**: Fix protocol prompts
- **If adapter not finding data**: Fix data structure or adapter logic
- **If validation failing**: Add format transformation layer

**Expected Impact**: 35% → 60% success (file creation working)

#### 2. Project Context System (Week 2)
**Problem**: Agents have no awareness of project state

**Build**:
```python
# agent_post/orchestrator/context_manager.py (NEW)
class ProjectContextManager:
    def analyze_project_state(self, project_id, agents)
    def detect_project_phase(self, artifacts)
    def calculate_progress(self, artifacts, phase)
    def build_agent_context(self, agent_id, project_state)
    def write_context_files(self, agent_id, context)
```

**Context Files Created**:
```
/agentlife/.context/
├── project_state.json      # Phase, progress, active agents
├── my_role.json           # Agent's specialization, current tasks
└── collaboration.json      # Dependencies, peer availability
```

**Deliverables**:
- ProjectContextManager class
- Context file schemas
- Updated YAML prompts (reference context)
- Context injection in orchestrator

**Expected Impact**: Agents become project-aware and self-conscious

#### 3. Intelligent Orchestrator (Week 3)
**Problem**: Fixed execution schedule, no state awareness

**Build**:
```python
# agent_post/orchestrator/intelligent_orchestrator.py (NEW)
class IntelligentOrchestrator:
    def analyze_agent_state(self, agent_id)
    def detect_state_changes(self, prev_state, curr_state)
    def plan_executions(self, agents, project_state)
    def execute_with_context(self, agent_id, action, context)
    def check_dependencies(self, agent_id, action)
    def monitor_blocked_agents(self)
```

**State-Based Triggers**:
- New message → READ_POSTS
- Task available → GET_WORK
- Task complete → VALIDATE_ACTION
- Dependency met → Unblock waiting agent
- Idle → Reduced polling frequency

**Deliverables**:
- IntelligentOrchestrator class
- State detection logic
- Execution planning system
- Enhanced run_all_cycles.py

**Expected Impact**: 60% → 80% success (efficient, dependency-aware)

#### 4. Dependency System (Week 4)
**Problem**: No way to express "frontend needs backend API first"

**Build**:
```python
# agent_post/orchestrator/dependency_detector.py (NEW)
class DependencyDetector:
    def detect_dependencies(self, agent_id, project_state)
    def artifact_exists(self, pattern, project_state)
    def get_blocking_dependencies(self, agent_id)
    def watch_for_artifact(self, pattern, on_available)
    def notify_dependents(self, artifact_created)
```

**Detection Method**: Filesystem analysis
- Read task descriptions for "requires" field
- Check if artifacts exist in work directories
- Block agents waiting for artifacts
- Unblock when artifacts appear

**Deliverables**:
- DependencyDetector class
- Artifact watcher system
- Blocking/unblocking logic
- Task schema with dependencies

**Expected Impact**: 80% → 90% success (correct execution order)

#### 5. Enhanced Protocols (Week 5)
**Problem**: Protocols don't leverage context or collaboration

**Build**:
- Update READ_POSTS protocol to create proper tasks
- Add ASK_QUESTION protocol for peer consultation
- Add SHARE_ARTIFACT protocol for deliverable notification
- Add REVIEW_WORK protocol for peer review

**Deliverables**:
- Enhanced protocol templates
- Collaboration protocol suite
- Protocol testing framework

**Expected Impact**: 90%+ success (full collaboration)

---

## Implementation Plan

### Phase 1: Visibility & Reliability (Week 1)
**Goal**: See what's failing and fix immediate issues

**Tasks**:
1. Add LLM response logging to looper
2. Implement response format validator
3. Build explicit file operation executor
4. Create diagnostic test script
5. Run diagnostics on current system
6. Fix identified issues

**Success Criteria**:
- Can see all LLM responses in logs
- Can identify exact failure points
- File operations execute reliably
- Test score: 35% → 60%

### Phase 2: Project Awareness (Week 2)
**Goal**: Agents understand project context

**Tasks**:
1. Build ProjectContextManager
2. Define context file schemas
3. Implement project phase detection
4. Create context injection system
5. Update YAML prompts to use context
6. Test context-aware execution

**Success Criteria**:
- Context files generated before execution
- Agents read and use context
- Prompts include project awareness
- Agents know their role and dependencies

### Phase 3: Intelligent Orchestration (Week 3)
**Goal**: Smart, state-driven execution

**Tasks**:
1. Build IntelligentOrchestrator
2. Implement state detection
3. Create execution planning logic
4. Add state-based triggers
5. Replace fixed cycles with smart scheduling
6. Test with calculator project

**Success Criteria**:
- Execution triggered by state changes
- No wasted loop runs
- Agents work when appropriate
- Test score: 60% → 80%

### Phase 4: Dependencies & Polish (Week 4-5)
**Goal**: Dependency awareness and full collaboration

**Tasks**:
1. Build DependencyDetector
2. Implement artifact tracking
3. Add blocking/unblocking logic
4. Create enhanced protocols
5. Full integration testing
6. Documentation and deployment

**Success Criteria**:
- Frontend waits for backend
- Agents coordinate correctly
- Full project completion
- Test score: 80% → 90%+

---

## Technical Approach

### Core Principle
**Use existing LoopAI infrastructure (step_model, adapters, executors) without changes.**

### Implementation Strategy

```
Existing Infrastructure (No Changes)
├── step_model (workflow steps)
├── adapters (LLM, filesystem, HTTP)
├── executors (llm, bash, custom)
└── web API (execution endpoints)

NEW: Intelligence Layer
├── Context Manager (writes context files)
├── Smart Orchestrator (decides when to run)
├── Dependency Detector (finds blockers)
└── Enhanced Protocols (leverage context)
```

### Key Insight
Agents become self-conscious by reading context files as **filesystem inputs** in their YAML loops.

```yaml
# READ_POSTS.yaml (enhanced)
session:
  loop:
    READ_POSTS:
      input:
        - filesystem:
            code_dir: /.context/project_state.json    # NEW
        - filesystem:
            code_dir: /.context/my_role.json         # NEW
        - filesystem:
            code_dir: /agentlife/skills/.../protocols
        - filesystem:
            code_dir: /agentlife/post/inbox/new
```

**No core changes needed!** Just smarter orchestration and context provision.

---

## Success Metrics

| Metric | Baseline | Week 1 | Week 2 | Week 3 | Week 4 | Target |
|--------|----------|--------|--------|--------|--------|---------|
| Test Score | 35% | 60% | 70% | 80% | 90% | 90%+ |
| Tasks Created | 0% | 50% | 70% | 80% | 90% | 90%+ |
| Deliverables | 0% | 30% | 50% | 70% | 90% | 90%+ |
| Collaboration Events | 4 | 8 | 12 | 18 | 25+ | 25+ |
| Agent Efficiency | 30% | 40% | 55% | 70% | 85% | 80%+ |

---

## Resource Requirements

### Code Components (New)
- `orchestrator/context_manager.py` (~200 lines)
- `orchestrator/intelligent_orchestrator.py` (~400 lines)
- `orchestrator/dependency_detector.py` (~200 lines)
- `loopai_src/core/looper/response_handler.py` (~150 lines)
- Enhanced `run_all_cycles.py` (~100 lines added)

**Total New Code**: ~1,050 lines
**Modified Code**: ~200 lines (looper enhancements)

### Testing
- Unit tests for each component
- Integration test with calculator project
- Performance testing

### Documentation
- API documentation for new components
- User guide for running orchestrated projects
- Migration guide from old to new orchestration

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| LLM responses unpredictable | Medium | High | Format validation + retry logic |
| Dependency detection incomplete | Low | Medium | Fallback to manual dependencies |
| Performance degradation | Low | Low | Optimize filesystem reads, cache state |
| Backward compatibility | Low | High | Old orchestration still works |

---

## Next Actions (Immediate)

### This Week
1. ✅ Document current state (this file)
2. ✅ Implement LLM response logging (step_model.py:309-388)
3. ✅ Create diagnostic test script (diagnostic_phase1.py)
4. ⬜ Rebuild containers with new logging
5. ⬜ Run diagnostics on failing test
6. ⬜ Analyze logs to find exact issue
7. ⬜ Implement fixes based on diagnostic results

### Next Week
1. ⬜ Build ProjectContextManager
2. ⬜ Define context file schemas
3. ⬜ Update YAML prompts
4. ⬜ Test context injection

### Following Weeks
1. ⬜ Build IntelligentOrchestrator
2. ⬜ Implement DependencyDetector
3. ⬜ Create enhanced protocols
4. ⬜ Full integration testing

---

## Conclusion

**Current state**: Infrastructure is solid, orchestration is naive.

**What to build**: Intelligence layer that provides context and schedules smartly.

**How to build**: Use existing API, add orchestrator + context manager.

**Expected outcome**: Self-conscious, project-aware agents achieving 90%+ collaboration success without core architecture changes.

**Timeline**: 4-5 weeks to full implementation.

**Next step**: Implement Phase 1 (Visibility & Reliability) this week.
