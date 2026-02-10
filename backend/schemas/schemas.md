# E.V.E. Schema Files Documentation

## 📋 Overview

This directory contains all Pydantic schema files for the E.V.E. Master Controller API. These schemas provide type validation, serialization, and documentation for API endpoints.

---

## 📁 Schema Files

### 1. **auth.py** - Authentication Schemas

Complete authentication system with JWT tokens, user management, and security features.

#### Request Schemas:
- `RegisterRequest` - User registration (email, password)
- `LoginRequest` - User login
- `PasswordChangeRequest` - Change password (authenticated)
- `PasswordResetRequest` - Forgot password flow
- `TokenRefreshRequest` - Refresh access token
- `UserUpdateRequest` - Update user profile
- `UserStatusUpdate` - Admin: update user status

#### Response Schemas:
- `UserResponse` - User information
- `LoginResponse` - Login success with tokens
- `TokenResponse` - Token validation/refresh
- `MessageResponse` - Generic success message
- `ErrorResponse` - Error details
- `UserListResponse` - List of users (admin)
- `AuthLog` - Authentication log entry

#### Internal Schemas:
- `TokenPayload` - JWT token structure

---

### 2. **task.py** - Task Management Schemas

Complete task lifecycle management with queue, assignment, and execution tracking.

#### Enums:
- `TaskStatus` - pending, queued, assigned, processing, completed, failed, cancelled
- `TaskType` - general, image_generation, text_analysis, code_execution, etc.
- `TaskPriority` - LOW (1), MEDIUM (2), HIGH (3), URGENT (4)

#### Request Schemas:
- `TaskCreateRequest` - Create new task
- `TaskUpdateRequest` - Update existing task
- `TaskCancelRequest` - Cancel task
- `TaskRetryRequest` - Retry failed task
- `TaskBatchRequest` - Create multiple tasks
- `TaskFilterRequest` - Filter tasks by criteria
- `TaskSearchRequest` - Search tasks by description
- `BulkCancelRequest` - Cancel multiple tasks
- `BulkRetryRequest` - Retry multiple tasks

#### Response Schemas:
- `TaskResponse` - Basic task info
- `TaskDetailedResponse` - Task with assignment & result
- `TaskListResponse` - Paginated task list
- `TaskCreatedResponse` - Task creation confirmation
- `TaskResultResponse` - Execution result
- `TaskStatsResponse` - Task statistics
- `QueueStatusResponse` - Queue status
- `QueuePositionResponse` - Task position in queue
- `TaskAssignment` - Assignment information
- `AssignmentListResponse` - List of assignments
- `BatchOperationResponse` - Batch operation results

---

### 3. **conversation.py** - Conversation & Message Schemas

Complete conversation history and context management for AI interactions.

#### Enums:
- `MessageRole` - user, assistant, system
- `ConversationStatus` - active, inactive, archived

#### Request Schemas:
- `ConversationCreateRequest` - Start new conversation
- `MessageCreateRequest` - Add message
- `MessageBatchRequest` - Add multiple messages
- `ConversationUpdateRequest` - Update conversation
- `ContextRetrievalRequest` - Get conversation context
- `ConversationSearchRequest` - Search conversations
- `ContextCreateRequest` - Store context data
- `ConversationExportRequest` - Export conversation
- `ConversationImportRequest` - Import conversation
- `ArchiveRequest` - Archive conversation
- `BulkArchiveRequest` - Archive multiple conversations
- `ConversationSummaryRequest` - Generate summary
- `MessageUpdateRequest` - Update message (admin)
- `ConversationMergeRequest` - Merge conversations

#### Response Schemas:
- `MessageResponse` - Single message
- `ConversationResponse` - Conversation metadata
- `ConversationDetailedResponse` - Conversation with messages
- `ConversationListResponse` - Paginated conversation list
- `MessageListResponse` - Paginated message list
- `ContextResponse` - Context for AI
- `ConversationStatsResponse` - Statistics
- `ContextData` - Stored context data
- `ContextListResponse` - List of contexts
- `ConversationExportResponse` - Exported data
- `ArchiveResponse` - Archive operation result
- `BulkArchiveResponse` - Bulk archive results
- `ConversationSummaryResponse` - Generated summary
- `ConversationMergeResponse` - Merge operation result

---

## 🔧 Usage Examples

