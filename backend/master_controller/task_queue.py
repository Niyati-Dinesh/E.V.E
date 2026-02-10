"""
Smart Task Queue with Priority Management
Works with distributed worker architecture
"""
import heapq
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from enum import IntEnum
import uuid

class Priority(IntEnum):
    """Task priority levels"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3

@dataclass(order=True)
class Task:
    """Task with priority and metadata"""
    priority: int
    timestamp: float = field(compare=False)
    task_id: str = field(compare=False)
    task_type: str = field(compare=False)
    payload: Any = field(compare=False)
    callback: Callable = field(compare=False, default=None)
    max_retries: int = field(compare=False, default=3)
    retry_count: int = field(compare=False, default=0)
    
    def __post_init__(self):
        if not self.task_id:
            self.task_id = str(uuid.uuid4())

class SmartTaskQueue:
    """Priority queue with intelligent task management"""
    
    def __init__(self, max_size=1000):
        self.queue = []
        self.max_size = max_size
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.task_map = {}  # task_id -> Task
        self.processing = set()  # Currently processing task IDs
        
    def enqueue(self, task_type, payload, priority=Priority.NORMAL, 
                callback=None, max_retries=3):
        """Add task to queue"""
        with self.lock:
            if len(self.queue) >= self.max_size:
                raise Exception("Queue is full")
            
            task = Task(
                priority=priority,
                timestamp=time.time(),
                task_id=str(uuid.uuid4()),
                task_type=task_type,
                payload=payload,
                callback=callback,
                max_retries=max_retries
            )
            
            heapq.heappush(self.queue, task)
            self.task_map[task.task_id] = task
            self.not_empty.notify()
            
            return task.task_id
    
    def dequeue(self, timeout=None):
        """Get highest priority task"""
        with self.not_empty:
            while not self.queue:
                self.not_empty.wait(timeout)
                if timeout and not self.queue:
                    return None
            
            task = heapq.heappop(self.queue)
            self.processing.add(task.task_id)
            return task
    
    def mark_complete(self, task_id, success=True):
        """Mark task as completed"""
        with self.lock:
            if task_id in self.processing:
                self.processing.remove(task_id)
            
            if task_id in self.task_map:
                task = self.task_map[task_id]
                
                if not success and task.retry_count < task.max_retries:
                    # Re-queue with increased retry count
                    task.retry_count += 1
                    task.timestamp = time.time()
                    heapq.heappush(self.queue, task)
                    return False  # Not truly complete, will retry
                
                del self.task_map[task_id]
                return True
    
    def get_queue_stats(self):
        """Get queue statistics"""
        with self.lock:
            priority_counts = {p.name: 0 for p in Priority}
            for task in self.queue:
                for p in Priority:
                    if task.priority == p:
                        priority_counts[p.name] += 1
                        break
            
            return {
                'total': len(self.queue),
                'processing': len(self.processing),
                'by_priority': priority_counts,
                'oldest_task_age': time.time() - self.queue[0].timestamp if self.queue else 0
            }
    
    def size(self):
        """Get current queue size"""
        with self.lock:
            return len(self.queue)
    
    def clear(self):
        """Clear all tasks"""
        with self.lock:
            self.queue.clear()
            self.task_map.clear()
            self.processing.clear()