"""
Conversation & Message Schemas for E.V.E. Master Controller
Includes: Conversation Management, Message History, Context Tracking
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ========== ENUMS ==========

class MessageRole(str, Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ConversationStatus(str, Enum):
    """Conversation status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


# ========== REQUEST SCHEMAS ==========

class ConversationCreateRequest(BaseModel):
    """Create new conversation"""
    conversation_id: Optional[str] = None  # Auto-generated if not provided
    metadata: Optional[Dict[str, Any]] = None  # Additional conversation metadata


class MessageCreateRequest(BaseModel):
    """Add message to conversation"""
    conversation_id: str
    role: MessageRole
    content: str = Field(min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None  # Additional message metadata


class MessageBatchRequest(BaseModel):
    """Add multiple messages to conversation"""
    conversation_id: str
    messages: List[Dict[str, str]]  # List of {role, content} dicts


class ConversationUpdateRequest(BaseModel):
    """Update conversation metadata"""
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class ContextRetrievalRequest(BaseModel):
    """Request conversation context"""
    conversation_id: str
    last_n_messages: int = Field(10, ge=1, le=100, description="Number of recent messages to retrieve")
    include_system: bool = False  # Include system messages


class ConversationSearchRequest(BaseModel):
    """Search conversations"""
    query: Optional[str] = None
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=100)


# ========== RESPONSE SCHEMAS ==========

class MessageResponse(BaseModel):
    """Single message response"""
    message_id: int
    conversation_id: str
    role: str
    content: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation metadata response"""
    conversation_id: str
    user_id: int
    started_at: datetime
    last_updated: datetime
    is_active: bool
    message_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class ConversationDetailedResponse(ConversationResponse):
    """Detailed conversation with messages"""
    messages: List[MessageResponse]
    total_messages: int


class ConversationListResponse(BaseModel):
    """List of conversations"""
    conversations: List[ConversationResponse]
    total: int
    page: int = 1
    page_size: int = 50


class MessageListResponse(BaseModel):
    """List of messages"""
    messages: List[MessageResponse]
    total: int
    conversation_id: str
    page: int = 1
    page_size: int = 50


class ContextResponse(BaseModel):
    """Conversation context for AI"""
    conversation_id: str
    messages: List[MessageResponse]
    total_retrieved: int
    context_window_used: int  # Approximate tokens/characters used
    

class ConversationStatsResponse(BaseModel):
    """Conversation statistics"""
    total_conversations: int
    active_conversations: int
    inactive_conversations: int
    archived_conversations: int
    total_messages: int
    avg_messages_per_conversation: float
    most_active_user: Optional[Dict[str, Any]] = None


# ========== CONTEXT TRACKING SCHEMAS ==========

class ContextData(BaseModel):
    """Context data storage"""
    context_id: int
    task_id: int
    context_data: str
    context_type: str
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContextCreateRequest(BaseModel):
    """Create context data"""
    task_id: int
    context_data: str
    context_type: str = "conversation"


class ContextListResponse(BaseModel):
    """List of context data"""
    contexts: List[ContextData]
    total: int


# ========== EXPORT/IMPORT SCHEMAS ==========

class ConversationExportRequest(BaseModel):
    """Request conversation export"""
    conversation_id: str
    format: str = Field("json", pattern="^(json|txt|markdown)$")
    include_metadata: bool = True


class ConversationExportResponse(BaseModel):
    """Exported conversation data"""
    conversation_id: str
    format: str
    data: str  # Exported data as string
    exported_at: datetime


class ConversationImportRequest(BaseModel):
    """Import conversation from external source"""
    conversation_id: Optional[str] = None
    user_id: int
    messages: List[Dict[str, str]]  # List of {role, content, timestamp?}
    metadata: Optional[Dict[str, Any]] = None


# ========== ARCHIVE SCHEMAS ==========

class ArchiveRequest(BaseModel):
    """Archive conversation"""
    conversation_id: str
    reason: Optional[str] = None


class ArchiveResponse(BaseModel):
    """Archive operation response"""
    conversation_id: str
    archived: bool
    message: str
    archived_at: datetime


class BulkArchiveRequest(BaseModel):
    """Archive multiple conversations"""
    conversation_ids: List[str]
    reason: Optional[str] = None


class BulkArchiveResponse(BaseModel):
    """Bulk archive response"""
    total_requested: int
    successful: int
    failed: int
    conversation_ids: List[str]
    errors: Optional[List[Dict[str, Any]]] = None


# ========== SUMMARY SCHEMAS ==========

class ConversationSummaryRequest(BaseModel):
    """Request conversation summary"""
    conversation_id: str
    max_length: int = Field(500, ge=50, le=2000)
    include_key_points: bool = True


class ConversationSummaryResponse(BaseModel):
    """Generated conversation summary"""
    conversation_id: str
    summary: str
    key_points: Optional[List[str]] = None
    message_count: int
    generated_at: datetime


# ========== UTILITY SCHEMAS ==========

class MessageUpdateRequest(BaseModel):
    """Update message (admin only)"""
    content: Optional[str] = Field(None, min_length=1, max_length=10000)
    metadata: Optional[Dict[str, Any]] = None


class ConversationMergeRequest(BaseModel):
    """Merge multiple conversations"""
    source_conversation_ids: List[str]
    target_conversation_id: Optional[str] = None  # Create new if not provided
    delete_sources: bool = False


class ConversationMergeResponse(BaseModel):
    """Merge operation response"""
    target_conversation_id: str
    merged_count: int
    total_messages: int
    message: str