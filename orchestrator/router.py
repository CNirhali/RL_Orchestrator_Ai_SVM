import hashlib
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from orchestrator.agents import writer_agent, reviewer_agent, planner_agent
from orchestrator.agents.packager import packager_agent
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
    plan_result: dict
    execution_result: dict
    review_result: dict
    package_result: dict
    reward: float
    is_failed: bool

def compute_context_hash(req: dict) -> str:
    desc = req.get("user_prompt", "")
    task_type = "complex" if len(desc) > 50 else "simple"
    return hashlib.md5(task_type.encode()).hexdigest()[:8]

def node_provision(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=provisioning")
    req = state["request"]
    workspace_path = provisioner.provision_workspace(
        state["task_id"], 
        req.get("user_prompt", "")
    )
    state["workspace_path"] = workspace_path
    state["context_hash"] = compute_context_hash(req)
    state["attempt_count"] = 0
    state["is_failed"] = False
    return state

def node_route(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=routing")
    state["attempt_count"] += 1
    chosen_ide = rl_agent.choose_ide(state["context_hash"])
    state["chosen_ide"] = chosen_ide
    return state

def node_plan(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=planning")
    result = planner_agent.plan(state["request"])
    state["plan_result"] = result
    return state

def node_execute(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info(
        "state=executing attempt=%s ide_agent=%s",
        state["attempt_count"],
        state["chosen_ide"],
    )
    task_details = dict(state["request"])
    task_details["task_id"] = state["task_id"]
    task_details["plan"] = state.get("plan_result", {})
    result = writer_agent.execute(state["chosen_ide"], state["workspace_path"], task_details)
    state["execution_result"] = result
    return state

def node_review(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=reviewing")
    result = reviewer_agent.review(state["workspace_path"], state["execution_result"])
    state["review_result"] = result
    return state

def edge_after_review(state: AgentState) -> str:
    if state["review_result"]["status"] == "approved":
        return "evaluate"
    else:
        if state["attempt_count"] >= 3:
            # We fail the pipeline for the user if it reaches 3 attempts
            state["is_failed"] = True
            return "evaluate"
        else:
            return "route" # Retry

def node_evaluate(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=evaluating")
    
    plan_metrics = state.get("plan_result", {}).get("metrics", {"cost": 0.0})
    exec_metrics = state["execution_result"].get("metrics", {"cost": 0.0, "time_taken": 0.0, "lint_errors": 0})
    rev_metrics = state["review_result"].get("metrics", {"cost": 0.0})
    
    total_cost = plan_metrics["cost"] + exec_metrics["cost"] + rev_metrics["cost"]
    
    if state.get("is_failed"):
        reward = -50.0
    else:
        reward = rl_agent.calculate_reward(
            success=True,
            cost=total_cost,
            time_taken=exec_metrics["time_taken"],
            lint_errors=exec_metrics["lint_errors"]
        )
        
    state["reward"] = reward
    rl_agent.update_q_value(state["context_hash"], state["chosen_ide"], reward)
    return state

def edge_after_evaluate(state: AgentState) -> str:
    if state.get("is_failed"):
        return END
    return "package"

def node_package(state: AgentState) -> AgentState:
    logger = get_logger(__name__, state["task_id"])
    logger.info("state=packaging")
    result = packager_agent.package(state["workspace_path"])
    state["package_result"] = result
    return state

workflow = StateGraph(AgentState)

workflow.add_node("provision", node_provision)
workflow.add_node("route", node_route)
workflow.add_node("plan", node_plan)
workflow.add_node("execute", node_execute)
workflow.add_node("review", node_review)
workflow.add_node("evaluate", node_evaluate)
workflow.add_node("package", node_package)

workflow.set_entry_point("provision")
workflow.add_edge("provision", "route")
workflow.add_edge("route", "plan")
workflow.add_edge("plan", "execute")
workflow.add_edge("execute", "review")
workflow.add_conditional_edges("review", edge_after_review)
workflow.add_conditional_edges("evaluate", edge_after_evaluate)
workflow.add_edge("package", END)

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
        "plan_result": {},
        "execution_result": {},
        "review_result": {},
        "package_result": {},
        "reward": 0.0,
        "is_failed": False
    }
    
    final_state: Optional[dict[str, Any]] = None
    for output in app.stream(initial_state):
        if isinstance(output, dict) and output:
            final_state = next(iter(output.values()))

    logger.info("orchestrator finished")
    if not final_state:
        return {"status": "unknown"}
    
    if final_state.get("is_failed"):
        return {"status": "failed", "message": "Failed to generate app. Please try again."}
        
    return {
        "status": "completed",
        "zip_path": final_state.get("package_result", {}).get("zip_path"),
        "reward": final_state.get("reward"),
        "chosen_ide": final_state.get("chosen_ide"),
        "attempt_count": final_state.get("attempt_count")
    }
