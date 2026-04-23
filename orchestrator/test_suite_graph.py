import subprocess
from typing import Any, Dict, List, Optional, TypedDict

from langgraph.graph import END, StateGraph


class SuiteState(TypedDict):
    changed_paths: List[str]
    risk_level: str
    suites: List[str]
    commands: List[str]
    run_commands: bool
    command_results: List[Dict[str, Any]]


SUITE_COMMANDS = {
    "smoke": "python -m pytest -q tests/test_logging_utils.py",
    "core": "python -m pytest -q tests/test_rl_agent.py tests/test_agent_roles.py",
    "api_e2e": "python -m pytest -q tests/test_webhook_e2e.py",
}


def _analyze_risk(state: SuiteState) -> SuiteState:
    changed = " ".join(state.get("changed_paths", []))
    high_risk_markers = ["main.py", "orchestrator/router.py", "orchestrator/executors.py"]
    medium_risk_markers = ["orchestrator/", "tests/", ".github/workflows/ci.yml"]

    if any(marker in changed for marker in high_risk_markers):
        state["risk_level"] = "high"
    elif any(marker in changed for marker in medium_risk_markers):
        state["risk_level"] = "medium"
    else:
        state["risk_level"] = "low"
    return state


def _select_suites(state: SuiteState) -> SuiteState:
    risk = state["risk_level"]
    if risk == "high":
        state["suites"] = ["smoke", "core", "api_e2e"]
    elif risk == "medium":
        state["suites"] = ["smoke", "core"]
    else:
        state["suites"] = ["smoke"]
    return state


def _build_commands(state: SuiteState) -> SuiteState:
    state["commands"] = [SUITE_COMMANDS[suite] for suite in state["suites"]]
    return state


def _execute_commands(state: SuiteState) -> SuiteState:
    if not state.get("run_commands", False):
        state["command_results"] = []
        return state

    results: List[Dict[str, Any]] = []
    for command in state["commands"]:
        proc = subprocess.run(command, shell=True, capture_output=True, text=True)
        results.append(
            {
                "command": command,
                "exit_code": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
    state["command_results"] = results
    return state


workflow = StateGraph(SuiteState)
workflow.add_node("analyze_risk", _analyze_risk)
workflow.add_node("select_suites", _select_suites)
workflow.add_node("build_commands", _build_commands)
workflow.add_node("execute_commands", _execute_commands)
workflow.set_entry_point("analyze_risk")
workflow.add_edge("analyze_risk", "select_suites")
workflow.add_edge("select_suites", "build_commands")
workflow.add_edge("build_commands", "execute_commands")
workflow.add_edge("execute_commands", END)
suite_graph = workflow.compile()


def create_best_suite(
    changed_paths: Optional[List[str]] = None, run_commands: bool = False
) -> Dict[str, Any]:
    initial_state: SuiteState = {
        "changed_paths": changed_paths or [],
        "risk_level": "low",
        "suites": [],
        "commands": [],
        "run_commands": run_commands,
        "command_results": [],
    }

    final_state: Dict[str, Any] = {}
    for output in suite_graph.stream(initial_state):
        if output:
            final_state = next(iter(output.values()))
    return final_state

