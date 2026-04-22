import hashlib
from typing import Dict, TypedDict, Any
from langgraph.graph import StateGraph, END
from orchestrator.provisioner import provisioner
from orchestrator.rl_agent import rl_agent
from orchestrator.executors import executor, reviewer
from orchestrator.hitl import hitl_manager

class AgentState(TypedDict):
    task_id: str
    request: dict
    workspace_path: str
    context_hash: str
    chosen_ide: str
    attempt_count: int
    execution_result: dict
    review_result: dict
    reward: float

def compute_context_hash(req: dict) -> str:
    # A simple way to hash the task context (e.g., language, complexity)
    # For stage 2, we just use a mock hash based on description length
    desc = req.get("description", "")
    task_type = "complex" if len(desc) > 50 else "simple"
    return hashlib.md5(task_type.encode()).hexdigest()[:8]

def node_provision(state: AgentState) -> AgentState:
    print(f"\n--- [State: Provisioning] Task {state['task_id']} ---")
    req = state["request"]
    workspace_path = provisioner.provision_workspace(
        state["task_id"], 
        req.get("repository_url", "local"), 
        req.get("description", "")
    )
    state["workspace_path"] = workspace_path
    state["context_hash"] = compute_context_hash(req)
    state["attempt_count"] = 0
    return state

def node_route(state: AgentState) -> AgentState:
    print(f"\n--- [State: Routing] Task {state['task_id']} ---")
    state["attempt_count"] += 1
    chosen_ide = rl_agent.choose_ide(state["context_hash"])
    state["chosen_ide"] = chosen_ide
    return state

def node_execute(state: AgentState) -> AgentState:
    print(f"\n--- [State: Executing] Task {state['task_id']} Attempt {state['attempt_count']} ---")
    result = executor.execute(state["chosen_ide"], state["workspace_path"], state["request"])
    state["execution_result"] = result
    return state

def node_review(state: AgentState) -> AgentState:
    print(f"\n--- [State: Reviewing] Task {state['task_id']} ---")
    result = reviewer.review(state["workspace_path"], state["execution_result"])
    state["review_result"] = result
    return state

def edge_after_review(state: AgentState) -> str:
    if state["review_result"]["status"] == "approved":
        return "evaluate"
    else:
        if state["attempt_count"] >= 3:
            return "hitl_escalation"
        else:
            return "route" # Retry

def node_hitl_escalation(state: AgentState) -> AgentState:
    print(f"\n--- [State: HITL Escalation] Task {state['task_id']} ---")
    hitl_manager.escalate(state["task_id"], state["request"])
    
    # After escalation, we penalize the RL agent heavily and end.
    state["reward"] = -50.0 
    rl_agent.update_q_value(state["context_hash"], state["chosen_ide"], state["reward"])
    return state

def node_evaluate(state: AgentState) -> AgentState:
    print(f"\n--- [State: Evaluating] Task {state['task_id']} ---")
    # Multi-objective reward calculation
    exec_metrics = state["execution_result"]["metrics"]
    rev_metrics = state["review_result"]["metrics"]
    
    total_cost = exec_metrics["cost"] + rev_metrics["cost"]
    
    reward = rl_agent.calculate_reward(
        success=True, # It reached evaluate, so it was approved
        cost=total_cost,
        time_taken=exec_metrics["time_taken"],
        lint_errors=exec_metrics["lint_errors"]
    )
        
    state["reward"] = reward
    rl_agent.update_q_value(state["context_hash"], state["chosen_ide"], reward)
    return state

workflow = StateGraph(AgentState)

workflow.add_node("provision", node_provision)
workflow.add_node("route", node_route)
workflow.add_node("execute", node_execute)
workflow.add_node("review", node_review)
workflow.add_node("hitl_escalation", node_hitl_escalation)
workflow.add_node("evaluate", node_evaluate)

workflow.set_entry_point("provision")
workflow.add_edge("provision", "route")
workflow.add_edge("route", "execute")
workflow.add_edge("execute", "review")
workflow.add_conditional_edges("review", edge_after_review)
workflow.add_edge("hitl_escalation", END)
workflow.add_edge("evaluate", END)

app = workflow.compile()

def run_orchestrator(task_id: str, request_data: dict):
    print(f"Starting orchestrator pipeline for task {task_id}")
    initial_state = {
        "task_id": task_id,
        "request": request_data,
        "workspace_path": "",
        "context_hash": "",
        "chosen_ide": "",
        "attempt_count": 0,
        "execution_result": {},
        "review_result": {},
        "reward": 0.0
    }
    
    for output in app.stream(initial_state):
        pass
            
    print(f"Finished orchestrator pipeline for task {task_id}")
