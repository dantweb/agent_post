#!/usr/bin/env python3
"""
LoopAI Agent Orchestration - Living Agent Workflow

This script orchestrates daily cycles for all agents using the Living Agent philosophy:
- Agents are autonomous professionals, not mechanical task executors
- Each agent makes context-aware decisions about what to work on
- Agents consider priorities, dependencies, team needs, and their own capacity
- Collaboration and team success are prioritized

Daily Cycle (3 Actions):
  1. READ_POSTS: Process incoming messages → create tasks
  2. GET_WORK: Context-aware task selection + execution (Living Agent intelligence)
  3. VALIDATE_WORK: Validate completed work quality

Weekly Reflection (Every 5 days):
  - REFLEX: Self-reflection, performance analysis, continuous improvement
"""
import json
import os
import sys
import subprocess
from flask.cli import load_dotenv
from datetime import datetime

from src.city_api import CityAPI
from src.external_api import ExternalAPI
from src.message_service import MessageService
import dotenv

load_dotenv()

# Define the daily action cycle (one "virtual day" = one complete cycle)
# Complex workflow: READ → SELECT → PREPARE → EXECUTE → VALIDATE (per action) → VALIDATE (overall)
# This allows iterative execution of multiple actions within a single work task

# Morning: Process messages and plan work
morning_actions = ["READ_POSTS", "GET_WORK"]

# Work cycle: Execute actions iteratively (can be repeated for multiple actions)
work_cycle_actions = ["PREPARE_ACTION", "DO_ACTION", "VALIDATE_ACTION"]
work_cycle_iterations = 3  # Number of action iterations per day

# Evening: Final validation
evening_actions = ["VALIDATE_WORK"]

# Combine all daily actions
daily_actions = morning_actions + (work_cycle_actions * work_cycle_iterations) + evening_actions

# Reflection runs after every 5 virtual days for continuous learning
reflex_action = "REFLEX"
days_per_reflex = 5

# Define the base directory of the project, assuming the script is in agent_post/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))

# Add the 'src' directory to the Python path to allow importing project modules [2]
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.insert(0, SRC_DIR)


AGENT_POST_CONFIG_JSON = "agent_post_config.json"

def load_config(config_path: str) -> dict:
    """Load and return configuration from a JSON file."""
    try:
        with open(config_path, "r") as config_file:
            config = json.load(config_file)
        return config
    except Exception as e:
        print(f"Error loading configuration from {config_path}: {e}")
        return {}


def run_action_for_agent(citizen_name, recipient_url, action):
    """Run a single action for a single agent."""
    modified_url = recipient_url.replace("WAKEUP", action)
    print(f"  [{datetime.now().strftime('%H:%M:%S')}] {citizen_name} → {action}")

    try:
        result = subprocess.run(
            ["curl", "-s", modified_url],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        response = json.loads(result.stdout)
        if response.get("success"):
            print(f"    ✓ Started (execution_id: {response.get('execution_id', 'N/A')[:8]}...)")
            return True
        else:
            print(f"    ✗ Failed: {response.get('message', 'Unknown error')}")
            return False
    except subprocess.TimeoutExpired:
        print(f"    ✗ Timeout after 30s")
        return False
    except subprocess.CalledProcessError as e:
        print(f"    ✗ Error: {e}")
        return False
    except json.JSONDecodeError:
        print(f"    ✗ Invalid JSON response")
        return False
    except Exception as e:
        print(f"    ✗ Unexpected error: {e}")
        return False


def run(num_days=1):
    """
    Run agent cycles for a specified number of virtual days.
    Each day runs: READ_POSTS → GET_WORK → VALIDATE_WORK
    After every 5 days, run: REFLEX

    Args:
        num_days (int): Number of virtual days to simulate (default: 1)
    """
    from time import sleep

    # Extract the cities_url from the config and assign it as api_url (fallback provided)
    api_url = os.getenv("CITY_API_URL", "http://loopai_web:5000/api/agents/cities-data/")
    print(f"\n{'='*80}")
    print(f"LoopAI Agent Orchestration - Running {num_days} virtual day(s)")
    print(f"Using API URL: {api_url}")
    print(f"{'='*80}\n")

    city_api = CityAPI(api_url)

    try:
        cities_data = city_api.get_cities()
    except Exception as e:
        print(f"❌ Error fetching cities: {e}")
        return

    # Extract addresses
    addresses = {}
    for address_dict in cities_data.get("addresses", []):
        addresses.update(address_dict)

    if not addresses:
        print("❌ No agent addresses found")
        return

    print(f"Found {len(addresses)} agent(s): {', '.join(addresses.keys())}\n")

    # Run cycles for specified number of days
    for day in range(1, num_days + 1):
        print(f"\n{'─'*80}")
        print(f"🌅 VIRTUAL DAY {day}/{num_days}")
        print(f"{'─'*80}\n")

        # Run daily actions for each agent
        for action in daily_actions:
            print(f"\n📋 Running action: {action}")
            print(f"{'─'*40}")

            success_count = 0
            for citizen_name, recipient_url in addresses.items():
                if run_action_for_agent(citizen_name, recipient_url, action):
                    success_count += 1

            print(f"\n  Summary: {success_count}/{len(addresses)} agents started successfully")

            # Wait between actions
            if action != daily_actions[-1]:  # Don't wait after last action
                print(f"  ⏳ Waiting 15 seconds before next action...")
                sleep(15)

        # Check if we should run reflection
        if day % days_per_reflex == 0:
            print(f"\n{'─'*80}")
            print(f"🤔 REFLECTION TIME (after {day} days)")
            print(f"{'─'*80}\n")
            print(f"📋 Running action: {reflex_action}")
            print(f"{'─'*40}")

            success_count = 0
            for citizen_name, recipient_url in addresses.items():
                if run_action_for_agent(citizen_name, recipient_url, reflex_action):
                    success_count += 1

            print(f"\n  Summary: {success_count}/{len(addresses)} agents started reflection")

        # Run message exchange after each day's work
        print(f"\n{'─'*80}")
        print(f"📬 MESSAGE EXCHANGE (End of Day {day})")
        print(f"{'─'*80}\n")
        try:
            # Initialize message service components
            external_api_token = os.getenv('EXTERNAL_API_TOKEN', 'default_token')
            external_api = ExternalAPI(token=external_api_token)
            message_service = MessageService(city_api=city_api, external_api=external_api)

            print("  🔄 Processing inter-agent messages...")
            message_service.process_messages()
            print("  ✅ Message exchange completed")
        except Exception as e:
            print(f"  ⚠️ Message exchange failed: {e}")

        # Wait before next day (unless it's the last day)
        if day < num_days:
            print(f"\n⏳ Day {day} complete. Waiting 20 seconds before next day...")
            sleep(20)

    print(f"\n{'='*80}")
    print(f"✅ All {num_days} virtual day(s) completed!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run LoopAI agent action cycles for multiple virtual days"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of virtual days to run (default: 1, REFLEX runs every 5 days)"
    )

    args = parser.parse_args()
    run(num_days=args.days)
