"""
Task Management Schemas for E.V.E. Master Controller
Includes: Task Creation, Updates, Results, Queue Management
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== ENUMS ==========

class TaskStatus(str, Enum):
    """Task status enumeration"""
    PENDING = "pending"
    QUEUED = "queued"
    ASSIGNED = "assigned"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """Task type enumeration"""
    GENERAL = "general"
    IMAGE_GENERATION = "image_generation"
    TEXT_ANALYSIS = "text_analysis"
    CODE_EXECUTION = "code_execution"
    DATA_PROCESSING = "data_processing"
    WEB_SCRAPING = "web_scraping"
    CUSTOM = "custom"


class TaskPriority(int, Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


# ========== REQUEST SCHEMAS ==========

class TaskCreateRequest(BaseModel):
    """Create new task request"""
    task_desc: str = Field(min_length=1, max_length=5000, description="Task description")
    task_type: Optional[TaskType] = TaskType.GENERAL
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    metadata: Optional[Dict[str, Any]] = None  # Additional task parameters
    context_data: Optional[str] = None  # Optional context for the task


class TaskUpdateRequest(BaseModel):
    """Update existing task"""
    task_desc: Optional[str] = Field(None, min_length=1, max_length=5000)
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    task_status: Optional[TaskStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskCancelRequest(BaseModel):
    """Cancel task request"""
    task_id: int
    reason: Optional[str] = None


class TaskRetryRequest(BaseModel):
    """Retry failed task"""
    task_id: int
    force: bool = False  # Force retry even if max retries exceeded


class TaskBatchRequest(BaseModel):
    """Create multiple tasks at once"""
    tasks: List[TaskCreateRequest]
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM


# ========== RESPONSE SCHEMAS ==========

class TaskResponse(BaseModel):
    """Single task response"""
    task_id: int
    user_id: int
    task_desc: str
    task_status: str
    task_type: str
    priority: int
    retry_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TaskDetailedResponse(TaskResponse):
    """Detailed task response with assignment and result info"""
    assigned_agent: Optional[Dict[str, Any]] = None  # Agent info if assigned
    result: Optional[Dict[str, Any]] = None  # Execution result if completed
    context: Optional[str] = None  # Task context data
    execution_time: Optional[float] = None


class TaskListResponse(BaseModel):
    """List of tasks response"""
    tasks: List[TaskResponse]
    total: int
    page: int = 1
    page_size: int = 50


class TaskCreatedResponse(BaseModel):
    """Task creation confirmation"""
    task_id: int
    message: str
    task_status: str
    estimated_wait_time: Optional[int] = None  # seconds


class TaskResultResponse(BaseModel):
    """Task execution result"""
    task_id: int
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    output_data: str
    success: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    completed_at: datetime
    
    class Config:
        from_attributes = True


class TaskStatsResponse(BaseModel):
    """Task statistics"""
    total_tasks: int
    completed: int
    failed: int
    pending: int
    queued: int
    assigned: int
    processing: int
    success_rate: float
    avg_execution_time: Optional[float] = None


# ========== QUEUE SCHEMAS ==========

class QueueStatusResponse(BaseModel):
    """Current queue status"""
    total_queued: int
    high_priority: int
    medium_priority: int
    low_priority: int
    avg_wait_time: Optional[float] = None
    next_tasks: List[TaskResponse]


class QueuePositionResponse(BaseModel):
    """Task position in queue"""
    task_id: int
    position: int
    total_ahead: int
    estimated_wait_time: Optional[int] = None  # seconds


# ========== ASSIGNMENT SCHEMAS ==========

class TaskAssignment(BaseModel):
    """Task assignment information"""
    task_id: int
    agent_id: int
    agent_name: str
    assigned_at: datetime
    assignment_order: int
    
    class Config:
        from_attributes = True


class AssignmentListResponse(BaseModel):
    """List of task assignments"""
    assignments: List[TaskAssignment]
    total: int


# ========== FILTER/SEARCH SCHEMAS ==========

class TaskFilterRequest(BaseModel):
    """Filter tasks by various criteria"""
    user_id: Optional[int] = None
    task_status: Optional[TaskStatus] = None
    task_type: Optional[TaskType] = None
    priority: Optional[TaskPriority] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


class TaskSearchRequest(BaseModel):
    """Search tasks by description"""
    query: str = Field(min_length=1, max_length=200)
    task_status: Optional[TaskStatus] = None
    task_type: Optional[TaskType] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


# ========== BATCH OPERATION SCHEMAS ==========

class BatchOperationResponse(BaseModel):
    """Response for batch operations"""
    total_requested: int
    successful: int
    failed: int
    task_ids: List[int]
    errors: Optional[List[Dict[str, Any]]] = None
    message: str


class BulkCancelRequest(BaseModel):
    """Cancel multiple tasks"""
    task_ids: List[int]
    reason: Optional[str] = None


class BulkRetryRequest(BaseModel):
    """Retry multiple failed tasks"""
    task_ids: List[int]
    force: bool = False