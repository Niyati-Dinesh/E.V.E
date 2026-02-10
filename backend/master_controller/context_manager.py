"""
Intelligent Context Manager for E.V.E. Master
Uses AI to understand conversation flow and select relevant context
"""

from groq import Groq
import json
from typing import List, Dict, Optional


class ContextManager:
    """
    Intelligent context management using AI
    - Detects if query is continuation of previous conversation
    - Selects only RELEVANT previous messages
    - Filters noise, keeps what workers need
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
    
    def analyze_context_needs(self, current_message: str, conversation_history: List[Dict]) -> Dict:
        """
        Use AI to determine:
        1. Is this a continuation of previous conversation?
        2. Which previous messages are relevant?
        3. What context should be sent to worker?
        """
        
        if not self.client or not conversation_history:
            return {
                "is_continuation": False,
                "relevant_messages": [],
                "context_summary": "",
                "reasoning": "No AI or no history"
            }
        
        # Build analysis prompt
        prompt = self._build_context_analysis_prompt(current_message, conversation_history)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Extract relevant message indices
            relevant_indices = result.get("relevant_message_indices", [])
            
            # Get the actual messages
            relevant_messages = []
            for idx in relevant_indices:
                if 0 <= idx < len(conversation_history):
                    relevant_messages.append(conversation_history[idx])
            
            context_analysis = {
                "is_continuation": result.get("is_continuation", False),
                "relevant_messages": relevant_messages,
                "context_summary": result.get("context_summary", ""),
                "reasoning": result.get("reasoning", "AI analysis")
            }
            
            print(f"\n🔍 Context Analysis:")
            print(f"   Continuation: {context_analysis['is_continuation']}")
            print(f"   Relevant messages: {len(relevant_messages)}/{len(conversation_history)}")
            print(f"   Summary: {context_analysis['context_summary'][:100]}...")
            
            return context_analysis
            
        except Exception as e:
            print(f"   ⚠️ Context analysis failed: {str(e)[:100]}")
            # Even on error, use AI for basic analysis
            return {
                "is_continuation": False,
                "relevant_messages": [],
                "context_summary": "Analysis unavailable - treating as new request",
                "reasoning": "Error in AI analysis, defaulting to safe mode"
            }
    
    def _build_context_analysis_prompt(self, current_message: str, history: List[Dict]) -> str:
        """Build prompt for AI to analyze context needs"""
        
        # Format conversation history for AI
        history_text = ""
        for i, msg in enumerate(history[-10:]):  # Last 10 messages max
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:200]  # Truncate long messages
            history_text += f"\n[{i}] {role.upper()}: {content}"
        
        prompt = f"""Analyze if the current message needs context from previous conversation. Understand the USER'S INTENT, not just keywords.

CURRENT MESSAGE: "{current_message}"

CONVERSATION HISTORY:{history_text}

YOUR TASK:
Determine if the current message is CONTINUING the previous conversation or starting something NEW.

THINK: "Does understanding this message REQUIRE knowing what was discussed before?"

CONTINUATION can be expressed in MANY ways:
- Using reference words: "it", "this", "that", "them", "above"
- Implied continuation: "now do X", "also Y", "make it better"
- Follow-up questions: asking about something previously discussed
- Requests to modify/enhance: building on previous work
- Sequential actions: "next step", "after that", "following up"
- Natural conversation flow: clearly connected to previous topic

NEW REQUEST indicators:
- Completely different topic
- Fresh question unrelated to history
- Explicit new start: "new task", "different question"
- No logical connection to previous messages

DON'T just look for specific words - UNDERSTAND the intent:
- "make it faster" = continuation (what's "it"?)
- "build something fast" = new request (just wants speed)
- "improve that" = continuation (what's "that"?)
- "improve my code" = depends on if they shared code before
- "do the same for X" = continuation (same as what?)
- "create X" = could be new or continuation - analyze context

RELEVANT MESSAGES:
- Only include messages that DIRECTLY help understand current request
- Maximum 5 messages
- Skip unrelated chatter, greetings, thanks
- Focus on what's needed to understand "it", "this", "that" references
- Include both question and answer if both are relevant

Respond with JSON:
{{
  "is_continuation": true/false,
  "relevant_message_indices": [0, 1, 2],
  "context_summary": "what context is needed and why",
  "reasoning": "how you determined this"
}}"""
        
        return prompt
    
    def build_context_for_worker(self, current_message: str, relevant_messages: List[Dict], 
                                  file_context: str = "") -> str:
        """
        Build context string to send to worker
        Includes only relevant previous messages
        """
        
        if not relevant_messages and not file_context:
            return ""
        
        context_parts = []
        
        # Add file context if exists
        if file_context:
            context_parts.append(f"📎 FILES PROVIDED:\n{file_context}")
        
        # Add relevant conversation context
        if relevant_messages:
            context_parts.append("\n💬 RELEVANT CONVERSATION CONTEXT:")
            for msg in relevant_messages:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')
                context_parts.append(f"\n{role.upper()}: {content}")
            context_parts.append(f"\n{'─'*60}")
        
        # Add current request
        context_parts.append(f"\n🎯 CURRENT REQUEST:\n{current_message}")
        
        return "\n".join(context_parts)
    
    def get_smart_context(self, current_message: str, conversation_history: List[Dict], 
                         file_context: str = "") -> tuple[str, Dict]:
        """
        Main method: Analyze context needs and build smart context for worker
        
        Returns:
            (context_string, analysis_info)
        """
        
        # Analyze what context is needed
        analysis = self.analyze_context_needs(current_message, conversation_history)
        
        # Build context string with only relevant messages
        context_string = self.build_context_for_worker(
            current_message,
            analysis["relevant_messages"],
            file_context
        )
        
        return context_string, analysis
