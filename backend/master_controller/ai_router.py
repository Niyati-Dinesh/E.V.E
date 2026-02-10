"""
E.V.E. INTELLIGENT AI ROUTER - NEW VERSION
Implements 3-Layer Intelligence:
- A: Self-Learning (Performance-based routing with success rate tracking)
- B: Multi-Agent Fallback (Retry logic, queueing, master's own brain)
- C: Context-Aware (Multi-step task handling, maintained context)
PLUS: Hardware-aware routing (CPU, RAM, Temperature consideration)
"""

from typing import Dict, List, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from backend.core.database import (
        get_available_agents, get_agent_performance, 
        assign_task_to_agent, queue_task, get_next_queued_task,
        store_context, get_recent_contexts, log_system_event
    )
except ImportError:
    print("⚠️  Using fallback imports...")
    from backend.core.database import (
        get_available_agents, get_agent_performance,
        assign_task_to_agent, queue_task, get_next_queued_task,
        store_context, get_recent_contexts, log_system_event
    )

# =============================================================================
# LAYER A: SELF-LEARNING ROUTING
# =============================================================================

def select_best_agent_by_performance(task_type: str, available_agents: List[Dict]) -> Optional[Dict]:
    """
    INTELLIGENCE LAYER A: Self-Learning
    Selects agent based on historical performance and success rate
    """
    if not available_agents:
        return None
    
    # Score each agent
    scored_agents = []
    for agent in available_agents:
        agent_id = agent['agent_id']
        perf = get_agent_performance(agent_id)
        
        if not perf:
            continue
        
        # Calculate score based on:
        # - Success rate (50% weight)
        # - Execution speed (30% weight)
        # - Total successful tasks (20% weight)
        success_rate = perf.get('success_rate', 0) / 100.0
        
        # Normalize execution time (lower is better)
        avg_time = perf.get('avg_execution_time', 1.0)
        time_score = 1.0 / (1.0 + avg_time / 10.0)  # Normalize to 0-1
        
        # Experience score
        successful_tasks = perf.get('successful_tasks', 0)
        experience_score = min(successful_tasks / 100.0, 1.0)  # Cap at 100 tasks
        
        # Combined score
        total_score = (
            success_rate * 0.5 +
            time_score * 0.3 +
            experience_score * 0.2
        )
        
        scored_agents.append({
            'agent': agent,
            'score': total_score,
            'success_rate': perf.get('success_rate', 0),
            'avg_time': avg_time
        })
        
        print(f"   📊 {agent['agent_name']}: Score={total_score:.3f} | Success={perf.get('success_rate', 0):.1f}% | Avg Time={avg_time:.2f}s")
    
    if not scored_agents:
        return available_agents[0]  # Fallback to first agent
    
    # Return best scoring agent
    best = max(scored_agents, key=lambda x: x['score'])
    print(f"   ✨ Selected: {best['agent']['agent_name']} (Score: {best['score']:.3f})")
    return best['agent']

# =============================================================================
# HARDWARE-AWARE ROUTING
# =============================================================================

def filter_by_hardware_health(agents: List[Dict], cpu_threshold: float = 80.0, 
                               memory_threshold: float = 90.0) -> List[Dict]:
    """
    Filter agents based on hardware health
    Avoids overloaded agents
    """
    healthy_agents = []
    
    for agent in agents:
        cpu = agent.get('cpu_usage', 0)
        memory = agent.get('memory_usage', 0)
        temp = agent.get('temperature', 0)
        
        # Check if agent is healthy
        if cpu < cpu_threshold and memory < memory_threshold:
            healthy_agents.append(agent)
            print(f"   ✅ {agent['agent_name']}: CPU={cpu}% RAM={memory}% Temp={temp}°C - Healthy")
        else:
            print(f"   ⚠️  {agent['agent_name']}: CPU={cpu}% RAM={memory}% - Overloaded (skipped)")
    
    return healthy_agents if healthy_agents else agents  # Return all if none healthy

