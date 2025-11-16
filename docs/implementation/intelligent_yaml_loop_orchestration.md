# Intelligent YAML-Loop Orchestration for LoopAI Agents

## Understanding the Current Architecture

### Key Principle
**All agents share the SAME set of YAML loops** - they are agent-agnostic. The difference is in:
- Agent's `/self/self_identity.json` (who they are)
- Agent's `/skills/` (what protocols they follow)
- Execution context (what messages they receive, what work is available)

### Current Orchestration (run_all_cycles.py)

```python
# Current approach: Fixed sequence, all agents together
for day in range(days):
    for action in ['READ_POSTS', 'GET_WORK', 'PREPARE_ACTION',
                   'DO_ACTION', 'VALIDATE_ACTION', ...]:
        for agent in all_agents:
            trigger_action(agent, action)
        wait(15_seconds)
```

**Problems**:
1. **No awareness of agent state** - Run loops even if agent has no work
2. **No project awareness** - Doesn't understand project phase or dependencies
3. **Wasteful execution** - Agents with no new messages still run READ_POSTS
4. **Rigid timing** - 15 second intervals regardless of actual needs
5. **No self-consciousness** - Agents don't know their role in larger project

## Solution: Intelligent Orchestration Layer

### Core Concept

Keep YAML loops identical across agents, but add an **Intelligent Orchestrator** that:
1. **Monitors agent state** - Only run loops when state changes warrant it
2. **Understands project context** - Knows what phase project is in
3. **Detects dependencies** - Waits for prerequisites before running loops
4. **Adapts timing** - Runs loops at appropriate frequency
5. **Provides context** - Injects project awareness into loop execution

## Architecture: Smart Orchestration Layer

```
┌────────────────────────────────────────────────────┐
│        Intelligent Orchestration Layer             │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐│
│  │State Monitor │  │Project Aware │  │Dependency││
│  │              │  │Engine        │  │Resolver  ││
│  └──────────────┘  └──────────────┘  └──────────┘│
│                                                     │
│  ┌──────────────────────────────────────────────┐ │
│  │          Execution Scheduler                  │ │
│  │  - When to run which agent's loops           │ │
│  │  - What context to provide                   │ │
│  │  - How frequently to poll                    │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
   ┌────────┐     ┌────────┐     ┌────────┐
   │Agent 1 │     │Agent 2 │     │Agent 3 │
   │YAML    │     │YAML    │     │YAML    │
   │Loops   │     │Loops   │     │Loops   │
   └────────┘     └────────┘     └────────┘
    (Same structure for all agents)
```

## Implementation: Intelligent Orchestrator

### 1. State-Based Execution Triggers

