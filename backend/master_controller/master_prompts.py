"""
AI System Prompts for E.V.E. Master Controller
Optimized for groq/compound
Updated for real workers: Image Generation, Documentation, Coding
"""

# =============================================================================
# TASK TYPE DETECTION PROMPT
# =============================================================================

TASK_TYPE_DETECTION_PROMPT = """Analyze this task and classify its type.

Task: "{task_description}"

Available Categories:
- coding: Programming, debugging, writing code, algorithms, technical implementation, API development
- documentation: Writing reports, guides, technical documentation, user manuals, API docs, specifications, **SUMMARIZING DOCUMENTS**, reading document files, analyzing written content, extracting information from documents
- image_generation: Creating images, logos, illustrations, diagrams, visual content, graphics, designs
- general: Everything else that doesn't fit the above categories

IMPORTANT: If the user asks to "summarize", "read", "analyze", or "extract from" a DOCUMENT FILE (.docx, .pdf, .txt), classify as 'documentation'.

Respond in EXACTLY this format (no extra text):
TASK_TYPE: <one category from above>
CONFIDENCE: <number between 0.0 and 1.0>
REASONING: <one clear sentence explaining your choice>

Example 1:
TASK_TYPE: coding
CONFIDENCE: 0.98
REASONING: Task requires implementing a sorting algorithm which is clearly a programming task.

Example 2:
TASK_TYPE: image_generation
CONFIDENCE: 0.95
REASONING: User requests generating a visual image of a sunset which requires image generation AI.

Example 3:
TASK_TYPE: documentation
CONFIDENCE: 0.92
REASONING: Task involves writing technical documentation for an API endpoint.

Example 4:
TASK_TYPE: documentation
CONFIDENCE: 0.96
REASONING: User asks to summarize a document file which is a documentation/reading task."""

# =============================================================================
# CONTEXT DETECTION PROMPT  
# =============================================================================

CONTEXT_DETECTION_PROMPT = """Determine if this message refers to previous conversation.

Previous Conversation (last few messages):
{conversation_history}

Current User Message: "{current_message}"

Messages that NEED context (refer to previous):
- "Add error handling to that function"
- "Can you explain it better?"
- "What were the main points?"
- "Continue from where you left off"
- "Make it faster"
- "Improve the image"
- "Add more detail to the document"
- Uses pronouns: "it", "that", "this", "those", "them"

Messages that DON'T NEED context (standalone):
- "Write a Python function to sort a list"
- "Generate an image of a sunset"
- "Create documentation for user authentication"
- "What is machine learning?"

Respond in EXACTLY this format:
NEEDS_CONTEXT: YES or NO
REASON: <one sentence explaining your decision>

Example:
NEEDS_CONTEXT: YES
REASON: User says "that function" which clearly refers to code mentioned in previous conversation."""

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def build_task_detection_prompt(task_description: str) -> str:
    """Build the task type detection prompt"""
    return TASK_TYPE_DETECTION_PROMPT.format(
        task_description=task_description
    )

def build_context_detection_prompt(
    current_message: str,
    conversation_history: str
) -> str:
    """Build the context detection prompt"""
    return CONTEXT_DETECTION_PROMPT.format(
        current_message=current_message,
        conversation_history=conversation_history or "No previous conversation"
    )

# =============================================================================
# FORMAT CONVERSATION HISTORY
# =============================================================================

def format_conversation_history(history: list) -> str:
    """Format conversation history for AI"""
    
    if not history:
        return "No previous conversation"
    
    formatted = ""
    
    # Take last 3 messages for context
    recent_messages = history[-3:] if len(history) > 3 else history
    
    for i, msg in enumerate(recent_messages, 1):
        role = msg['role'].capitalize()
        
        # Truncate very long messages
        content = msg['content']
        if len(content) > 150:
            content = content[:150] + "..."
        
        formatted += f"{i}. {role}: {content}\n"
    
    return formatted.strip()

# =============================================================================
# FORMAT WORKER DETAILS (Not used in always-best strategy, but kept for compatibility)
# =============================================================================

def format_worker_details(workers: dict, task_type: str) -> str:
    """Format worker information for AI (compatibility function)"""
    
    details = ""
    
    for worker_id, info in workers.items():
        details += f"\n{worker_id}:\n"
        details += f"  - Specialization: {info.get('specialization', 'general')}\n"
        details += f"  - Current active tasks: {info.get('active_tasks', 0)}\n"
        details += f"  - Status: {info.get('status', 'unknown')}\n"
        
        perf = info.get('performance_for_task_type', {})
        
        if perf and perf.get('total_tasks', 0) > 0:
            details += f"  - Performance for '{task_type}' tasks:\n"
            details += f"    * Success rate: {perf.get('success_rate', 0)*100:.0f}%\n"
            details += f"    * Avg execution time: {perf.get('avg_execution_time', 0):.1f}s\n"
            details += f"    * Total tasks: {perf.get('total_tasks', 0)}\n"
        else:
            details += f"  - No performance history for '{task_type}' yet\n"
        
        details += "\n"
    
    return details.strip()

# =============================================================================
# PARSE AI RESPONSES
# =============================================================================

def parse_task_type_response(response_text: str) -> tuple:
    """
    Parse AI's task type detection response
    
    Returns: (task_type, confidence, reasoning)
    """
    
    task_type = "general"
    confidence = 0.5
    reasoning = "AI analysis"
    
    for line in response_text.split("\n"):
        line = line.strip()
        
        if line.startswith("TASK_TYPE:"):
            task_type = line.split("TASK_TYPE:")[1].strip().lower()
            # Remove punctuation
            task_type = task_type.replace(".", "").replace(",", "")
            
        elif line.startswith("CONFIDENCE:"):
            try:
                conf_str = line.split("CONFIDENCE:")[1].strip()
                # Remove non-numeric except decimal
                conf_str = ''.join(c for c in conf_str if c.isdigit() or c == '.')
                confidence = float(conf_str)
                confidence = max(0.0, min(1.0, confidence))
            except:
                confidence = 0.7
                
        elif line.startswith("REASONING:"):
            reasoning = line.split("REASONING:")[1].strip()
    
    return task_type, confidence, reasoning

def parse_context_detection_response(response_text: str) -> tuple:
    """
    Parse AI's context detection response
    
    Returns: (needs_context, reason)
    """
    
    needs_context = False
    reason = "AI analysis"
    
    for line in response_text.split("\n"):
        line = line.strip()
        
        if line.startswith("NEEDS_CONTEXT:"):
            answer = line.split("NEEDS_CONTEXT:")[1].strip().upper()
            needs_context = "YES" in answer
            
        elif line.startswith("REASON:"):
            reason = line.split("REASON:")[1].strip()
    
    return needs_context, reason

def build_worker_selection_prompt(task_description: str, task_type: str, worker_details: str) -> str:
    """Compatibility function - not used in always-best strategy"""
    return ""

def parse_worker_selection_response(response_text: str) -> tuple:
    """Compatibility function - not used in always-best strategy"""
    return None, "Compatibility function"