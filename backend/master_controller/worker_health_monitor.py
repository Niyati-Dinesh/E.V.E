"""
Worker Health Monitoring System
Tracks worker health, detects failures, and manages recovery
"""

import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import threading


class WorkerHealthMonitor:
    """
    Real-time worker health monitoring with automatic failure detection
    """
    
    def __init__(self):
        self.worker_health = {}  # {worker_id: {last_heartbeat, status, failures}}
        self.health_threshold = 30  # seconds without heartbeat = unhealthy (was 10, now 30)
        self.failure_threshold = 3  # consecutive failures before marking dead
        self.monitoring_active = False
        self.monitor_thread = None
        
        print("💓 Worker Health Monitor initialized")
    
    def update_heartbeat(self, worker_id: str, status: str = "idle"):
        """Record worker heartbeat"""
        now = time.time()
        
        if worker_id not in self.worker_health:
            self.worker_health[worker_id] = {
                "last_heartbeat": now,
                "status": status,
                "consecutive_failures": 0,
                "total_failures": 0,
                "health_status": "healthy",
                "first_seen": now
            }
        else:
            self.worker_health[worker_id]["last_heartbeat"] = now
            self.worker_health[worker_id]["status"] = status
            self.worker_health[worker_id]["consecutive_failures"] = 0  # Reset on success
            if self.worker_health[worker_id]["health_status"] == "dead":
                print(f"   🔄 Worker {worker_id} recovered from dead state")
            self.worker_health[worker_id]["health_status"] = "healthy"
    
    def record_failure(self, worker_id: str):
        """Record a worker failure"""
        if worker_id not in self.worker_health:
            return
        
        self.worker_health[worker_id]["consecutive_failures"] += 1
        self.worker_health[worker_id]["total_failures"] += 1
        
        failures = self.worker_health[worker_id]["consecutive_failures"]
        
        if failures >= self.failure_threshold:
            self.worker_health[worker_id]["health_status"] = "dead"
            print(f"   ⚠️ Worker {worker_id} marked as DEAD after {failures} failures")
        elif failures >= 2:
            self.worker_health[worker_id]["health_status"] = "degraded"
            print(f"   ⚠️ Worker {worker_id} marked as DEGRADED ({failures} failures)")
    
    def check_worker_health(self, worker_id: str) -> str:
        """Check individual worker health status"""
        if worker_id not in self.worker_health:
            return "unknown"
        
        worker = self.worker_health[worker_id]
        time_since_heartbeat = time.time() - worker["last_heartbeat"]
        
        # Check if heartbeat is stale
        if time_since_heartbeat > self.health_threshold:
            if worker["health_status"] != "dead":
                worker["health_status"] = "unhealthy"
                print(f"   ⚠️ Worker {worker_id} unhealthy (no heartbeat for {time_since_heartbeat:.1f}s)")
        
        return worker["health_status"]
    
    def get_healthy_workers(self, worker_type: Optional[str] = None) -> List[str]:
        """Get list of healthy workers, optionally filtered by type"""
        healthy = []
        
        for worker_id, health in self.worker_health.items():
            status = self.check_worker_health(worker_id)
            
            # Only include healthy or degraded workers (not dead/unhealthy)
            if status in ["healthy", "degraded"]:
                # Filter by type if specified
                if worker_type is None or worker_type in worker_id.lower():
                    healthy.append(worker_id)
        
        return healthy
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report"""
        total = len(self.worker_health)
        healthy = sum(1 for w in self.worker_health.values() 
                     if self.check_worker_health(list(self.worker_health.keys())[list(self.worker_health.values()).index(w)]) == "healthy")
        degraded = sum(1 for w in self.worker_health.values() 
                      if self.check_worker_health(list(self.worker_health.keys())[list(self.worker_health.values()).index(w)]) == "degraded")
        unhealthy = sum(1 for w in self.worker_health.values() 
                       if self.check_worker_health(list(self.worker_health.keys())[list(self.worker_health.values()).index(w)]) == "unhealthy")
        dead = sum(1 for w in self.worker_health.values() 
                  if self.check_worker_health(list(self.worker_health.keys())[list(self.worker_health.values()).index(w)]) == "dead")
        
        return {
            "total_workers": total,
            "healthy": healthy,
            "degraded": degraded,
            "unhealthy": unhealthy,
            "dead": dead,
            "workers": {
                worker_id: {
                    "status": self.check_worker_health(worker_id),
                    "last_heartbeat_ago": f"{time.time() - health['last_heartbeat']:.1f}s",
                    "consecutive_failures": health["consecutive_failures"],
                    "total_failures": health["total_failures"],
                    "uptime": f"{(time.time() - health['first_seen']) / 60:.1f} minutes"
                }
                for worker_id, health in self.worker_health.items()
            }
        }
    
    def start_monitoring(self):
        """Start background health monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("   ✅ Background health monitoring started")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring_active:
            time.sleep(5)  # Check every 5 seconds
            
            # Check all workers
            for worker_id in list(self.worker_health.keys()):
                self.check_worker_health(worker_id)
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.monitoring_active = False
        print("   🛑 Health monitoring stopped")
