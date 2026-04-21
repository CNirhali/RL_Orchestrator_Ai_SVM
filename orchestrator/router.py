from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from orchestrator.provisioner import provisioner
from orchestrator.rl_agent import rl_agent
from orchestrator.executors import executor

# Define the state for LangGraph
class AgentState(TypedDict):
    task_id: str
    request: dict
    workspace_path: str
    chosen_ide: str
    execution_result: dict
    reward: float

def node_provision(state: AgentState) -> AgentState:
    print(f"\n--- [State: Provisioning] Task {state['task_id']} ---")
    req = state["request"]
    workspace_path = provisioner.provision_workspace(
        state["task_id"], 
        req.get("repository_url", "local"), 
        req.get("description", "")
    )
    state["workspace_path"] = workspace_path
    return state

def node_route(state: AgentState) -> AgentState:
    print(f"\n--- [State: Routing] Task {state['task_id']} ---")
    # Ask RL agent to choose IDE
    chosen_ide = rl_agent.choose_ide(task_type="general")
    state["chosen_ide"] = chosen_ide
    return state

def node_execute(state: AgentState) -> AgentState:
    print(f"\n--- [State: Executing] Task {state['task_id']} ---")
    result = executor.execute(state["chosen_ide"], state["workspace_path"], state["request"])
    state["execution_result"] = result
    return state

def node_evaluate(state: AgentState) -> AgentState:
    print(f"\n--- [State: Evaluating] Task {state['task_id']} ---")
    result = state["execution_result"]
    # Simple reward function: +1 for success, -1 for failure
    if result["status"] == "success":
        reward = 1.0
    else:
        reward = -1.0
        
    state["reward"] = reward
    # Update RL policy
    rl_agent.update_q_value(state["chosen_ide"], reward)
    return state

# Build the LangGraph
workflow = StateGraph(AgentState)

workflow.add_node("provision", node_provision)
workflow.add_node("route", node_route)
workflow.add_node("execute", node_execute)
workflow.add_node("evaluate", node_evaluate)

workflow.set_entry_point("provision")
workflow.add_edge("provision", "route")
workflow.add_edge("route", "execute")
workflow.add_edge("execute", "evaluate")
workflow.add_edge("evaluate", END)

app = workflow.compile()

def run_orchestrator(task_id: str, request_data: dict):
    print(f"Starting orchestrator pipeline for task {task_id}")
    initial_state = {
        "task_id": task_id,
        "request": request_data,
        "workspace_path": "",
        "chosen_ide": "",
        "execution_result": {},
        "reward": 0.0
    }
    
    # Run the graph
    for output in app.stream(initial_state):
        # output is a dict with node name as key and state as value
        for key, value in output.items():
            pass # Just iterate through the stream
            
    print(f"Finished orchestrator pipeline for task {task_id}")
