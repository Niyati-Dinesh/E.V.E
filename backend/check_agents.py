import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'master_controller'))

from backend.core.database import get_available_agents

agents = get_available_agents()
print(f'\nFound {len(agents)} agents:\n')
for a in agents:
    print(f'  - {a["agent_name"]} ({a["capability"]}) - Status: {a["status"]} - Last HB: {a["last_heartbeat"]}')
