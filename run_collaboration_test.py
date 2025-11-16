#!/usr/bin/env python3
"""
Automated Team Collaboration Test Runner

This script executes and evaluates the multi-agent collaboration test scenario
where agents work together on a calculator web app project.

Usage:
    python run_collaboration_test.py --days 3 --output test_report.md
"""

import os
import sys
import json
import time
import re
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.message_repo import message_repo
from src.external_api import ExternalAPI


class CollaborationTestRunner:
    """Runs and evaluates team collaboration test scenarios"""

    def __init__(self, output_dir: str = "/tmp/collaboration_test"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.start_time = datetime.now()
        self.test_data = {
            'messages': [],
            'files': [],
            'executions': [],
            'timeline': [],
            'scores': {}
        }

        # Agent configuration for Calculator Web App test
        self.agents = {
            'FRBG/padre': {
                'id': 10,
                'loop': 72,
                'role': 'Project Manager'
            },
            'FRBG/TeacherJohn': {
                'id': 8,
                'loop': 70,
                'role': 'Backend Developer'
            },
            'FRBG/zhou': {
                'id': 12,
                'loop': 74,
                'role': 'Frontend Developer'
            }
        }

        # API configuration for execution monitoring
        self.base_url = "http://loopai.local:5050/api/public"
        self.execution_timeout = 5  # seconds

        # Collaboration patterns for NLP analysis
        self.collaboration_patterns = [
            r"let[\'']s\s+coordinate",
            r"work\s+together",
            r"team\s+effort",
            r"collaborate\s+with",
            r"input\s+from",
            r"what\s+do\s+you\s+think",
            r"your\s+thoughts",
        ]

        self.decision_patterns = [
            r"I\s+suggest|propose|recommend",
            r"option\s+(A|B|1|2)",
            r"best\s+approach",
            r"decided\s+to|decision\s+made",
            r"after\s+considering",
            r"pros\s+and\s+cons",
        ]

        self.project_thinking_patterns = [
            r"phase\s+\d+",
            r"milestone",
            r"dependency|depends\s+on",
            r"deadline|timeline|schedule",
            r"deliverable",
            r"next\s+steps",
            r"action\s+items",
            r"task\s+breakdown",
            r"backend.*frontend",
            r"api.*endpoint",
        ]

    def check_execution(self, execution_id: str) -> Dict:
        """Check execution result and progress via REST API."""
        result_url = f"{self.base_url}/execution/{execution_id}/result/"
        progress_url = f"{self.base_url}/execution/{execution_id}/progress/"

        try:
            result_resp = requests.get(result_url, timeout=self.execution_timeout)
            progress_resp = requests.get(progress_url, timeout=self.execution_timeout)

            return {
                "execution_id": execution_id,
                "result": result_resp.json() if result_resp.status_code == 200 else None,
                "progress": progress_resp.json() if progress_resp.status_code == 200 else None,
                "timestamp": datetime.now()
            }
        except Exception as e:
            return {
                "execution_id": execution_id,
                "error": str(e),
                "timestamp": datetime.now()
            }

    def monitor_executions(self, execution_ids: List[str], check_interval: int = 10, max_checks: int = 60) -> Dict[str, Dict]:
        """Monitor multiple executions until completion."""
        if not execution_ids:
            print("⚠️  No execution IDs to monitor")
            return {}

        pending = set(execution_ids)
        completed = {}
        checks = 0

        print(f"\n{'='*80}")
        print(f"MONITORING {len(execution_ids)} EXECUTIONS")
        print(f"{'='*80}\n")

        while pending and checks < max_checks:
            checks += 1
            print(f"Check {checks}/{max_checks} - Pending: {len(pending)} executions")

            for exec_id in list(pending):
                result = self.check_execution(exec_id)

                if result.get("error"):
                    print(f"  ❌ {exec_id[:8]}... - Error: {result['error']}")
                    pending.remove(exec_id)
                    completed[exec_id] = result
                    continue

                progress = result.get("progress", {})
                status = progress.get("status", "unknown")

                if status == "completed":
                    completed[exec_id] = result
                    pending.remove(exec_id)
                    print(f"  ✅ {exec_id[:8]}... - COMPLETED")

                    # Show result summary
                    res_data = result.get("result", {})
                    if res_data.get("success"):
                        broadcast = res_data.get("data", {}).get("broadcast_data", [])
                        print(f"     Steps executed: {len(broadcast)}")
                elif status == "running":
                    print(f"  ⏳ {exec_id[:8]}... - RUNNING")
                elif status == "failed":
                    completed[exec_id] = result
                    pending.remove(exec_id)
                    print(f"  ❌ {exec_id[:8]}... - FAILED")
                    error = progress.get("error", "Unknown error")
                    print(f"     Error: {error}")
                else:
                    print(f"  ⚪ {exec_id[:8]}... - {status}")

            if pending:
                time.sleep(check_interval)

        print(f"\n{'='*80}")
        print(f"Monitoring complete: {len(completed)} finished, {len(pending)} pending")
        print(f"{'='*80}\n")

        return completed

    def extract_execution_ids_from_log(self, log_file: str) -> List[str]:
        """Extract execution IDs from a log file."""
        execution_ids = []

        if not os.path.exists(log_file):
            return execution_ids

        try:
            with open(log_file, 'r') as f:
                content = f.read()
                # Look for execution ID patterns (UUID format)
                pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
                matches = re.findall(pattern, content, re.IGNORECASE)
                execution_ids = list(set(matches))  # Remove duplicates

        except Exception as e:
            print(f"⚠️  Error reading log file {log_file}: {e}")

        return execution_ids

    def create_kickoff_message(self) -> str:
        """Creates the initial project kick-off message for calculator web app"""

        message = {
            "from": "FRBG/padre",
            "to": "FRBG/TeacherJohn, FRBG/zhou",
            "subject": "New Project: Simple Calculator Web Application",
            "body": """Hello team,

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
Project Manager""",
            "timestamp": datetime.now().isoformat() + "Z",
            "priority": "high",
            "project_type": "software_development_collaboration",
            "tags": ["test", "collaboration", "calculator", "3-day-project"],
            "expected_deliverables": ["backend_api", "frontend_ui", "integration", "documentation"]
        }

        return message

    def send_kickoff_message(self) -> bool:
        """Sends kick-off message to padre's outbox"""

        message = self.create_kickoff_message()

        # Write to padre's outbox
        padre_loop = self.agents['FRBG/padre']['loop']
        outbox_path = f"/Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops/{padre_loop}/filesystem/agentlife/post/outbox/new"

        os.makedirs(outbox_path, exist_ok=True)

        message_file = os.path.join(outbox_path, "calculator_project_kickoff.json")

        try:
            with open(message_file, 'w') as f:
                json.dump(message, f, indent=2)

            print(f"✅ Kick-off message created: {message_file}")
            self.test_data['timeline'].append({
                'timestamp': datetime.now(),
                'event': 'kickoff_sent',
                'details': 'Project kick-off message sent to TeacherJohn and zhou'
            })
            return True
        except Exception as e:
            print(f"❌ Failed to create kick-off message: {e}")
            return False

    def collect_messages(self) -> List[Dict]:
        """Collects all messages related to this test"""

        messages = message_repo.find_all()

        # Filter for project-related messages
        project_messages = []
        cutoff_time = self.start_time - timedelta(minutes=5)  # Include messages from just before test start

        for msg in messages:
            if msg.created_at and msg.created_at >= cutoff_time:
                # Check if message is calculator project-related
                if any(keyword in msg.data.lower() for keyword in
                       ['calculator', 'project', 'backend', 'frontend', 'api', 'endpoint',
                        'add', 'subtract', 'multiply', 'divide']):
                    project_messages.append({
                        'id': msg.id,
                        'from': msg.from_address,
                        'to': msg.to_address,
                        'data': msg.data,
                        'created_at': msg.created_at
                    })

        return project_messages

    def scan_agent_files(self) -> Dict[str, List[str]]:
        """Scans agent directories for created files"""

        files_by_agent = {}
        base_path = "/Users/dantweb/dantweb/l-sdk-27a/loopai_src/var/users/1/loops"

        for agent_name, agent_info in self.agents.items():
            loop_id = agent_info['loop']
            agent_paths = [
                f"{base_path}/{loop_id}/filesystem/agentlife/work",
                f"{base_path}/{loop_id}/filesystem/agentlife/post/outbox",
                f"{base_path}/{loop_id}/filesystem/agentlife/reflections"
            ]

            files = []
            for agent_path in agent_paths:
                if os.path.exists(agent_path):
                    for root, _, filenames in os.walk(agent_path):
                        for filename in filenames:
                            # Look for code files, docs, and messages
                            if any(filename.endswith(ext) for ext in
                                   ['.txt', '.json', '.md', '.py', '.js', '.html', '.css']):
                                full_path = os.path.join(root, filename)
                                # Check if file modified after test start
                                if os.path.getmtime(full_path) >= self.start_time.timestamp():
                                    files.append(full_path)

            files_by_agent[agent_name] = files

        return files_by_agent

    def analyze_collaboration(self, messages: List[Dict]) -> int:
        """Analyzes collaboration quality and returns score (0-40)"""

        score = 0

        # Communication Quality (15 pts)
        respondents = set()
        has_questions = False
        has_updates = False

        for msg in messages:
            respondents.add(msg['from'])

            # Check for clarifying questions
            if any(q in msg['data'].lower() for q in ['?', 'clarify', 'unclear', 'question', 'what do you mean']):
                has_questions = True

            # Check for status updates
            if any(u in msg['data'].lower() for u in ['update', 'progress', 'status', 'completed', 'working on']):
                has_updates = True

        # All agents responded
        if len(respondents) >= 4:  # At least 4 out of 5 agents
            score += 5

        if has_questions:
            score += 5

        if has_updates:
            score += 5

        # Coordination Effectiveness (15 pts)
        role_mentions = 0
        dependency_mentions = 0
        handoff_mentions = 0

        for msg in messages:
            # Check for role understanding
            if any(r in msg['data'].lower() for r in ['coordinator', 'lead', 'reviewer', 'reporter', 'my role']):
                role_mentions += 1

            # Check for dependency identification
            for pattern in [r'depend', r'after.*complete', r'before.*can', r'waiting for']:
                if re.search(pattern, msg['data'].lower()):
                    dependency_mentions += 1
                    break

            # Check for handoffs
            if any(h in msg['data'].lower() for h in ['sending you', 'attached', 'ready for', 'please review']):
                handoff_mentions += 1

        if role_mentions >= 2:
            score += 5
        if dependency_mentions >= 1:
            score += 5
        if handoff_mentions >= 2:
            score += 5

        # Responsiveness (10 pts)
        if len(messages) > 0:
            response_times = []
            sorted_msgs = sorted(messages, key=lambda m: m['created_at'])

            for i in range(1, len(sorted_msgs)):
                if sorted_msgs[i]['from'] != sorted_msgs[i-1]['from']:
                    time_diff = (sorted_msgs[i]['created_at'] - sorted_msgs[i-1]['created_at']).total_seconds() / 3600
                    response_times.append(time_diff)

            if response_times:
                avg_response = sum(response_times) / len(response_times)
                if avg_response < 24:  # Less than 24 hours
                    score += 5

            # Task completion (simplified - check if files exist)
            if len(self.test_data['files']) >= 3:  # At least 3 deliverables created
                score += 5

        return score

    def analyze_decisions(self, messages: List[Dict], files: Dict) -> int:
        """Analyzes decision-making quality and returns score (0-30)"""

        score = 0

        # Planning Decisions (10 pts)
        format_decided = False
        rationale_provided = False

        for msg in messages:
            # Check for format decisions
            if any(f in msg['data'].lower() for f in ['format', 'structure', 'sections', 'layout', 'organize']):
                format_decided = True

            # Check for rationale
            if any(r in msg['data'].lower() for r in ['because', 'reason', 'rationale', 'why', 'this way']):
                rationale_provided = True

        if format_decided:
            score += 5
        if rationale_provided:
            score += 5

        # Content Decisions (10 pts)
        topics_chosen = False
        length_appropriate = False

        for msg in messages:
            if any(t in msg['data'].lower() for t in ['topic', 'focus on', 'write about', 'cover']):
                topics_chosen = True

        # Check file lengths (if files exist)
        for agent_files in files.values():
            for file_path in agent_files:
                if 'article' in file_path or 'insights' in file_path or 'content' in file_path:
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            word_count = len(content.split())
                            if 100 <= word_count <= 300:  # Reasonable length
                                length_appropriate = True
                                break
                    except:
                        pass

        if topics_chosen:
            score += 5
        if length_appropriate:
            score += 5

        # Conflict Resolution (10 pts) - bonus if evidence found
        conflict_handled = False
        consensus_reached = False

        for msg in messages:
            if any(c in msg['data'].lower() for c in ['disagree', 'concern', 'issue', 'problem', 'conflict']):
                # Look for resolution
                if any(r in msg['data'].lower() for r in ['resolve', 'solution', 'compromise', 'agree', 'consensus']):
                    conflict_handled = True
                    consensus_reached = True

        if conflict_handled:
            score += 5
        if consensus_reached:
            score += 5

        return score

    def analyze_project_thinking(self, messages: List[Dict], files: Dict) -> int:
        """Analyzes project thinking quality and returns score (0-30)"""

        score = 0

        # Planning & Breakdown (10 pts)
        phases_defined = False
        dependencies_identified = False

        for msg in messages:
            # Check for phase planning
            if any(p in msg['data'].lower() for p in ['phase', 'step 1', 'step 2', 'first', 'then', 'finally']):
                phases_defined = True

            # Check for dependencies
            for pattern in self.project_thinking_patterns[2:3]:  # dependency patterns
                if re.search(pattern, msg['data'].lower()):
                    dependencies_identified = True
                    break

        # Check for project plan file
        for agent_files in files.values():
            for file_path in agent_files:
                if 'plan' in file_path.lower():
                    phases_defined = True
                    break

        if phases_defined:
            score += 5
        if dependencies_identified:
            score += 5

        # Execution Management (10 pts)
        timeline_tracked = False
        progress_monitored = False

        for msg in messages:
            if any(t in msg['data'].lower() for t in ['deadline', 'timeline', 'schedule', 'by day']):
                timeline_tracked = True

            if any(p in msg['data'].lower() for p in ['progress', 'status', 'completed', 'working on', 'next']):
                progress_monitored = True

        if timeline_tracked:
            score += 5
        if progress_monitored:
            score += 5

        # Reflection & Learning (10 pts)
        retrospective_exists = False
        improvements_identified = False

        # Check for reflection files
        for agent_files in files.values():
            for file_path in agent_files:
                if 'retrospective' in file_path.lower() or 'reflection' in file_path.lower() or 'lessons' in file_path.lower():
                    retrospective_exists = True
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            if any(i in content for i in ['improve', 'better', 'next time', 'learn']):
                                improvements_identified = True
                    except:
                        pass

        if retrospective_exists:
            score += 5
        if improvements_identified:
            score += 5

        return score

    def calculate_deliverable_bonus(self, files: Dict) -> int:
        """Calculates bonus points for deliverables (0-20)"""

        bonus = 0

        required_files = {
            'backend_api': False,   # Backend API code
            'frontend_ui': False,   # Frontend UI code
            'integration': False,   # Combined project
            'documentation': False  # Documentation/README
        }

        for agent_files in files.values():
            for file_path in agent_files:
                filename = file_path.lower()

                if any(kw in filename for kw in ['backend', 'api', 'server']) and any(ext in filename for ext in ['.py', '.js']):
                    required_files['backend_api'] = True
                elif any(kw in filename for kw in ['frontend', 'ui', 'calculator']) and any(ext in filename for ext in ['.html', '.js', '.css']):
                    required_files['frontend_ui'] = True
                elif 'integration' in filename or 'combined' in filename or 'calculator_project' in filename:
                    required_files['integration'] = True
                elif any(kw in filename for kw in ['readme', 'doc', 'instruction', 'usage']) and filename.endswith('.md'):
                    required_files['documentation'] = True

        # Award 5 points for each deliverable
        for delivered in required_files.values():
            if delivered:
                bonus += 5

        return bonus

    def generate_report(self, messages: List[Dict], files: Dict, scores: Dict) -> str:
        """Generates comprehensive test report"""

        total_score = sum(scores.values())
        max_score = 120
        percentage = (total_score / max_score) * 100
        result = "PASS" if total_score >= 70 else "FAIL"

        duration = datetime.now() - self.start_time

        report = f"""# Team Collaboration Test Report

**Test Run:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {duration.total_seconds() / 3600:.1f} hours
**Scenario:** Calculator Web App Project

---

## Executive Summary

**Total Score:** {total_score}/120 points ({percentage:.1f}%)
**Result:** **{result}**

### Score Breakdown
- Team Collaboration: {scores['collaboration']}/40 ({scores['collaboration']/40*100:.0f}%)
- Decision Making: {scores['decision']}/30 ({scores['decision']/30*100:.0f}%)
- Project Thinking: {scores['project']}/30 ({scores['project']/30*100:.0f}%)
- Deliverable Bonus: {scores['bonus']}/20 ({scores['bonus']/20*100:.0f}%)

### Performance Level
"""

        if total_score >= 90:
            report += "🏆 **EXCELLENT** - Outstanding team collaboration and execution\n"
        elif total_score >= 70:
            report += "✅ **GOOD** - Solid teamwork with room for improvement\n"
        elif total_score >= 50:
            report += "⚠️  **NEEDS IMPROVEMENT** - Basic collaboration but significant gaps\n"
        else:
            report += "❌ **POOR** - Major collaboration and execution issues\n"

        report += "\n---\n\n## Detailed Findings\n\n"

        # Communication Analysis
        report += "### Communication Analysis\n\n"
        report += f"- **Messages exchanged:** {len(messages)}\n"

        if messages:
            agents_involved = set(msg['from'] for msg in messages)
            report += f"- **Agents participating:** {len(agents_involved)}/3 ({', '.join(sorted(agents_involved))})\n"

            response_times = []
            sorted_msgs = sorted(messages, key=lambda m: m['created_at'])
            for i in range(1, len(sorted_msgs)):
                if sorted_msgs[i]['from'] != sorted_msgs[i-1]['from']:
                    time_diff = (sorted_msgs[i]['created_at'] - sorted_msgs[i-1]['created_at']).total_seconds() / 3600
                    response_times.append(time_diff)

            if response_times:
                avg_response = sum(response_times) / len(response_times)
                report += f"- **Average response time:** {avg_response:.1f} hours\n"
        else:
            report += "- **Agents participating:** 0/3\n"
            report += "- **Average response time:** N/A\n"

        # Decision Making
        report += "\n### Decision Making\n\n"

        decision_count = 0
        for msg in messages:
            if any(re.search(pattern, msg['data'].lower()) for pattern in self.decision_patterns):
                decision_count += 1

        report += f"- **Decision points identified:** {decision_count}\n"
        report += f"- **Format decisions made:** {'✓' if scores['decision'] >= 5 else '✗'}\n"
        report += f"- **Rationale provided:** {'✓' if scores['decision'] >= 10 else '✗'}\n"

        # Project Execution
        report += "\n### Project Execution\n\n"

        total_files = sum(len(f) for f in files.values())
        report += f"- **Files created:** {total_files}\n"
        report += f"- **Project planning evident:** {'✓' if scores['project'] >= 5 else '✗'}\n"
        report += f"- **Timeline management:** {'✓' if scores['project'] >= 15 else '✗'}\n"
        report += f"- **Retrospective conducted:** {'✓' if scores['project'] >= 25 else '✗'}\n"

        # Deliverables
        report += "\n### Deliverables Status\n\n"

        deliverables = {
            'Backend API Code': '✓' if scores['bonus'] >= 5 else '✗',
            'Frontend UI Code': '✓' if scores['bonus'] >= 10 else '✗',
            'Integration/Combined Project': '✓' if scores['bonus'] >= 15 else '✗',
            'Documentation/README': '✓' if scores['bonus'] >= 20 else '✗'
        }

        for deliverable, status in deliverables.items():
            report += f"- {deliverable}: {status}\n"

        # File Artifacts
        report += "\n### File Artifacts Created\n\n"

        if total_files > 0:
            for agent, agent_files in files.items():
                if agent_files:
                    report += f"**{agent}:**\n"
                    for file_path in agent_files:
                        report += f"- `{os.path.basename(file_path)}`\n"
                    report += "\n"
        else:
            report += "*No files created during test period*\n\n"

        # Message Timeline
        report += "### Message Timeline\n\n"

        if messages:
            report += "```\n"
            for msg in sorted(messages, key=lambda m: m['created_at']):
                timestamp = msg['created_at'].strftime('%H:%M:%S')
                from_agent = msg['from'].split('/')[-1]
                to_agent = msg['to'].split('/')[-1]
                preview = msg['data'][:60].replace('\n', ' ')
                report += f"[{timestamp}] {from_agent} → {to_agent}: {preview}...\n"
            report += "```\n\n"
        else:
            report += "*No messages exchanged during test period*\n\n"

        # Recommendations
        report += "## Recommendations\n\n"

        if scores['collaboration'] < 20:
            report += "- **Improve Communication:** Encourage more frequent status updates and clarifying questions\n"

        if scores['decision'] < 15:
            report += "- **Strengthen Decision Making:** Document decisions with clear rationale\n"

        if scores['project'] < 15:
            report += "- **Enhance Project Thinking:** Create explicit project plans with phases and dependencies\n"

        if scores['bonus'] < 10:
            report += "- **Focus on Deliverables:** Ensure core project outputs are completed on time\n"

        if total_score >= 90:
            report += "- **Maintain Excellence:** Continue current collaboration practices and share as best practices\n"

        # Conclusion
        report += "\n## Conclusion\n\n"

        if result == "PASS":
            report += f"The team demonstrated **{result.lower()}ing** collaboration skills with a score of {total_score}/{max_score} ({percentage:.1f}%). "

            if total_score >= 90:
                report += "The team showed excellent coordination, clear decision-making, and strong project management. "
                report += "This level of performance indicates the agents can successfully execute complex multi-agent projects.\n"
            else:
                report += "While the team met the passing threshold, there are opportunities for improvement in "
                weak_areas = []
                if scores['collaboration'] < 30:
                    weak_areas.append("communication")
                if scores['decision'] < 20:
                    weak_areas.append("decision-making")
                if scores['project'] < 20:
                    weak_areas.append("project planning")
                report += ", ".join(weak_areas) + ".\n"
        else:
            report += f"The team **failed** to demonstrate adequate collaboration with a score of {total_score}/{max_score} ({percentage:.1f}%). "
            report += "Significant improvements are needed before agents can reliably work together on complex projects.\n"

        report += "\n---\n\n"
        report += f"*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        report += f"*Test scenario: Calculator Web App Project (3-day cycle)*\n"

        return report

    def run_test(self, days: int = 3, log_file: Optional[str] = None, monitor_interval: int = 10, send_kickoff: bool = False) -> Dict:
        """
        Runs complete collaboration test with async execution monitoring

        Args:
            days: Number of days to run test
            log_file: Path to log file with execution IDs (e.g., /tmp/calculator_3day_test.log)
            monitor_interval: Seconds between execution checks
            send_kickoff: Whether to send kick-off message (default: False, assumes message already sent)

        Returns:
            Test results dictionary
        """

        print("=" * 80)
        print("CALCULATOR WEB APP COLLABORATION TEST")
        print("=" * 80)
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {days} days")
        print(f"Execution check interval: {monitor_interval} seconds")
        print()

        # Step 1: Optionally send kick-off message
        if send_kickoff:
            print("Step 1: Sending project kick-off message...")
            if not self.send_kickoff_message():
                print("❌ Failed to send kick-off message. Aborting test.")
                return {}

            print("✅ Kick-off message sent successfully")
            print(f"   Message location: Loop {self.agents['FRBG/padre']['loop']} outbox/new")
            print()
        else:
            print("Step 1: Kick-off message already sent - skipping")
            print()

        # Step 2: Monitor execution IDs from log file
        if log_file:
            print(f"Step 2: Monitoring executions from log file: {log_file}")
            print("   Waiting for log file to populate with execution IDs...")
            print()

            # Wait a bit for initial executions to start
            time.sleep(5)

            # Extract execution IDs from log
            execution_ids = self.extract_execution_ids_from_log(log_file)

            if execution_ids:
                print(f"   Found {len(execution_ids)} execution IDs")
                for exec_id in execution_ids[:5]:  # Show first 5
                    print(f"   - {exec_id[:8]}...")
                if len(execution_ids) > 5:
                    print(f"   ... and {len(execution_ids) - 5} more")
                print()

                # Monitor executions
                completed_executions = self.monitor_executions(
                    execution_ids,
                    check_interval=monitor_interval,
                    max_checks=120  # Up to 20 minutes of monitoring
                )

                self.test_data['executions'] = completed_executions
                print(f"✅ Monitored {len(completed_executions)} executions")
                print()
            else:
                print("⚠️  No execution IDs found in log file yet")
                print("   Test will proceed with file/message analysis only")
                print()
        else:
            print("Step 2: No log file specified - skipping execution monitoring")
            print()

        # Step 3: Collect data
        print("Step 3: Collecting test data...")
        messages = self.collect_messages()
        files = self.scan_agent_files()

        self.test_data['messages'] = messages
        self.test_data['files'] = files

        print(f"   Messages collected: {len(messages)}")
        print(f"   Files found: {sum(len(f) for f in files.values())}")
        print()

        # Step 4: Evaluate results
        print("Step 4: Evaluating collaboration quality...")

        scores = {
            'collaboration': self.analyze_collaboration(messages),
            'decision': self.analyze_decisions(messages, files),
            'project': self.analyze_project_thinking(messages, files),
            'bonus': self.calculate_deliverable_bonus(files)
        }

        self.test_data['scores'] = scores

        print(f"   Collaboration score: {scores['collaboration']}/40")
        print(f"   Decision making score: {scores['decision']}/30")
        print(f"   Project thinking score: {scores['project']}/30")
        print(f"   Deliverable bonus: {scores['bonus']}/20")
        print()

        total_score = sum(scores.values())
        result = "PASS" if total_score >= 70 else "FAIL"
        print(f"   TOTAL SCORE: {total_score}/120 ({total_score/120*100:.1f}%) - {result}")
        print()

        # Step 5: Generate report
        print("Step 5: Generating test report...")
        report = self.generate_report(messages, files, scores)

        # Save report
        report_path = self.output_dir / f"calculator_test_report_{self.start_time.strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_path, 'w') as f:
            f.write(report)

        print(f"✅ Report saved: {report_path}")
        print()

        print("=" * 80)
        print(f"TEST {result}")
        print("=" * 80)

        return self.test_data


def main():
    """Main entry point"""

    import argparse

    parser = argparse.ArgumentParser(
        description='Run automated team collaboration test for Calculator Web App',
        epilog="""
Examples:
  # Monitor existing 3-day cycle from log file
  python run_collaboration_test.py --log-file /tmp/calculator_3day_test.log --days 3

  # Send kick-off and start new test
  python run_collaboration_test.py --send-kickoff --days 3

  # Just send kick-off message and exit
  python run_collaboration_test.py --send-only
        """
    )
    parser.add_argument('--days', type=int, default=3, help='Number of days to run test (default: 3)')
    parser.add_argument('--output', type=str, default='/tmp/collaboration_test', help='Output directory')
    parser.add_argument('--interval', type=int, default=10, help='Execution check interval in seconds (default: 10)')
    parser.add_argument('--log-file', type=str, help='Path to log file with execution IDs (e.g., /tmp/calculator_3day_test.log)')
    parser.add_argument('--send-kickoff', action='store_true', help='Send kick-off message before starting test')
    parser.add_argument('--send-only', action='store_true', help='Only send kick-off message and exit')

    args = parser.parse_args()

    # Create test runner
    runner = CollaborationTestRunner(output_dir=args.output)

    if args.send_only:
        print("Sending kick-off message only...")
        runner.send_kickoff_message()
        print("✅ Done. Message exchange will process it on next cycle.")
        return

    # Run full test
    results = runner.run_test(
        days=args.days,
        log_file=args.log_file,
        monitor_interval=args.interval,
        send_kickoff=args.send_kickoff
    )

    if results:
        total_score = sum(results['scores'].values())
        if total_score >= 70:
            print("\n🎉 TEST PASSED!")
            sys.exit(0)
        else:
            print("\n❌ TEST FAILED")
            sys.exit(1)
    else:
        print("\n❌ TEST ERROR")
        sys.exit(2)


if __name__ == '__main__':
    main()
