"""
Performance Analytics System
Tracks detailed metrics for workers and master performance
"""

import time
from typing import Dict, List, Optional
from collections import defaultdict
import statistics


class PerformanceAnalytics:
    """
    Comprehensive performance tracking and analytics
    """
    
    def __init__(self):
        self.worker_metrics = defaultdict(lambda: {
            "total_tasks": 0,
            "successful_tasks": 0,
            "failed_tasks": 0,
            "total_duration": 0.0,
            "durations": [],
            "quality_scores": [],
            "first_seen": time.time()
        })
        
        self.master_metrics = {
            "total_requests": 0,
            "single_step_requests": 0,
            "multi_step_requests": 0,
            "ai_calls_made": 0,
            "cache_hits": 0,
            "avg_response_time": 0.0,
            "start_time": time.time()
        }
        
        print("📊 Performance Analytics initialized")
    
    def record_worker_task(self, worker_name: str, success: bool, duration: float, 
                          quality_score: Optional[float] = None):
        """Record worker task execution"""
        metrics = self.worker_metrics[worker_name]
        
        metrics["total_tasks"] += 1
        if success:
            metrics["successful_tasks"] += 1
        else:
            metrics["failed_tasks"] += 1
        
        metrics["total_duration"] += duration
        metrics["durations"].append(duration)
        
        # Keep only last 100 durations for stats
        if len(metrics["durations"]) > 100:
            metrics["durations"] = metrics["durations"][-100:]
        
        if quality_score is not None:
            metrics["quality_scores"].append(quality_score)
            if len(metrics["quality_scores"]) > 100:
                metrics["quality_scores"] = metrics["quality_scores"][-100:]
    
    def record_master_request(self, is_multi_step: bool, duration: float, 
                             ai_calls: int = 0, cache_hit: bool = False):
        """Record master controller request"""
        self.master_metrics["total_requests"] += 1
        
        if is_multi_step:
            self.master_metrics["multi_step_requests"] += 1
        else:
            self.master_metrics["single_step_requests"] += 1
        
        self.master_metrics["ai_calls_made"] += ai_calls
        
        if cache_hit:
            self.master_metrics["cache_hits"] += 1
        
        # Update average response time
        total = self.master_metrics["total_requests"]
        current_avg = self.master_metrics["avg_response_time"]
        self.master_metrics["avg_response_time"] = (
            (current_avg * (total - 1) + duration) / total
        )
    
    def get_worker_stats(self, worker_name: str) -> Dict:
        """Get detailed stats for a specific worker"""
        if worker_name not in self.worker_metrics:
            return {"error": "Worker not found"}
        
        metrics = self.worker_metrics[worker_name]
        
        success_rate = (metrics["successful_tasks"] / metrics["total_tasks"] * 100) if metrics["total_tasks"] > 0 else 0
        avg_duration = statistics.mean(metrics["durations"]) if metrics["durations"] else 0
        median_duration = statistics.median(metrics["durations"]) if metrics["durations"] else 0
        avg_quality = statistics.mean(metrics["quality_scores"]) if metrics["quality_scores"] else 0
        
        uptime_minutes = (time.time() - metrics["first_seen"]) / 60
        
        return {
            "worker_name": worker_name,
            "total_tasks": metrics["total_tasks"],
            "successful_tasks": metrics["successful_tasks"],
            "failed_tasks": metrics["failed_tasks"],
            "success_rate": f"{success_rate:.1f}%",
            "avg_duration": f"{avg_duration:.2f}s",
            "median_duration": f"{median_duration:.2f}s",
            "avg_quality_score": f"{avg_quality:.1f}/10" if avg_quality > 0 else "N/A",
            "uptime_minutes": f"{uptime_minutes:.1f}m",
            "tasks_per_minute": f"{metrics['total_tasks'] / uptime_minutes:.2f}" if uptime_minutes > 0 else "0"
        }
    
    def get_best_worker(self, worker_type: Optional[str] = None, 
                       metric: str = "success_rate") -> Optional[str]:
        """Get best performing worker by metric"""
        eligible_workers = {}
        
        for worker_name, metrics in self.worker_metrics.items():
            # Filter by type if specified
            if worker_type and worker_type.lower() not in worker_name.lower():
                continue
            
            # Only consider workers with at least 3 tasks
            if metrics["total_tasks"] < 3:
                continue
            
            if metric == "success_rate":
                score = metrics["successful_tasks"] / metrics["total_tasks"]
            elif metric == "speed":
                score = -statistics.mean(metrics["durations"]) if metrics["durations"] else 0  # Negative for sorting
            elif metric == "quality":
                score = statistics.mean(metrics["quality_scores"]) if metrics["quality_scores"] else 0
            else:
                continue
            
            eligible_workers[worker_name] = score
        
        if not eligible_workers:
            return None
        
        return max(eligible_workers, key=eligible_workers.get)
    
    def get_master_stats(self) -> Dict:
        """Get master controller statistics"""
        uptime_minutes = (time.time() - self.master_metrics["start_time"]) / 60
        requests_per_minute = self.master_metrics["total_requests"] / uptime_minutes if uptime_minutes > 0 else 0
        
        cache_hit_rate = (self.master_metrics["cache_hits"] / self.master_metrics["total_requests"] * 100) \
                        if self.master_metrics["total_requests"] > 0 else 0
        
        avg_ai_calls = self.master_metrics["ai_calls_made"] / self.master_metrics["total_requests"] \
                      if self.master_metrics["total_requests"] > 0 else 0
        
        return {
            "total_requests": self.master_metrics["total_requests"],
            "single_step": self.master_metrics["single_step_requests"],
            "multi_step": self.master_metrics["multi_step_requests"],
            "avg_response_time": f"{self.master_metrics['avg_response_time']:.2f}s",
            "requests_per_minute": f"{requests_per_minute:.2f}",
            "total_ai_calls": self.master_metrics["ai_calls_made"],
            "avg_ai_calls_per_request": f"{avg_ai_calls:.2f}",
            "cache_hits": self.master_metrics["cache_hits"],
            "cache_hit_rate": f"{cache_hit_rate:.1f}%",
            "uptime_minutes": f"{uptime_minutes:.1f}m"
        }
    
    def get_comprehensive_report(self) -> Dict:
        """Get full system performance report"""
        return {
            "master": self.get_master_stats(),
            "workers": {
                worker_name: self.get_worker_stats(worker_name)
                for worker_name in self.worker_metrics.keys()
            },
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Check for underperforming workers
        for worker_name, metrics in self.worker_metrics.items():
            if metrics["total_tasks"] >= 5:
                success_rate = metrics["successful_tasks"] / metrics["total_tasks"]
                if success_rate < 0.7:
                    recommendations.append(
                        f"⚠️ Worker {worker_name} has low success rate ({success_rate*100:.0f}%) - consider investigation"
                    )
        
        # Check AI call efficiency
        avg_ai_calls = self.master_metrics["ai_calls_made"] / self.master_metrics["total_requests"] \
                      if self.master_metrics["total_requests"] > 0 else 0
        if avg_ai_calls > 3.5:
            recommendations.append(
                f"💡 High AI call rate ({avg_ai_calls:.1f}/request) - consider batching or caching"
            )
        
        # Check response time
        if self.master_metrics["avg_response_time"] > 10:
            recommendations.append(
                f"⚠️ High average response time ({self.master_metrics['avg_response_time']:.1f}s) - optimize workers"
            )
        
        # Check cache effectiveness
        cache_hit_rate = (self.master_metrics["cache_hits"] / self.master_metrics["total_requests"] * 100) \
                        if self.master_metrics["total_requests"] > 0 else 0
        if cache_hit_rate < 10 and self.master_metrics["total_requests"] > 20:
            recommendations.append(
                f"💡 Low cache hit rate ({cache_hit_rate:.0f}%) - queries may be too unique"
            )
        
        if not recommendations:
            recommendations.append("✅ System performing optimally!")
        
        return recommendations
