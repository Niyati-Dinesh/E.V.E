"""
Master Failover System for E.V.E.
Implements leader election and automatic failover between multiple masters
"""

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional
from backend.core.database import (
    register_master,
    update_master_heartbeat,
    set_active_master,
    get_active_master,
    get_all_masters
)
from backend.core.config import (
    MASTER_ID,
    MASTER_HEARTBEAT_INTERVAL,
    MASTER_TIMEOUT,
    ENABLE_MASTER_FAILOVER
)

# =============================================================================
# MASTER STATE CLASS
# =============================================================================

class MasterState:
    """
    Tracks the state of THIS master instance
    
    Each master has:
    - master_id: Unique identifier (master-1, master-2, master-3)
    - is_active: Am I the one making decisions?
    - last_heartbeat: When did I last check in?
    """
    
    def __init__(self, master_id: str):
        self.master_id = master_id
        self.is_active = False
        self.last_heartbeat = None
        
        # Register myself in the database
        register_master(master_id)
        # Send immediate heartbeat to avoid initial timeout
        self.send_heartbeat()
        print(f"🎯 Master {master_id} initialized and registered")
    
    def become_active(self):
        """
        Promote this master to ACTIVE status
        Now THIS master will handle all requests
        """
        set_active_master(self.master_id)
        self.is_active = True
        print(f"\n{'='*60}")
        print(f"👑 {self.master_id} is now ACTIVE")
        print(f"   This master will process all requests")
        print(f"{'='*60}\n")
    
    def become_standby(self):
        """
        Demote this master to STANDBY status
        Another master is active, we just monitor
        """
        self.is_active = False
        print(f"⏸️  {self.master_id} is now STANDBY (monitoring only)")
    
    def send_heartbeat(self):
        """
        Send heartbeat to database - "I'm alive!"
        """
        try:
            update_master_heartbeat(self.master_id)
            self.last_heartbeat = datetime.now(timezone.utc)
        except Exception as e:
            print(f"❌ Failed to send heartbeat: {e}")

# =============================================================================
# LEADER ELECTION ALGORITHM
# =============================================================================

def elect_leader() -> str:
    """
    Decide which master should be active
    
    Election Rules:
    1. If current active master is still alive → Keep it active
    2. If active master is dead → Elect new leader
    3. New leader = Master with lowest ID among alive masters
       (master-1 has priority over master-2, etc.)
    
    Returns: master_id that should be active
    """
    
    all_masters = get_all_masters()
    
    if not all_masters:
        # No masters in database? Shouldn't happen, but elect self
        return MASTER_ID
    
    now = datetime.now(timezone.utc)
    
    # Check if there's already an active master
    for master in all_masters:
        if master['active']:
            # Found active master, check if it's still alive
            if master['last_heartbeat']:
                try:
                    # Parse the ISO format timestamp - may or may not have timezone
                    last_beat_str = master['last_heartbeat']
                    if 'T' in last_beat_str:
                        last_beat = datetime.fromisoformat(last_beat_str.replace('Z', '+00:00'))
                    else:
                        # Assume UTC if no timezone
                        last_beat = datetime.fromisoformat(last_beat_str).replace(tzinfo=timezone.utc)
                    
                    seconds_since_heartbeat = (now - last_beat).total_seconds()
                    
                    if seconds_since_heartbeat < MASTER_TIMEOUT:
                        # Active master is still alive! Keep it
                        return master['master_id']
                    else:
                        # Active master is DEAD (no heartbeat)
                        print(f"💀 Active master {master['master_id']} appears DEAD")
                        print(f"   No heartbeat for {seconds_since_heartbeat:.1f}s (timeout: {MASTER_TIMEOUT}s)")
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Error parsing heartbeat timestamp: {e}")
            # Continue to elect new leader
    
    # No active master OR active master is dead
    # Find all alive masters
    alive_masters = []
    
    for master in all_masters:
        if master['last_heartbeat']:
            try:
                # Parse the ISO format timestamp
                last_beat_str = master['last_heartbeat']
                if 'T' in last_beat_str:
                    last_beat = datetime.fromisoformat(last_beat_str.replace('Z', '+00:00'))
                else:
                    # Assume UTC if no timezone
                    last_beat = datetime.fromisoformat(last_beat_str).replace(tzinfo=timezone.utc)
                
                seconds_since = (now - last_beat).total_seconds()
                
                if seconds_since < MASTER_TIMEOUT:
                    alive_masters.append(master['master_id'])
                    print(f"✅ {master['master_id']} is alive (heartbeat {seconds_since:.1f}s ago)")
            except (ValueError, TypeError) as e:
                print(f"⚠️ Error parsing heartbeat for {master['master_id']}: {e}")
    
    if alive_masters:
        # Sort by ID and pick first (master-1 before master-2)
        alive_masters.sort()
        elected = alive_masters[0]
        print(f"🗳️  Elected {elected} as new leader from {len(alive_masters)} alive masters")
        return elected
    else:
        # No alive masters found in database, elect self
        print(f"⚠️  No alive masters found, electing self: {MASTER_ID}")
        return MASTER_ID
    
    if alive_masters:
        # Sort by ID and pick first (master-1 before master-2)
        alive_masters.sort()
        elected = alive_masters[0]
        print(f"🗳️  Elected {elected} as new leader from {len(alive_masters)} alive masters")
        return elected
    else:
        # No alive masters found in database, elect self
        print(f"⚠️  No alive masters found, electing self: {MASTER_ID}")
        return MASTER_ID