```python
class StateBasedOrchestrator:
    """Run loops only when agent state changes warrant it"""

    def __init__(self):
        self.agent_states = {}  # agent_id → current state
        self.state_triggers = self.define_triggers()

    def define_triggers(self):
        """Define what state changes trigger which loops"""
        return {
            'new_message_received': {
                'triggers': ['READ_POSTS', 'GET_WORK'],
                'priority': 'high'
            },
            'task_completed': {
                'triggers': ['VALIDATE_ACTION', 'GET_WORK'],
                'priority': 'medium'
            },
            'work_available': {
                'triggers': ['GET_WORK', 'PREPARE_ACTION'],
                'priority': 'high'
            },
            'waiting_for_dependency': {
                'triggers': [],  # Don't run anything, agent is blocked
                'priority': 'low'
            },
            'artifact_created': {
                'triggers': ['VALIDATE_ACTION', 'NOTIFY_PEERS'],
                'priority': 'medium'
            },
            'question_received': {
                'triggers': ['READ_POSTS', 'RESPOND_TO_QUESTION'],
                'priority': 'high'
            },
            'no_work_idle': {
                'triggers': ['READ_POSTS'],  # Only check for new messages
                'frequency': 'every_30_minutes'  # Reduced frequency
            }
        }

    def monitor_agent_state(self, agent_id):
        """Continuously monitor agent for state changes"""
        current_state = self.get_agent_state(agent_id)
        previous_state = self.agent_states.get(agent_id, {})

        # Detect state changes
        changes = self.detect_state_changes(previous_state, current_state)

        if changes:
            # Determine which loops to trigger
            loops_to_run = self.determine_loops_to_run(changes)

            # Execute with context
            for loop in loops_to_run:
                self.execute_loop_with_context(
                    agent_id,
                    loop,
                    context=self.build_context(agent_id, loop, changes)
                )

        self.agent_states[agent_id] = current_state

    def get_agent_state(self, agent_id):
        """Get current agent state by checking filesystem"""
        base_path = f"/var/users/1/loops/{agent_id}/filesystem/agentlife"

        return {
            'inbox_count': self.count_files(f"{base_path}/post/inbox/new"),
            'tasks_available': self.count_files(f"{base_path}/tasks/new"),
            'tasks_active': self.count_files(f"{base_path}/tasks/active"),
            'work_artifacts': self.count_files(f"{base_path}/work"),
            'waiting_for': self.check_dependencies(agent_id),
            'last_activity': self.get_last_activity_time(agent_id),
            'energy_level': self.calculate_energy_level(agent_id)
        }

    def detect_state_changes(self, previous, current):
        """Identify meaningful state changes"""
        changes = []

        # New messages arrived
        if current['inbox_count'] > previous.get('inbox_count', 0):
            changes.append({
                'type': 'new_message_received',
                'count': current['inbox_count'] - previous.get('inbox_count', 0)
            })

        # New tasks available
        if current['tasks_available'] > previous.get('tasks_available', 0):
            changes.append({
                'type': 'work_available',
                'count': current['tasks_available']
            })

        # Task completed
        if current['tasks_active'] < previous.get('tasks_active', 0):
            changes.append({
                'type': 'task_completed',
                'completed': previous.get('tasks_active', 0) - current['tasks_active']
            })

        # New artifact created
        if current['work_artifacts'] > previous.get('work_artifacts', 0):
            changes.append({
                'type': 'artifact_created',
                'count': current['work_artifacts'] - previous.get('work_artifacts', 0)
            })

        # Became idle
        if (current['tasks_available'] == 0 and
            current['tasks_active'] == 0 and
            current['inbox_count'] == 0):
            changes.append({'type': 'no_work_idle'})

        # Dependencies met
        if previous.get('waiting_for') and not current['waiting_for']:
            changes.append({
                'type': 'dependency_met',
                'was_waiting_for': previous['waiting_for']
            })

        return changes
```

### 2. Project-Aware Context Injection

```python
class ProjectContextEngine:
    """Understand project state and inject context into loop execution"""

    def __init__(self):
        self.project_state = {}
        self.project_phases = ['kickoff', 'design', 'implementation',
                               'integration', 'testing', 'completion']

    def analyze_project_state(self, project_id):
        """Analyze current project state across all agents"""

        # Gather artifacts from all agents
        artifacts = self.gather_all_artifacts(project_id)

        # Determine project phase
        phase = self.determine_project_phase(artifacts)

        # Identify blockers and dependencies
        blockers = self.identify_blockers(artifacts)

        # Calculate progress
        progress = self.calculate_progress(artifacts, phase)

        return {
            'project_id': project_id,
            'phase': phase,
            'progress': progress,
            'artifacts': artifacts,
            'blockers': blockers,
            'active_agents': self.get_active_agents(project_id),
            'completed_milestones': self.get_completed_milestones(artifacts),
            'pending_work': self.get_pending_work(project_id)
        }

    def determine_project_phase(self, artifacts):
        """Determine what phase project is in based on artifacts"""

        has_requirements = any('requirement' in a for a in artifacts)
        has_design = any(a.endswith('_spec.md') or a.endswith('_design.md')
                        for a in artifacts)
        has_code = any(a.endswith('.py') or a.endswith('.js') or a.endswith('.html')
                      for a in artifacts)
        has_integration = any('integrated' in a or 'combined' in a
                            for a in artifacts)
        has_tests = any('test' in a for a in artifacts)

        if has_tests:
            return 'testing'
        elif has_integration:
            return 'integration'
        elif has_code:
            return 'implementation'
        elif has_design:
            return 'design'
        elif has_requirements:
            return 'kickoff'
        else:
            return 'unknown'

    def build_execution_context(self, agent_id, action, project_state):
        """Build rich context for loop execution"""

        agent_identity = self.load_agent_identity(agent_id)

        context = {
            # Agent awareness
            'agent': {
                'id': agent_id,
                'specialization': agent_identity['specialization'],
                'expertise': agent_identity['expertise'],
                'current_workload': self.get_workload(agent_id)
            },

            # Project awareness
            'project': {
                'phase': project_state['phase'],
                'progress': project_state['progress'],
                'active_agents': project_state['active_agents'],
                'blockers': project_state['blockers']
            },

            # Action-specific context
            'action_context': self.get_action_context(action, agent_id, project_state),

            # Collaboration context
            'collaboration': {
                'peers': self.get_peer_agents(agent_id, project_state),
                'dependencies': self.get_my_dependencies(agent_id, project_state),
                'dependents': self.get_who_depends_on_me(agent_id, project_state),
                'available_for_questions': self.get_available_experts(agent_id)
            },

            # Temporal context
            'timing': {
                'project_deadline': project_state.get('deadline'),
                'my_time_spent': self.get_time_spent(agent_id),
                'estimated_remaining': self.estimate_remaining_work(agent_id)
            }
        }

        return context

    def inject_context_into_loop(self, agent_id, action, context):
        """Inject context into YAML loop execution"""

        # Create context file that loop can read
        context_file = f"/var/users/1/loops/{agent_id}/filesystem/agentlife/.context/execution_context.json"

        os.makedirs(os.path.dirname(context_file), exist_ok=True)

        with open(context_file, 'w') as f:
            json.dump(context, f, indent=2)

        # YAML loop can now read this context
        # Protocols can reference: "Read /.context/execution_context.json for project awareness"
```