### Authentication Example

```python
from schemas.auth import RegisterRequest, LoginRequest, LoginResponse

# Registration
register_data = RegisterRequest(
    email="user@example.com",
    password="secure_password123"
)

# Login
login_data = LoginRequest(
    email="user@example.com",
    password="secure_password123"
)

# Response
login_response = LoginResponse(
    access_token="eyJ0eXAiOiJKV1QiLCJhbGc...",
    refresh_token="dGhpc2lzYXJlZnJlc2h0b2tlbg...",
    token_type="bearer",
    expires_in=3600,
    user=UserResponse(
        user_id=1,
        email="user@example.com",
        role="user",
        status="active",
        created_at=datetime.now()
    )
)
```

### Task Creation Example

```python
from schemas.task import TaskCreateRequest, TaskType, TaskPriority

# Create task
task_request = TaskCreateRequest(
    task_desc="Generate an image of a sunset over mountains",
    task_type=TaskType.IMAGE_GENERATION,
    priority=TaskPriority.HIGH,
    metadata={
        "style": "photorealistic",
        "resolution": "1024x1024"
    },
    context_data="User prefers warm colors and dramatic lighting"
)
```

### Conversation Example

```python
from schemas.conversation import (
    ConversationCreateRequest,
    MessageCreateRequest,
    MessageRole,
    ContextRetrievalRequest
)

# Create conversation
conversation = ConversationCreateRequest(
    metadata={"topic": "AI assistance"}
)

# Add message
message = MessageCreateRequest(
    conversation_id="conv_abc123",
    role=MessageRole.USER,
    content="Hello, can you help me with Python?"
)

# Get context for AI
context_request = ContextRetrievalRequest(
    conversation_id="conv_abc123",
    last_n_messages=10,
    include_system=False
)
```

---

## 📊 Schema Relationships

```
Users (auth.py)
  ↓
  ├─→ Tasks (task.py)
  │     ↓
  │     ├─→ Task Assignments
  │     ├─→ Task Results
  │     └─→ Task Queue
  │
  └─→ Conversations (conversation.py)
        ↓
        ├─→ Messages
        └─→ Context Data
```

---

## 🛡️ Validation Features

All schemas include:
- ✅ Type validation
- ✅ Field constraints (min/max length, ranges)
- ✅ Email validation
- ✅ Enum validation
- ✅ Optional/required field handling
- ✅ Pattern matching (regex)
- ✅ Nested object validation
- ✅ Custom validation rules

---

## 🚀 Integration with FastAPI

```python
from fastapi import APIRouter, Depends, HTTPException
from schemas.auth import LoginRequest, LoginResponse
from schemas.task import TaskCreateRequest, TaskResponse
from schemas.conversation import MessageCreateRequest, MessageResponse

router = APIRouter()

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Pydantic automatically validates the request
    # Returns validated LoginResponse
    pass

@router.post("/tasks", response_model=TaskResponse)
async def create_task(request: TaskCreateRequest, user_id: int):
    # Request is validated and typed
    # Response is validated and serialized
    pass

@router.post("/conversations/{conv_id}/messages", response_model=MessageResponse)
async def add_message(conv_id: str, request: MessageCreateRequest):
    # Automatic validation and serialization
    pass
```

---

## 📝 Best Practices

1. **Always use type hints** - Pydantic enforces types
2. **Use Enums** for fixed choices - Better validation and autocomplete
3. **Set field constraints** - min_length, max_length, ge, le, pattern
4. **Provide descriptions** - Helps with API documentation
5. **Use Optional** for non-required fields
6. **Separate Request/Response** - Different validation rules
7. **Enable `from_attributes`** - For ORM model conversion
8. **Use `Field`** for advanced validation

---

## 🔄 Schema Updates

When updating schemas:
1. Maintain backward compatibility
2. Use `Optional` for new fields
3. Document breaking changes
4. Version your API if needed
5. Update API documentation
6. Test with existing clients

---

## 📚 Additional Resources

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Type Hints (Python)](https://docs.python.org/3/library/typing.html)

---

## 🎯 Summary

- **auth.py** - 15+ schemas for authentication & user management
- **task.py** - 25+ schemas for complete task lifecycle
- **conversation.py** - 25+ schemas for conversation & message tracking

**Total**: 65+ production-ready schemas covering all API functionality!