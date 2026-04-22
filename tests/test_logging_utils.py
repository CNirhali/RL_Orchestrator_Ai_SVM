from orchestrator.logging_utils import get_logger


def test_call_time_task_id_overrides_adapter_default():
    logger = get_logger("test.logger")
    _, kwargs = logger.process("message", {"extra": {"task_id": "actual_id"}})

    assert kwargs["extra"]["task_id"] == "actual_id"


def test_adapter_task_id_is_used_when_call_time_extra_missing():
    logger = get_logger("test.logger", "adapter_id")
    _, kwargs = logger.process("message", {})

    assert kwargs["extra"]["task_id"] == "adapter_id"

