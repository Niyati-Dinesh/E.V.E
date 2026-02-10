"""
Context Engine for E.V.E. Master Controller
Uses Groq API with Llama 3.3 for intelligent context detection
"""

from groq import Groq
from typing import List, Dict, Tuple
from core.database import get_last_n_messages
from core.config import (
    GROQ_API_KEY,
    MASTER_AI_MODEL,
    AI_MAX_TOKENS,
    REFERENCE_KEYWORDS,
    MAX_CONTEXT_MESSAGES,
    ENABLE_CONTEXT_ENGINE
)
from master_prompts import (
    build_context_detection_prompt,
    format_conversation_history,
    parse_context_detection_response
)

# Initialize Groq client
client = None
if GROQ_API_KEY:
    try:
        client = Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        print(f"⚠️  Failed to initialize Groq for context engine: {e}")
        client = None

# =============================================================================
# SIMPLE CONTEXT DETECTION (Fallback)
# =============================================================================

def needs_context_simple(user_message: str) -> bool:
    """
    Quick keyword-based context detection
    Checks for reference words like "that", "this", "earlier"
    """
    message_lower = user_message.lower()
    
    for keyword in REFERENCE_KEYWORDS:
        if keyword in message_lower:
            return True
    
    return False

# =============================================================================
# AI-POWERED CONTEXT DETECTION
# =============================================================================

def needs_context_ai(
    user_message: str,
    conversation_history: List[Dict]
) -> Tuple[bool, str]:
    """
    Use Llama to intelligently detect if context is needed
    
    Llama understands subtle references that keywords miss:
    - "Can you elaborate?" (needs context, no obvious keyword)
    - "Continue" (clearly needs context)
    - "What's 2+2?" (doesn't need context)
    
    Returns: (needs_context: bool, reason: str)
    """
    
    if not client:
        result = needs_context_simple(user_message)
        return result, "Simple keyword detection (no API key)"
    
    # Format conversation history for Llama
    history_text = format_conversation_history(conversation_history)
    
    # Build prompt
    prompt = build_context_detection_prompt(user_message, history_text)
    
    try:
        response = client.chat.completions.create(
            model=MASTER_AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=AI_MAX_TOKENS,
            temperature=0.3  # Lower temperature for consistent detection
        )
        
        result = response.choices[0].message.content.strip()
        
        # Parse Llama's response
        needs_ctx, reason = parse_context_detection_response(result)
        
        return needs_ctx, reason
        
    except Exception as e:
        print(f"⚠️  AI context detection error: {str(e)[:100]}")
        result = needs_context_simple(user_message)
        return result, f"Fallback to keywords (error: {str(e)[:30]})"

# =============================================================================
# HYBRID DETECTION (Smart Strategy)
# =============================================================================

def needs_context(
    user_message: str,
    conversation_history: List[Dict] = None
) -> Tuple[bool, str]:
    """
    MAIN FUNCTION - Smart hybrid context detection
    
    Strategy:
    1. No conversation history? → No context possible
    2. Quick keyword check first (fast)
    3. If keywords found → Use AI to confirm
    4. If message is very short → Use AI to double-check
    
    Returns: (needs_context: bool, reason: str)
    """
    
    # Feature disabled?
    if not ENABLE_CONTEXT_ENGINE:
        return False, "Context engine disabled in config"
    
    # No history? No context possible
    if not conversation_history or len(conversation_history) == 0:
        return False, "No previous conversation exists"
    
    # Quick keyword check
    has_keywords = needs_context_simple(user_message)
    
    if has_keywords:
        # Keywords found, use AI to confirm if available
        if client:
            needs_ctx, reason = needs_context_ai(user_message, conversation_history)
            return needs_ctx, f"AI confirmed: {reason}"
        else:
            # No AI, trust keywords
            found_keywords = [k for k in REFERENCE_KEYWORDS if k in user_message.lower()]
            return True, f"Keywords detected: {', '.join(found_keywords[:3])}"
    else:
        # No keywords found
        # But very short messages might still need context
        word_count = len(user_message.split())
        
        if word_count < 5 and client:
            # Messages like "Continue", "More details", "Explain" need AI check
            needs_ctx, reason = needs_context_ai(user_message, conversation_history)
            return needs_ctx, f"Short message analysis: {reason}"
        else:
            # Long message with no keywords → probably doesn't need context
            return False, "No reference keywords and message is substantial"