### 3. Dependency-Aware Scheduling

```python
class DependencyAwareScheduler:
    """Schedule loop execution based on inter-agent dependencies"""

    def __init__(self):
        self.dependency_graph = {}
        self.waiting_agents = {}

    def define_dependencies(self, project_config):
        """Define which agents depend on which artifacts"""

        # Example: Frontend depends on Backend API spec
        dependencies = {
            'FRBG/zhou': {
                'needs': [
                    {
                        'artifact': 'api_specification.md',
                        'from_agent': 'FRBG/TeacherJohn',
                        'for_action': 'DESIGN_UI'
                    }
                ]
            },
            'FRBG/padre': {
                'needs': [
                    {
                        'artifact': '*.py',  # Backend code
                        'from_agent': 'FRBG/TeacherJohn',
                        'for_action': 'INTEGRATE'
                    },
                    {
                        'artifact': '*.html',  # Frontend code
                        'from_agent': 'FRBG/zhou',
                        'for_action': 'INTEGRATE'
                    }
                ]
            }
        }

        return dependencies

    def check_dependencies_met(self, agent_id, action):
        """Check if agent can proceed with action"""

        dependencies = self.dependency_graph.get(agent_id, {}).get('needs', [])

        for dep in dependencies:
            if dep['for_action'] == action:
                # Check if required artifact exists
                if not self.artifact_exists(dep['artifact'], dep['from_agent']):
                    return False, f"Waiting for {dep['artifact']} from {dep['from_agent']}"

        return True, None

    def schedule_with_dependencies(self, agents, action):
        """Schedule action execution respecting dependencies"""

        ready_agents = []
        blocked_agents = []

        for agent_id in agents:
            can_proceed, reason = self.check_dependencies_met(agent_id, action)

            if can_proceed:
                ready_agents.append(agent_id)
            else:
                blocked_agents.append({
                    'agent_id': agent_id,
                    'reason': reason
                })
                self.waiting_agents[agent_id] = reason

        # Execute ready agents
        for agent_id in ready_agents:
            self.execute_agent_action(agent_id, action)

        # Monitor blocked agents - re-check when dependencies might be met
        if blocked_agents:
            self.monitor_blocked_agents(blocked_agents)

    def monitor_blocked_agents(self, blocked_agents):
        """Monitor and unblock agents when dependencies are met"""

        # This runs in background, checking periodically
        for blocked in blocked_agents:
            # Set up file watcher for required artifacts
            self.watch_for_artifact(
                blocked['agent_id'],
                on_available=lambda agent_id: self.unblock_and_execute(agent_id)
            )
```

### 4. Adaptive Loop Frequency

