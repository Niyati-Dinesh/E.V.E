import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'master_controller'))

from backend.core.database import get_available_agents

print("\n" + "="*60)
print("TESTING get_available_agents()")
print("="*60)

test_types = ['coding', 'documentation', 'analysis', 'general', None]

for task_type in test_types:
    agents = get_available_agents(task_type=task_type)
    print(f"\ntask_type='{task_type}': Found {len(agents)} agents")
    for a in agents:
        print(f"   - {a['agent_name']} ({a['capability']})")

print("\n" + "="*60)
