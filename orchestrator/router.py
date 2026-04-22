import hashlib
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from orchestrator.executors import executor, reviewer
from orchestrator.hitl import hitl_manager
from orchestrator.logging_utils import get_logger
from orchestrator.provisioner import provisioner
from orchestrator.rl_agent import rl_agent


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
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=provisioning")
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
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=routing")
    state["attempt_count"] += 1
    chosen_ide = rl_agent.choose_ide(state["context_hash"])
    state["chosen_ide"] = chosen_ide
    return state

def node_execute(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=executing attempt=%s ide=%s", state["attempt_count"], state["chosen_ide"])
    task_details = dict(state["request"])
    task_details["task_id"] = state["task_id"]
    result = executor.execute(state["chosen_ide"], state["workspace_path"], task_details)
    state["execution_result"] = result
    return state

def node_review(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=reviewing")
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
    logger = get_logger(__name__, state["task_id"])
    logger.warning("state=hitl_escalation")
    hitl_manager.escalate(state["task_id"], state["request"])
    
    # After escalation, we penalize the RL agent heavily and end.
    state["reward"] = -50.0 
    rl_agent.update_q_value(state["context_hash"], state["chosen_ide"], state["reward"])
    return state

def node_evaluate(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=evaluating")
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
    logger = get_logger(__name__, task_id)
    logger.info("orchestrator start")
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
    
    final_state: Optional[dict[str, Any]] = None
    for output in app.stream(initial_state):
        # output shape: {node_name: state}
        if isinstance(output, dict) and output:
            final_state = next(iter(output.values()))

    logger.info("orchestrator finished")
    # Keep return payload small and stable for API clients.
    if not final_state:
        return {"status": "unknown"}
    return {
        "status": "completed",
        "reward": final_state.get("reward"),
        "chosen_ide": final_state.get("chosen_ide"),
        "attempt_count": final_state.get("attempt_count"),
        "workspace_path": final_state.get("workspace_path"),
        "context_hash": final_state.get("context_hash"),
        "review_status": (final_state.get("review_result") or {}).get("status"),
    }