```python
class AdaptiveFrequencyScheduler:
    """Adjust loop execution frequency based on agent activity"""

    def __init__(self):
        self.agent_frequencies = {}  # agent_id → frequency config

    def calculate_optimal_frequency(self, agent_id):
        """Calculate how often to run agent's loops"""

        activity_level = self.get_activity_level(agent_id)
        workload = self.get_workload(agent_id)
        urgency = self.get_urgency(agent_id)

        if activity_level == 'high' and workload > 3:
            # Active work, check frequently
            return {
                'READ_POSTS': 30,  # seconds
                'GET_WORK': 60,
                'CHECK_DEPENDENCIES': 30
            }

        elif activity_level == 'medium':
            # Moderate activity
            return {
                'READ_POSTS': 120,  # 2 minutes
                'GET_WORK': 300,  # 5 minutes
                'CHECK_DEPENDENCIES': 180
            }

        else:
            # Idle, check infrequently
            return {
                'READ_POSTS': 600,  # 10 minutes
                'GET_WORK': 1800,  # 30 minutes
                'CHECK_DEPENDENCIES': 600
            }

    def dynamic_polling(self, agent_id):
        """Dynamically adjust polling based on recent activity"""

        while True:
            frequencies = self.calculate_optimal_frequency(agent_id)

            for action, interval in frequencies.items():
                # Schedule next check
                self.schedule_action(agent_id, action, after_seconds=interval)

            # Recalculate frequencies every 5 minutes
            time.sleep(300)
```

## Enhanced YAML Loop Structure

### YAML Loops Stay The Same, But Read Context

```yaml
# READ_POSTS.yaml (same for all agents)
session:
  name: "READ_POSTS"
  loop:
    READ_CONTEXT:
      description: "Load execution context"
      type: filesystem
      input:
        - filesystem:
            code_dir: /.context/execution_context.json
      action:
        executor: json
        # Loads project awareness, agent role, dependencies, etc.

    READ_POSTS:
      description: "Read and process messages"
      type: llm
      input:
        - filesystem:
            code_dir: /.context/execution_context.json  # NOW HAS CONTEXT
        - filesystem:
            code_dir: /agentlife/skills/project_thinking/protocols/read_posts
        - filesystem:
            code_dir: /agentlife/post/inbox/new
      action:
        executor: llm
        model: deepseek-reasoner
        prompt: |
          You are {{agent.specialization}} working on a {{project.phase}} phase project.

          PROJECT CONTEXT:
          - Phase: {{project.phase}}
          - Progress: {{project.progress}}%
          - Your role: {{agent.specialization}}
          - Active collaborators: {{collaboration.peers}}

          DEPENDENCIES:
          {{#if collaboration.dependencies}}
          You are waiting for:
          {{#each collaboration.dependencies}}
          - {{this.artifact}} from {{this.agent}}
          {{/each}}
          {{/if}}

          {{#if collaboration.dependents}}
          Others are waiting for your:
          {{#each collaboration.dependents}}
          - {{this.artifact}} needed by {{this.agent}}
          {{/each}}
          {{/if}}

          Now read your messages and extract work items relevant to your role
          and current project phase. Follow the protocol in the requestContent.
```

## Orchestration Runner: Enhanced run_all_cycles.py