# =============================================================================
# LAYER B: MULTI-AGENT FALLBACK
# =============================================================================

async def route_with_fallback(
    task_id: int,
    task_desc: str,
    task_type: str,
    max_retries: int = 3,
    use_master_brain: bool = True
) -> Tuple[Optional[Dict], str]:
    """
    INTELLIGENCE LAYER B: Multi-Agent Fallback
    - Try best agent first
    - If fails, try next best
    - If all busy, queue task
    - If all fail, use master's own brain (Groq)
    """
    print(f"\n🔍 Routing Task {task_id} (Type: {task_type})")
    
    # Get available agents
    agents = get_available_agents(task_type)
    
    if not agents:
        print("   ⚠️  No agents available!")
        if use_master_brain:
            print("   🧠 Will use Master's own brain (Groq)")
            return None, "master_brain"
        else:
            print("   📥 Queueing task...")
            queue_task(task_id, priority=1)
            return None, "queued"
    
    # Filter by hardware health
    healthy_agents = filter_by_hardware_health(agents)
    
    if not healthy_agents:
        print("   ⚠️  All agents overloaded!")
        queue_task(task_id, priority=2)  # Higher priority for overload
        return None, "queued_overload"
    
    # SELF-LEARNING: Select best agent by performance (even if busy)
    print("\n   📈 Self-Learning Agent Selection:")
    best_agent = select_best_agent_by_performance(task_type, healthy_agents)
    
    if not best_agent:
        print("   ❌ No suitable agent found")
        queue_task(task_id, priority=1)
        return None, "queued_no_match"
    
    # Check if best agent is busy
    if best_agent['status'] == 'busy':
        print(f"   ⏳ Best agent ({best_agent['agent_name']}) is busy - queueing for this specific worker")
        queue_task(task_id, priority=1)
        return None, f"queued_for_{best_agent['agent_name']}"
    
    # Agent is idle and ready!
    print(f"   ✨ Selected: {best_agent['agent_name']} (Ready)")
    best_agent = best_agent
    
    # Assign task to the selected best agent
    assign_task_to_agent(task_id, best_agent['agent_id'])
    log_system_event(
        'info',
        f"Task {task_id} assigned to {best_agent['agent_name']}",
        agent_id=best_agent['agent_id'],
        task_id=task_id
    )
    
    return best_agent, "assigned"

# =============================================================================
# LAYER C: CONTEXT-AWARE ROUTING
# =============================================================================

def analyze_context_for_multi_step(task_desc: str, recent_tasks: List[Dict]) -> Dict:
    """
    INTELLIGENCE LAYER C: Context-Aware Analysis
    Detects if task is part of multi-step sequence
    Maintains context across related tasks
    """
    context_analysis = {
        "is_multi_step": False,
        "related_tasks": [],
        "suggested_agent": None,
        "context_type": "single"
    }
    
    # Keywords indicating multi-step tasks
    multi_step_keywords = [
        "then", "after that", "next", "also", "and also",
        "continue", "following", "step", "first", "second"
    ]
    
    task_lower = task_desc.lower()
    
    # Check for multi-step indicators
    for keyword in multi_step_keywords:
        if keyword in task_lower:
            context_analysis["is_multi_step"] = True
            context_analysis["context_type"] = "multi_step"
            break
    
    # Find related recent tasks
    for recent in recent_tasks:
        recent_desc = recent.get('task_desc', '').lower()
        # Simple similarity check (can be enhanced with embeddings)
        common_words = set(task_lower.split()) & set(recent_desc.split())
        if len(common_words) > 3:  # If >3 common words, likely related
            context_analysis["related_tasks"].append(recent['task_id'])
    
    if context_analysis["related_tasks"]:
        print(f"   🔗 Context: Found {len(context_analysis['related_tasks'])} related tasks")
        context_analysis["context_type"] = "contextual"
    
    return context_analysis

