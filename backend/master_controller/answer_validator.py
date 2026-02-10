"""
Answer Validator for E.V.E. Master v9.0
Validates worker responses before returning to user
Like a teacher checking student answers
"""

from groq import Groq
import json
from typing import Dict, Optional
from backend.core.config import GROQ_API_KEY

class AnswerValidator:
    """
    Validates responses from workers or master
    Ensures quality before returning to user
    """
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key) if groq_api_key else None
        self.validation_history = []  # Track validations for learning
    
    def validate_answer(self, 
                       original_task: str, 
                       response: str,
                       worker_name: str = "Unknown") -> Dict:
        """
        Check if response actually answers the task
        
        Returns: {
            "is_complete": True/False,
            "quality_score": 0-10,
            "should_retry": True/False,
            "reasoning": "explanation",
            "confidence": 0.0-1.0
        }
        """
        
        # If no AI, do basic validation
        if not self.client:
            return self._basic_validation(response)
        
        # Build validation prompt
        prompt = self._build_validation_prompt(original_task, response)
        
        try:
            result = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            validation = json.loads(result.choices[0].message.content)
            
            # Ensure all required fields
            validation.setdefault("is_complete", True)
            validation.setdefault("quality_score", 7)
            validation.setdefault("should_retry", False)
            validation.setdefault("reasoning", "Validation complete")
            validation.setdefault("confidence", 0.8)
            
            # Normalize values
            validation["quality_score"] = max(0, min(10, validation["quality_score"]))
            validation["confidence"] = max(0.0, min(1.0, validation["confidence"]))
            
            # Log validation
            self.validation_history.append({
                "worker": worker_name,
                "quality": validation["quality_score"],
                "complete": validation["is_complete"],
                "retry": validation["should_retry"]
            })
            
            # Print validation result
            self._print_validation(validation, worker_name)
            
            return validation
            
        except Exception as e:
            print(f"⚠️ Validation error: {str(e)[:100]}")
            return self._basic_validation(response)
    
    def _build_validation_prompt(self, task: str, response: str) -> str:
        """Build the validation prompt"""
        
        # Truncate long responses for validation
        response_preview = response[:1000] + ("..." if len(response) > 1000 else "")
        
        prompt = f"""You are an answer quality validator. Check if this response properly answers the task.

ORIGINAL TASK:
"{task}"

RESPONSE RECEIVED:
"{response_preview}"

EVALUATE THE RESPONSE:

1. Is it COMPLETE? (Does it fully answer the task?)
   - Yes if: Task is answered, nothing missing
   - No if: Partial answer, missing key parts

2. Quality Score (0-10):
   - 9-10: Excellent, comprehensive, correct
   - 7-8: Good, mostly correct
   - 5-6: Acceptable but has issues
   - 3-4: Poor quality, major problems
   - 0-2: Failed, wrong, or useless

3. Should RETRY?
   - Yes if: Quality < 6 OR incomplete OR errors detected
   - No if: Quality >= 6 AND complete

4. Confidence (0.0-1.0): How sure are you of this evaluation?

SPECIAL CASES:
- If response says "error", "failed", "cannot" → quality=2, retry=true
- If response is just a greeting for a greeting → quality=10, complete=true
- If response is code that looks broken → quality=3, retry=true
- If response is too short (<50 chars) for complex task → quality=4, retry=true

Respond ONLY with valid JSON:
{{
  "is_complete": true/false,
  "quality_score": 0-10,
  "should_retry": true/false,
  "reasoning": "brief explanation",
  "confidence": 0.0-1.0
}}"""
        
        return prompt
    
    def _basic_validation(self, response: str) -> Dict:
        """Fallback validation without AI"""
        
        # Simple checks
        is_error = any(word in response.lower()[:200] for word in 
                      ["error", "failed", "cannot", "unable"])
        
        is_too_short = len(response.strip()) < 10
        
        quality = 3 if is_error else (4 if is_too_short else 7)
        should_retry = is_error or is_too_short
        
        return {
            "is_complete": not should_retry,
            "quality_score": quality,
            "should_retry": should_retry,
            "reasoning": "Basic validation (no AI)",
            "confidence": 0.5
        }
    
    def _print_validation(self, validation: Dict, worker_name: str):
        """Print validation results nicely"""
        
        quality = validation["quality_score"]
        complete = validation["is_complete"]
        retry = validation["should_retry"]
        
        # Quality emoji
        if quality >= 8:
            emoji = "🌟"
        elif quality >= 6:
            emoji = "✅"
        elif quality >= 4:
            emoji = "⚠️"
        else:
            emoji = "❌"
        
        print(f"\n   {emoji} VALIDATION RESULT:")
        print(f"      Worker: {worker_name}")
        print(f"      Quality: {quality}/10")
        print(f"      Complete: {'Yes' if complete else 'No'}")
        print(f"      Action: {'✓ Accept' if not retry else '↻ Retry Recommended'}")
        print(f"      Reason: {validation['reasoning']}")
        print(f"      Confidence: {validation['confidence']:.1%}")
    
    def get_validation_stats(self) -> Dict:
        """Get statistics on validations performed"""
        
        if not self.validation_history:
            return {"total": 0}
        
        total = len(self.validation_history)
        avg_quality = sum(v["quality"] for v in self.validation_history) / total
        retry_count = sum(1 for v in self.validation_history if v["retry"])
        complete_count = sum(1 for v in self.validation_history if v["complete"])
        
        return {
            "total_validations": total,
            "avg_quality_score": round(avg_quality, 2),
            "retry_rate": round(retry_count / total * 100, 1),
            "completion_rate": round(complete_count / total * 100, 1)
        }


# Test the validator
if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Answer Validator")
    print("="*60)
    
    validator = AnswerValidator(GROQ_API_KEY)
    
    test_cases = [
        {
            "task": "Write a Python function to add two numbers",
            "response": "def add(a, b):\n    return a + b"
        },
        {
            "task": "Explain quantum computing",
            "response": "Error: Unable to process request"
        },
        {
            "task": "Hello",
            "response": "Hello! How can I help you today?"
        },
        {
            "task": "Write a detailed analysis of climate change",
            "response": "Climate change is real."  # Too short
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}")
        print(f"Task: {test['task']}")
        print(f"Response: {test['response'][:100]}")
        
        result = validator.validate_answer(test['task'], test['response'], f"TestWorker-{i}")
    
    print(f"\n{'='*60}")
    print("Validation Statistics:")
    stats = validator.get_validation_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*60)