```python
#!/usr/bin/env python3
"""
Intelligent orchestration of agent YAML loops
"""

class IntelligentOrchestrator:
    """Smart orchestration layer for agent YAML loops"""

    def __init__(self):
        self.state_monitor = StateBasedOrchestrator()
        self.context_engine = ProjectContextEngine()
        self.dependency_scheduler = DependencyAwareScheduler()
        self.frequency_scheduler = AdaptiveFrequencyScheduler()

        self.agents = self.discover_agents()
        self.projects = self.discover_active_projects()

    def run_intelligent_orchestration(self, duration_hours=72):
        """
        Run intelligent orchestration instead of fixed cycles

        Key differences from old approach:
        1. Event-driven, not time-driven
        2. Context-aware execution
        3. Dependency-respecting
        4. Adaptive frequencies
        """

        start_time = time.time()

        # Start background monitors
        self.start_state_monitors()
        self.start_project_monitors()
        self.start_dependency_monitors()

        print("🚀 Intelligent orchestration started")

        while (time.time() - start_time) < (duration_hours * 3600):
            # Main orchestration loop

            # 1. Update project contexts
            for project_id in self.projects:
                project_state = self.context_engine.analyze_project_state(project_id)
                self.context_engine.update_context_files(project_state)

            # 2. Check each agent's state and determine what to run
            for agent_id in self.agents:
                # Get current state
                current_state = self.state_monitor.get_agent_state(agent_id)

                # Detect changes
                changes = self.state_monitor.detect_state_changes(
                    self.state_monitor.agent_states.get(agent_id, {}),
                    current_state
                )

                # If meaningful changes occurred, run appropriate loops
                if changes:
                    self.handle_agent_state_changes(agent_id, changes)

                # Update state
                self.state_monitor.agent_states[agent_id] = current_state

            # 3. Check blocked agents - maybe dependencies are now met
            self.check_blocked_agents()

            # 4. Adjust polling frequencies
            self.update_frequencies()

            # Sleep before next orchestration cycle
            time.sleep(10)  # Check every 10 seconds

        print("✅ Orchestration completed")

    def handle_agent_state_changes(self, agent_id, changes):
        """Handle detected state changes for an agent"""

        for change in changes:
            change_type = change['type']

            # Determine which loops to run
            triggers = self.state_monitor.state_triggers.get(change_type, {})
            loops_to_run = triggers.get('triggers', [])

            if not loops_to_run:
                continue

            # Build context
            project_state = self.context_engine.get_project_state_for_agent(agent_id)
            context = self.context_engine.build_execution_context(
                agent_id,
                loops_to_run[0],  # Primary action
                project_state
            )

            # Inject context
            self.context_engine.inject_context_into_loop(agent_id, context)

            # Check dependencies before execution
            for loop in loops_to_run:
                can_execute, reason = self.dependency_scheduler.check_dependencies_met(
                    agent_id,
                    loop
                )

                if can_execute:
                    print(f"▶️  {agent_id} → {loop} (triggered by {change_type})")
                    self.execute_loop(agent_id, loop, context)
                else:
                    print(f"⏸️  {agent_id} → {loop} blocked: {reason}")
                    self.dependency_scheduler.waiting_agents[agent_id] = reason

    def execute_loop(self, agent_id, action, context):
        """Execute a YAML loop with context"""

        # Trigger via API
        execution_id = self.trigger_agent_action(agent_id, action)

        # Track execution
        self.running_executions[execution_id] = {
            'agent_id': agent_id,
            'action': action,
            'context': context,
            'started_at': time.time()
        }

        return execution_id
```

## Key Improvements

### 1. State-Driven vs Time-Driven

**Before**: Run loops every 15 seconds regardless of need
**After**: Run loops when agent state changes warrant it

### 2. Project Awareness

**Before**: Agents have no idea what project phase they're in
**After**: Every loop execution receives rich project context

### 3. Dependency Awareness

**Before**: Frontend starts before backend API exists
**After**: Frontend automatically waits for backend artifacts

### 4. Adaptive Frequency

**Before**: Fixed 15-second intervals
**After**: Busy agents polled every 30 seconds, idle agents every 10 minutes

### 5. Self-Consciousness

**Before**: Agents blindly execute actions
**After**: Agents know their role, project phase, who they're collaborating with, what's blocking them

## Expected Impact

| Metric | Current | With Intelligent Orchestration |
|--------|---------|-------------------------------|
| Wasted loop executions | ~80% | ~20% |
| Time to task completion | N/A | -50% |
| Agent idle time | ~70% | ~30% |
| Successful collaborations | 35% | 80-90% |
| Resource efficiency | Low | High |

## Implementation Roadmap

### Phase 1: State Monitoring (Week 1)
- Implement StateBasedOrchestrator
- Add filesystem state detection
- Create state change triggers

### Phase 2: Context Engine (Week 2)
- Build ProjectContextEngine
- Implement project phase detection
- Create context injection system

### Phase 3: Dependency Scheduler (Week 3)
- Implement DependencyAwareScheduler
- Add artifact watching
- Create blocking/unblocking system

### Phase 4: Adaptive Frequency (Week 4)
- Build AdaptiveFrequencyScheduler
- Implement activity level detection
- Create dynamic polling

### Phase 5: Integration & Testing (Week 5)
- Integrate all components
- Test with calculator project
- Measure improvements

## Conclusion

This approach:
✅ Keeps YAML loops identical across agents (agent-agnostic)
✅ Makes orchestration intelligent and context-aware
✅ Enables project-conscious behavior
✅ Respects dependencies naturally
✅ Optimizes resource usage
✅ Maintains architectural simplicity

The key insight: **Don't change WHAT agents do (YAML loops), change WHEN and HOW we run them (orchestration).**
