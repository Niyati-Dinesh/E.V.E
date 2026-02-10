"""
Task Planner for E.V.E. Master v9.0
Breaks complex tasks into sequential steps
Like a smart teacher planning a lesson
"""

from groq import Groq
import json
from typing import List, Dict, Optional
from backend.core.config import GROQ_API_KEY

class TaskPlanner:
    """
    Intelligent task planning system
    Breaks complex tasks into simple steps
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
    
    def plan_task(self, message: str, files: List[Dict] = None) -> Dict:
        """
        Break a complex task into execution steps
        
        Example:
        Input: "Write a Python function to sort a list and document it"
        Output: {
            "steps": ["coding", "documentation"],
            "is_multi_step": True,
            "reasoning": "Task requires both code creation and documentation"
        }
        
        Returns: Planning result with steps array
        """
        
        # If no AI, assume single step
        if not self.client:
            return {
                "steps": ["general"],
                "is_multi_step": False,
                "reasoning": "No AI planner available - single step execution"
            }
        
        # Build planning prompt
        prompt = self._build_planning_prompt(message, files)
        
        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate response
            if "steps" not in result or not isinstance(result["steps"], list):
                return self._default_plan()
            
            # Clean up steps
            valid_steps = []
            for step in result["steps"]:
                step_clean = step.lower().strip()
                if step_clean in ["coding", "documentation", "analysis", "general"]:
                    valid_steps.append(step_clean)
            
            if not valid_steps:
                valid_steps = ["general"]
            
            plan = {
                "steps": valid_steps,
                "is_multi_step": len(valid_steps) > 1,
                "reasoning": result.get("reasoning", "AI task planning")
            }
            
            print(f"\n📋 TASK PLAN:")
            print(f"   Steps: {' → '.join(plan['steps'])}")
            print(f"   Multi-step: {plan['is_multi_step']}")
            print(f"   Reason: {plan['reasoning']}")
            
            return plan
            
        except Exception as e:
            print(f"⚠️ Planning error: {str(e)[:100]}")
            return self._default_plan()
    
    def _build_planning_prompt(self, message: str, files: List[Dict]) -> str:
        """Build the planning prompt for AI - ENHANCED for varied question formats"""
        
        file_context = ""
        if files:
            file_types = [f.get('filename', '').split('.')[-1] for f in files]
            file_context = f"\n\nFiles attached: {len(files)} files ({', '.join(file_types)})"
        
        prompt = f"""You are a smart task planner. Understand what the user REALLY wants to accomplish and break it into logical steps.

USER REQUEST: "{message}"{file_context}

STEP CATEGORIES:
- "coding" → Creating/fixing/working with any kind of programs or code
- "documentation" → Creating/writing any kind of explanatory content, reports, guides, or documents
- "analysis" → Researching/analyzing/comparing/evaluating data or information
- "general" → Other tasks

PLANNING RULES:
1. DEFAULT to SINGLE STEP - most requests need just one type of work
2. Use MULTIPLE STEPS only when the user explicitly wants multiple different types of work done sequentially
3. Maximum 3 steps

IMPORTANT DISTINCTIONS:
- "write code and a report" → ["coding", "documentation"] (code + written report)
- "write code and analyze" → ["coding", "analysis"] (code + evaluation)
- "analyze data and write report" → ["analysis", "documentation"] (research + write)
- "write code to analyze" → ["coding"] (SINGLE step - code that does analysis)
- "create analysis code" → ["coding"] (SINGLE step - just code)
- "explain analysis results" → ["documentation"] (SINGLE step - just explanation)

THINK:
- Does the user want ONE thing done? → Single step
- Does the user want multiple DIFFERENT things done in sequence? → Multiple steps
- Are they using connecting words like "and then", "after that", "also", "plus"? → Likely multiple steps

Examples:
- "write code to measure X and provide a report" → ["coding", "documentation"]
- "build a program and document it" → ["coding", "documentation"]
- "write analysis code" → ["coding"] 
- "create a data analyzer" → ["coding"]
- "research X and write about it" → ["analysis", "documentation"]

Understand their GOAL, not their exact words.

Respond with JSON:
{{"steps": ["type1", "type2"], "reasoning": "what they want to accomplish"}}"""
        
        return prompt
    
    def _default_plan(self) -> Dict:
        """Fallback plan when AI fails"""
        return {
            "steps": ["general"],
            "is_multi_step": False,
            "reasoning": "Default single-step plan"
        }
    
    def should_continue_to_next_step(self, 
                                     current_step: int, 
                                     total_steps: int,
                                     current_result: str) -> bool:
        """
        Decide if we should continue to next step or stop
        
        Simple logic:
        - If current step succeeded and there are more steps → continue
        - If current step failed → stop
        """
        
        # Check if result looks like an error
        error_indicators = [
            "error", "failed", "cannot", "unable to",
            "sorry", "apologize", "something went wrong"
        ]
        
        result_lower = current_result.lower()[:200]  # Check first 200 chars
        
        for indicator in error_indicators:
            if indicator in result_lower:
                print(f"   ⚠️ Step {current_step + 1} appears to have failed")
                print(f"   🛑 Stopping multi-step execution")
                return False
        
        # If we're not at the last step, continue
        if current_step < total_steps - 1:
            print(f"   ✅ Step {current_step + 1}/{total_steps} complete")
            print(f"   ➡️ Proceeding to step {current_step + 2}")
            return True
        
        return False


# Test the planner
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Task Planner")
    print("="*60)
    
    planner = TaskPlanner(GROQ_API_KEY)
    
    test_tasks = [
        "Write a Python function to calculate fibonacci",
        "Create a sorting algorithm and document how it works",
        "Debug this code and explain the fix",
        "Hello, how are you?",
        "Analyze sales data and write a summary report",
        "Generate an image of a sunset"
    ]
    
    for task in test_tasks:
        print(f"\n📝 Task: {task}")
        plan = planner.plan_task(task)
        print(f"   Result: {plan}")
    
    print("\n" + "="*60)