# =============================================================================
# FAILOVER MONITOR (Runs continuously in background)
# =============================================================================

async def failover_monitor(master_state: MasterState):
    """
    Background task that continuously monitors for failover
    
    This runs FOREVER in a loop:
    1. Send own heartbeat
    2. Check who should be leader
    3. Become active or standby as needed
    4. Wait, repeat
    """
    
    # If failover is disabled, just become active and return
    if not ENABLE_MASTER_FAILOVER:
        print("ℹ️  Master failover DISABLED - running in single master mode")
        master_state.become_active()
        
        # Still send heartbeats in background
        while True:
            try:
                master_state.send_heartbeat()
            except Exception as e:
                print(f"⚠️ Heartbeat error: {e}")
            await asyncio.sleep(MASTER_HEARTBEAT_INTERVAL)
        
        return
    
    print(f"🔍 Failover monitor started for {master_state.master_id}")
    print(f"   Heartbeat interval: {MASTER_HEARTBEAT_INTERVAL}s")
    print(f"   Master timeout: {MASTER_TIMEOUT}s")
    
    while True:
        try:
            # Send own heartbeat
            master_state.send_heartbeat()
            
            # Run leader election
            elected_leader = elect_leader()
            
            # Check if I should be active
            if elected_leader == master_state.master_id:
                if not master_state.is_active:
                    # I'm elected but not active yet
                    print(f"\n🚨 FAILOVER EVENT!")
                    print(f"   {master_state.master_id} taking over as active master")
                    master_state.become_active()
            else:
                if master_state.is_active:
                    # Someone else should be active
                    print(f"\n⚠️  {master_state.master_id} stepping down")
                    print(f"   {elected_leader} is now the leader")
                    master_state.become_standby()
            
            # Wait before next check
            await asyncio.sleep(MASTER_HEARTBEAT_INTERVAL)
            
        except asyncio.CancelledError:
            print(f"🛑 Failover monitor stopped for {master_state.master_id}")
            raise
        except Exception as e:
            print(f"❌ Failover monitor error: {e}")
            # Continue running even if there's an error
            await asyncio.sleep(MASTER_HEARTBEAT_INTERVAL)

# =============================================================================
# REQUEST PROCESSING CHECK
# =============================================================================

def should_process_request(master_state: MasterState) -> bool:
    """
    Check if THIS master should process incoming requests
    
    Rules:
    - If failover disabled → Always process
    - If failover enabled → Only if I'm active
    
    This gets called at the start of every API request
    """
    
    if not ENABLE_MASTER_FAILOVER:
        # Single master mode, always process
        return True
    
    # Multi-master mode, only active processes
    return master_state.is_active

# =============================================================================
# STATUS REPORTING
# =============================================================================

def get_master_status() -> dict:
    """
    Get current status of all masters in the cluster
    
    Useful for monitoring and debugging
    """
    
    all_masters = get_all_masters()
    active = get_active_master()
    
    return {
        "total_masters": len(all_masters),
        "active_master": active,
        "all_masters": all_masters,
        "failover_enabled": ENABLE_MASTER_FAILOVER,
        "current_master": MASTER_ID
    }

# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    """
    Test the failover system
    
    Run this with: python master_failover.py master-1
    Run in another terminal: python master_failover.py master-2
    """
    
    import sys
    
    # Get master ID from command line or use default
    if len(sys.argv) > 1:
        test_master_id = sys.argv[1]
    else:
        test_master_id = "master-1"
    
    print(f"Testing failover as {test_master_id}")
    print("Press Ctrl+C to stop\n")
    
    # Create master state
    state = MasterState(test_master_id)
    
    # Run failover monitor
    try:
        asyncio.run(failover_monitor(state))
    except KeyboardInterrupt:
        print(f"\n{test_master_id} stopped")