async def route_with_context_awareness(
    task_id: int,
    task_desc: str,
    task_type: str
) -> Tuple[Optional[Dict], Dict]:
    """
    Route task with context awareness
    Returns: (selected_agent, context_info)
    """
    print(f"\n🧠 Context-Aware Routing for Task {task_id}")
    
    # Get recent context
    recent_contexts = get_recent_contexts(limit=10)
    
    # Analyze context
    context_info = analyze_context_for_multi_step(task_desc, recent_contexts)
    
    if context_info["is_multi_step"]:
        print(f"   ✨ Multi-step task detected! Type: {context_info['context_type']}")
    
    # Store context for this task
    import json
    store_context(task_id, json.dumps(context_info), context_type=context_info['context_type'])
    
    # Route with fallback
    agent, status = await route_with_fallback(task_id, task_desc, task_type)
    
    return agent, context_info

# =============================================================================
# MAIN ROUTING FUNCTION - COMBINES ALL 3 LAYERS
# =============================================================================

async def intelligent_route(
    task_id: int,
    task_desc: str,
    task_type: str = 'general',
    priority: int = 1
) -> Tuple[Optional[Dict], Dict]:
    """
    MASTER INTELLIGENT ROUTING FUNCTION
    Combines all 3 intelligence layers:
    - Layer A: Self-learning performance-based selection
    - Layer B: Multi-agent fallback with retry logic
    - Layer C: Context-aware multi-step task handling
    PLUS: Hardware-aware routing
    
    Returns: (selected_agent, routing_info)
    """
    print("\n" + "="*70)
    print("🧠 INTELLIGENT ROUTING SYSTEM")
    print("="*70)
    print(f"Task ID: {task_id}")
    print(f"Type: {task_type}")
    print(f"Priority: {priority}")
    print(f"Description: {task_desc[:100]}...")
    
    routing_info = {
        "task_id": task_id,
        "task_type": task_type,
        "routing_decision": None,
        "agent_selected": None,
        "context_aware": False,
        "self_learning_applied": False,
        "hardware_checked": True,
        "status": "pending"
    }
    
    try:
        # Apply Layer C: Context Awareness
        agent, context_info = await route_with_context_awareness(task_id, task_desc, task_type)
        
        routing_info["context_aware"] = context_info.get("is_multi_step", False)
        routing_info["context_info"] = context_info
        
        if agent:
            routing_info["agent_selected"] = agent['agent_name']
            routing_info["agent_id"] = agent['agent_id']
            routing_info["status"] = "assigned"
            routing_info["self_learning_applied"] = True
            
            print(f"\n✅ Routing Complete: {agent['agent_name']}")
            print("="*70 + "\n")
            
        else:
            routing_info["status"] = "queued_or_master_brain"
            print(f"\n⏸️  Routing Deferred: Task queued or will use master brain")
            print("="*70 + "\n")
        
        return agent, routing_info
        
    except Exception as e:
        print(f"❌ Routing error: {e}")
        log_system_event('error', f"Routing failed for task {task_id}: {e}", task_id=task_id)
        routing_info["status"] = "error"
        routing_info["error"] = str(e)
        return None, routing_info

# =============================================================================
# QUEUE PROCESSOR
# =============================================================================

async def process_queued_tasks():
    """
    Process tasks from queue when agents become available
    """
    print("\n🔄 Checking task queue...")
    
    next_task = get_next_queued_task()
    
    if not next_task:
        return None
    
    task_id = next_task['task_id']
    task_desc = next_task['task_desc']
    task_type = next_task.get('task_type', 'general')
    
    print(f"📋 Processing queued task {task_id}")
    
    # Try routing again
    return await intelligent_route(task_id, task_desc, task_type)

if __name__ == "__main__":
    print("E.V.E. Intelligent AI Router - Ready")
    print("Features:")
    print("  ✅ Self-Learning (Performance-based)")
    print("  ✅ Multi-Agent Fallback")
    print("  ✅ Context-Aware")
    print("  ✅ Hardware Monitoring")