# =============================================================================
# PROMPT BUILDING WITH CONTEXT
# =============================================================================

def build_prompt_with_context(
    conversation_id: str,
    current_message: str,
    max_messages: int = MAX_CONTEXT_MESSAGES
) -> Tuple[str, int]:
    """
    Build complete prompt including conversation history
    
    This creates the full prompt that gets sent to workers
    
    Example output:
    '''
    === Previous Conversation ===
    User: Write a Python function to add numbers
    Assistant: def add(a, b):
        return a + b
    
    === Current Request ===
    User: Add error handling to that
    
    Instructions: Respond considering the context above.
    '''
    
    Returns: (full_prompt: str, context_message_count: int)
    """
    
    # Fetch conversation history from database
    history = get_last_n_messages(conversation_id, max_messages)
    
    if not history:
        # No history, return simple prompt
        return current_message, 0
    
    # Build context section
    context_section = "=== Previous Conversation ===\n"
    for msg in history:
        role = msg['role'].capitalize()
        content = msg['content']
        context_section += f"{role}: {content}\n\n"
    
    # Build complete prompt
    full_prompt = f"""{context_section}=== Current Request ===
User: {current_message}

Instructions: Please respond to the current request above, taking into account the previous conversation context. Maintain consistency with earlier responses and reference them when relevant."""
    
    return full_prompt, len(history)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_context_summary(conversation_id: str, limit: int = 5) -> str:
    """
    Format conversation history for display/logging
    Makes it easy to see what context was used
    """
    history = get_last_n_messages(conversation_id, limit)
    
    if not history:
        return "No context available"
    
    summary = f"Last {len(history)} messages:\n"
    for i, msg in enumerate(history, 1):
        role_emoji = "👤" if msg['role'] == 'user' else "🤖"
        
        # Truncate long messages
        content = msg['content']
        if len(content) > 60:
            content = content[:60] + "..."
        
        summary += f"  {i}. {role_emoji} {content}\n"
    
    return summary

# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Context Engine with Groq/Llama")
    print("="*60)
    
    # Test cases: (message, expected_needs_context)
    test_cases = [
        ("Write a Python function to add numbers", False),
        ("Now add error handling to that", True),
        ("What were the key points?", True),
        ("Explain quantum computing", False),
        ("Can you elaborate?", True),
        ("Continue", True),
        ("What's the weather today?", False),
        ("Make it faster", True),
        ("Calculate 15% of 200", False)
    ]
    
    print("\n📋 Context Detection Tests:")
    print("-" * 60)
    
    # Create fake conversation history for testing
    fake_history = [
        {"role": "user", "content": "Write a Python function"},
        {"role": "assistant", "content": "def example(): pass"}
    ]
    
    for i, (message, expected) in enumerate(test_cases, 1):
        print(f"\n{i}. Message: \"{message}\"")
        print(f"   Expected: {'Needs context' if expected else 'No context'}")
        
        # Test with simple detection
        simple_result = needs_context_simple(message)
        print(f"   Simple: {'Needs context' if simple_result else 'No context'}")
        
        # Test with AI if available
        if client:
            ai_result, reason = needs_context_ai(message, fake_history)
            status = "✅" if ai_result == expected else "⚠️"
            print(f"   {status} AI: {'Needs context' if ai_result else 'No context'}")
            print(f"   Reason: {reason}")
        
        # Test with hybrid approach
        hybrid_result, hybrid_reason = needs_context(message, fake_history)
        status = "✅" if hybrid_result == expected else "⚠️"
        print(f"   {status} Hybrid: {'Needs context' if hybrid_result else 'No context'}")
        print(f"   Reason: {hybrid_reason}")
    
    print("\n" + "="*60)
    print("✅ Context Engine test complete!")
    print("="*60)