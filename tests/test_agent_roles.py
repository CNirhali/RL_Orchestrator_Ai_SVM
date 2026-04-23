from orchestrator.executors import IDEExecutor
from orchestrator.hitl import hitl_manager


def test_ide_executor_routes_to_named_agent():
    executor = IDEExecutor(sleep_s=0)
    result = executor.execute(
        "cursor",
        "/tmp/workspace",
        {"task_id": "task-1", "description": "Test task"},
    )

    assert "metrics" in result
    assert result["metrics"]["agent_name"] == "cursor"


def test_human_in_loop_agent_payload():
    escalation = hitl_manager.escalate("task-2", {"description": "Needs review"})
    assert escalation["status"] == "escalated"
    assert escalation["owner"] == "human_in_loop"
    assert escalation["next_action"] == "await_human_decision"

