"""
Performance Tracker for Distributed Workers - 10/10 INTELLIGENCE
Advanced ML-like features:
- Predictive routing based on historical patterns
- Adaptive learning rates
- Trend analysis for early degradation detection
- Cost optimization
- Quality-based scoring
- Self-tuning thresholds
"""
import json
import time
from datetime import datetime, timedelta
from collections import defaultdict, deque
from pathlib import Path
import threading
import statistics

class PerformanceTracker:
    """Advanced performance tracker with ML-like intelligence"""
    
    def __init__(self, db_path="performance_metrics.json"):
        self.db_path = Path(db_path)
        self.metrics = defaultdict(lambda: {
            'success_count': 0,
            'failure_count': 0,
            'total_tasks': 0,
            'avg_response_time': 0.0,
            'avg_quality_score': 0.0,
            'total_tokens_used': 0,
            'total_cost': 0.0,
            'last_failure_time': None,
            'consecutive_failures': 0,
            'uptime_percentage': 100.0,
            'task_types': defaultdict(int),
            # 🆕 ADVANCED METRICS
            'response_time_history': [],  # Last 20 response times for trend analysis
            'success_history': [],  # Last 20 outcomes for pattern detection
            'quality_history': [],  # Last 20 quality scores
            'cost_per_task': 0.0,
            'predicted_success_rate': 100.0,
            'performance_trend': 'stable',  # stable, improving, degrading
            'optimal_task_types': [],  # Task types this worker excels at
            'learning_phase': True,  # New workers learn faster
            'specialization_score': 0.0  # How specialized vs generalist
        })
        self.lock = threading.Lock()
        self.load_metrics()
    
    def load_metrics(self):
        """Load historical performance data"""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    for worker, stats in data.items():
                        self.metrics[worker].update(stats)
                        # Convert defaultdict
                        if 'task_types' in stats:
                            self.metrics[worker]['task_types'] = defaultdict(int, stats['task_types'])
            except Exception as e:
                print(f"Error loading metrics: {e}")
    
    def save_metrics(self):
        """Persist metrics to disk"""
        with self.lock:
            try:
                data = {}
                for worker, stats in self.metrics.items():
                    data[worker] = dict(stats)
                    data[worker]['task_types'] = dict(stats['task_types'])
                
                with open(self.db_path, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error saving metrics: {e}")
    
    def log_task_result(self, worker_name, task_type, success, duration, 
                       tokens_used=0, cost=0.0, quality_score=None):
        """🆕 ADVANCED: Log task with ML-like learning"""
        with self.lock:
            metrics = self.metrics[worker_name]
            metrics['total_tasks'] += 1
            metrics['task_types'][task_type] += 1
            
            # 🆕 ADAPTIVE LEARNING RATE (faster for new workers, slower for established)
            if metrics['total_tasks'] < 10:
                alpha = 0.5  # Fast learning for new workers
                metrics['learning_phase'] = True
            elif metrics['total_tasks'] < 50:
                alpha = 0.3  # Medium learning
                metrics['learning_phase'] = False
            else:
                alpha = 0.2  # Stable learning for experienced workers
            
            # Basic metrics
            if success:
                metrics['success_count'] += 1
                metrics['consecutive_failures'] = 0
            else:
                metrics['failure_count'] += 1
                metrics['consecutive_failures'] += 1
                metrics['last_failure_time'] = datetime.now().isoformat()
            
            # 🆕 HISTORY TRACKING (last 20 tasks for trend analysis)
            if 'response_time_history' not in metrics:
                metrics['response_time_history'] = []
            metrics['response_time_history'].append(duration)
            if len(metrics['response_time_history']) > 20:
                metrics['response_time_history'].pop(0)
            
            if 'success_history' not in metrics:
                metrics['success_history'] = []
            metrics['success_history'].append(1 if success else 0)
            if len(metrics['success_history']) > 20:
                metrics['success_history'].pop(0)
            
            # Exponential moving average for response time
            if metrics['avg_response_time'] == 0:
                metrics['avg_response_time'] = duration
            else:
                metrics['avg_response_time'] = (
                    alpha * duration + (1 - alpha) * metrics['avg_response_time']
                )
            
            # 🆕 QUALITY TRACKING with history
            if 'quality_history' not in metrics:
                metrics['quality_history'] = []
            if quality_score is not None:
                metrics['quality_history'].append(quality_score)
                if len(metrics['quality_history']) > 20:
                    metrics['quality_history'].pop(0)
            
            # Update average quality
            if quality_score is not None:
                if metrics['avg_quality_score'] == 0:
                    metrics['avg_quality_score'] = quality_score
                else:
                    metrics['avg_quality_score'] = (
                        alpha * quality_score + (1 - alpha) * metrics['avg_quality_score']
                    )
            
            # Token usage
            metrics['total_tokens_used'] += tokens_used
            metrics['total_cost'] += cost
            
            # 🆕 COST PER TASK
            if metrics['total_tasks'] > 0:
                metrics['cost_per_task'] = metrics['total_cost'] / metrics['total_tasks']
            
            # Uptime percentage
            metrics['uptime_percentage'] = (metrics['success_count'] / metrics['total_tasks']) * 100
            
            # 🆕 TREND ANALYSIS
            self._analyze_performance_trend(worker_name)
            
            # 🆕 SPECIALIZATION DETECTION
            self._detect_specialization(worker_name)
            
            # 🆕 PREDICTIVE SUCCESS RATE
            self._calculate_predicted_success(worker_name)
        
        # Auto-save every 5 tasks (more frequent for learning)
        if metrics['total_tasks'] % 5 == 0:
            self.save_metrics()
    
    def get_worker_score(self, worker_name: str, task_type: str = None) -> float:
        """🆕 ADVANCED: ML-like scoring with predictive intelligence"""
        metrics = self.metrics[worker_name]
        
        if metrics['total_tasks'] == 0:
            return 50.0  # Neutral score for new workers
        
        # 🆕 Use PREDICTED success rate instead of historical (more intelligent!)
        predicted_success = metrics.get('predicted_success_rate', metrics['uptime_percentage'])
        success_score = (predicted_success / 100) * 35
        
        # Speed score (25%) - with trend consideration
        speed_score = 0
        if metrics['avg_response_time'] > 0:
            base_speed = min(25, (1 / metrics['avg_response_time']) * 100)
            
            # 🆕 Bonus for improving speed trend
            if len(metrics.get('response_time_history', [])) >= 10:
                recent_avg = statistics.mean(metrics['response_time_history'][-5:])
                older_avg = statistics.mean(metrics['response_time_history'][-10:-5])
                if recent_avg < older_avg:  # Getting faster!
                    base_speed *= 1.1
            
            speed_score = base_speed
        
        # Quality score (20%) - with trend bonus
        quality_score = 0
        if metrics['avg_quality_score'] > 0:
            base_quality = (metrics['avg_quality_score'] / 10) * 20
            
            # 🆕 Bonus for improving quality
            if len(metrics.get('quality_history', [])) >= 10:
                recent_quality = statistics.mean(metrics['quality_history'][-5:])
                older_quality = statistics.mean(metrics['quality_history'][-10:-5])
                if recent_quality > older_quality:  # Getting better!
                    base_quality *= 1.1
            
            quality_score = base_quality
        
        # 🆕 Task type specialization (15% - increased weight)
        expertise_score = 0
        if task_type:
            # Perfect match with specialization
            if task_type in metrics.get('optimal_task_types', []):
                expertise_score = 15  # Full points for specialization
            elif task_type in metrics['task_types']:
                # Has experience but not specialized
                task_count = metrics['task_types'][task_type]
                expertise_score = min(15, (task_count / 10) * 15)
        
        # 🆕 Cost efficiency bonus (5%)
        cost_score = 0
        if metrics.get('cost_per_task', 0) > 0:
            # Lower cost = higher score (inverted)
            # Assume $0.01 per task is good, $0.05 is expensive
            cost_ratio = 0.01 / max(metrics['cost_per_task'], 0.001)
            cost_score = min(5, cost_ratio * 5)
        
        # 🆕 DYNAMIC penalty based on trend
        failure_penalty = 0
        if metrics['consecutive_failures'] > 0:
            # Harsher penalty if degrading
            if metrics.get('performance_trend') == 'degrading':
                failure_penalty = min(30, metrics['consecutive_failures'] * 10)
            else:
                failure_penalty = min(20, metrics['consecutive_failures'] * 5)
        
        # 🆕 Bonus for stable/improving workers
        trend_bonus = 0
        if metrics.get('performance_trend') == 'improving':
            trend_bonus = 5
        elif metrics.get('performance_trend') == 'stable' and metrics['total_tasks'] > 20:
            trend_bonus = 3
        
        total_score = (
            success_score + 
            speed_score + 
            quality_score + 
            expertise_score + 
            cost_score + 
            trend_bonus - 
            failure_penalty
        )
        
        return max(0, min(100, total_score))
    
    def _analyze_performance_trend(self, worker_name):
        """🆕 Detect if worker performance is improving, stable, or degrading"""
        metrics = self.metrics[worker_name]
        
        if len(metrics.get('success_history', [])) < 10:
            metrics['performance_trend'] = 'learning'
            return
        
        # Compare recent vs older performance
        recent = metrics['success_history'][-10:]  # Last 10 tasks
        older = metrics['success_history'][-20:-10] if len(metrics['success_history']) >= 20 else recent
        
        recent_success = sum(recent) / len(recent)
        older_success = sum(older) / len(older) if older else recent_success
        
        diff = recent_success - older_success
        
        if diff > 0.1:
            metrics['performance_trend'] = 'improving'
        elif diff < -0.1:
            metrics['performance_trend'] = 'degrading'
        else:
            metrics['performance_trend'] = 'stable'
    
    def _detect_specialization(self, worker_name):
        """🆕 Identify which task types this worker excels at"""
        metrics = self.metrics[worker_name]
        
        if metrics['total_tasks'] < 15:
            return
        
        task_types = metrics['task_types']
        if not task_types:
            return
        
        # Find task types with high volume
        total = sum(task_types.values())
        specialized_types = []
        
        for task_type, count in task_types.items():
            percentage = (count / total) * 100
            if percentage > 40:  # More than 40% of tasks are this type
                specialized_types.append(task_type)
        
        metrics['optimal_task_types'] = specialized_types
        
        # Calculate specialization score (0-100)
        if specialized_types:
            # Highly specialized
            metrics['specialization_score'] = min(100, max(task_types.values()) / total * 100)
        else:
            # Generalist
            metrics['specialization_score'] = 0
    
    def _calculate_predicted_success(self, worker_name):
        """🆕 Predict success rate for next task based on trends"""
        metrics = self.metrics[worker_name]
        
        if len(metrics.get('success_history', [])) < 5:
            metrics['predicted_success_rate'] = metrics['uptime_percentage']
            return
        
        # Weighted average: recent tasks matter more
        recent = metrics['success_history'][-5:]  # Last 5 tasks
        weights = [1, 1.2, 1.4, 1.6, 2.0]  # More weight to recent
        
        weighted_sum = sum(s * w for s, w in zip(recent, weights[:len(recent)]))
        weight_total = sum(weights[:len(recent)])
        
        predicted = (weighted_sum / weight_total) * 100
        metrics['predicted_success_rate'] = predicted
    
    def is_worker_healthy(self, worker_name: str, max_consecutive_failures: int = 3) -> bool:
        """🆕 ADVANCED: Self-tuning circuit breaker with predictive health check"""
        metrics = self.metrics[worker_name]
        
        # 🆕 DYNAMIC threshold based on worker experience
        if metrics['total_tasks'] < 5:
            # New workers get more chances
            max_failures = max_consecutive_failures + 2
        elif metrics.get('performance_trend') == 'improving':
            # Improving workers get second chances
            max_failures = max_consecutive_failures + 1
        else:
            max_failures = max_consecutive_failures
        
        # Too many consecutive failures
        if metrics['consecutive_failures'] >= max_failures:
            return False
        
        # 🆕 PREDICTIVE: Check if predicted success rate is too low
        predicted = metrics.get('predicted_success_rate', 100)
        if predicted < 40:  # Predicted to fail most tasks
            return False
        
        # 🆕 TREND-BASED: If degrading trend with low uptime
        if metrics.get('performance_trend') == 'degrading':
            if metrics['total_tasks'] > 10 and metrics['uptime_percentage'] < 60:
                return False
        else:
            # Standard threshold for stable workers
            if metrics['total_tasks'] > 10 and metrics['uptime_percentage'] < 50:
                return False
        
        # Recent failure check with adaptive timing
        if metrics['last_failure_time']:
            try:
                last_failure = datetime.fromisoformat(metrics['last_failure_time'])
                time_since = datetime.now() - last_failure
                
                # 🆕 Longer cooldown for degrading workers
                cooldown = timedelta(minutes=5)
                if metrics.get('performance_trend') == 'degrading':
                    cooldown = timedelta(minutes=10)
                
                if time_since < cooldown:
                    return False
            except:
                pass
        
        return True
    
    def get_stats(self, worker_name=None):
        """Get performance statistics"""
        if worker_name:
            return dict(self.metrics[worker_name])
        return {k: dict(v) for k, v in self.metrics.items()}
    
    def reset_worker_stats(self, worker_name):
        """Reset specific worker stats (for recovery)"""
        with self.lock:
            if worker_name in self.metrics:
                self.metrics[worker_name]['consecutive_failures'] = 0
                self.metrics[worker_name]['last_failure_time'] = None
    
    def get_best_worker(self, available_workers, task_type=None):
        """Get best worker based on performance"""
        if not available_workers:
            return None
        
        scored_workers = [
            (worker, self.get_worker_score(worker, task_type))
            for worker in available_workers
        ]
        
        # Sort by score descending
        scored_workers.sort(key=lambda x: x[1], reverse=True)
        return scored_workers
    
    def is_worker_healthy(self, worker_name, max_consecutive_failures=3):
        """Check if worker is healthy (circuit breaker)"""
        metrics = self.metrics[worker_name]
        
        # Too many consecutive failures
        if metrics['consecutive_failures'] >= max_consecutive_failures:
            return False
        
        # Very low uptime
        if metrics['total_tasks'] > 10 and metrics['uptime_percentage'] < 50:
            return False
        
        # Recent failure (within last 5 minutes)
        if metrics['last_failure_time']:
            try:
                last_failure = datetime.fromisoformat(metrics['last_failure_time'])
                if datetime.now() - last_failure < timedelta(minutes=5):
                    if metrics['consecutive_failures'] >= 2:
                        return False
            except:
                pass
        
        return True
    
    def get_stats(self, worker_name=None):
        """Get performance statistics"""
        if worker_name:
            return dict(self.metrics[worker_name])
        return {k: dict(v) for k, v in self.metrics.items()}
    
    def reset_worker_stats(self, worker_name):
        """Reset specific worker stats (for recovery)"""
        with self.lock:
            if worker_name in self.metrics:
                self.metrics[worker_name]['consecutive_failures'] = 0
                self.metrics[worker_name]['last_failure_time'] = None
    
    def get_system_insights(self):
        """🆕 ADVANCED: Get AI-like insights and recommendations"""
        insights = {
            'total_workers': len(self.metrics),
            'healthy_workers': 0,
            'degrading_workers': [],
            'top_performers': [],
            'recommendations': [],
            'cost_analysis': {
                'total_cost': 0.0,
                'avg_cost_per_task': 0.0,
                'most_efficient': None,
                'least_efficient': None
            },
            'specialization_map': {}
        }
        
        all_workers = []
        
        for worker_name, metrics in self.metrics.items():
            if self.is_worker_healthy(worker_name):
                insights['healthy_workers'] += 1
            
            # Track degrading workers
            if metrics.get('performance_trend') == 'degrading':
                insights['degrading_workers'].append({
                    'name': worker_name,
                    'predicted_success': metrics.get('predicted_success_rate', 0),
                    'recent_failures': metrics.get('consecutive_failures', 0)
                })
            
            # Cost analysis
            insights['cost_analysis']['total_cost'] += metrics.get('total_cost', 0)
            
            # Specialization map
            if metrics.get('optimal_task_types'):
                insights['specialization_map'][worker_name] = metrics['optimal_task_types']
            
            all_workers.append((worker_name, self.get_worker_score(worker_name)))
        
        # Top performers
        all_workers.sort(key=lambda x: x[1], reverse=True)
        insights['top_performers'] = [
            {'name': w[0], 'score': w[1]} 
            for w in all_workers[:3]
        ]
        
        # Cost efficiency
        total_tasks = sum(m.get('total_tasks', 0) for m in self.metrics.values())
        if total_tasks > 0:
            insights['cost_analysis']['avg_cost_per_task'] = (
                insights['cost_analysis']['total_cost'] / total_tasks
            )
        
        # Find most/least efficient
        workers_by_cost = [
            (name, m.get('cost_per_task', 0))
            for name, m in self.metrics.items()
            if m.get('total_tasks', 0) > 5
        ]
        if workers_by_cost:
            workers_by_cost.sort(key=lambda x: x[1])
            insights['cost_analysis']['most_efficient'] = workers_by_cost[0][0]
            insights['cost_analysis']['least_efficient'] = workers_by_cost[-1][0]
        
        # Generate recommendations
        if len(insights['degrading_workers']) > 0:
            insights['recommendations'].append(
                f"⚠️ {len(insights['degrading_workers'])} worker(s) showing degraded performance - consider restart"
            )
        
        if insights['healthy_workers'] < 2:
            insights['recommendations'].append(
                "⚠️ Low worker availability - consider starting more workers"
            )
        
        specialized_workers = len(insights['specialization_map'])
        if specialized_workers == 0 and total_tasks > 50:
            insights['recommendations'].append(
                "💡 No specialized workers detected - consider dedicated workers per task type"
            )
        
        if not insights['recommendations']:
            insights['recommendations'].append("✅ System operating optimally!")
        
        return insights