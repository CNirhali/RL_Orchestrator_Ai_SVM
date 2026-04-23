from orchestrator.logging_utils import get_logger


class HumanInLoopAgent:
    def escalate(self, task_id: str, context: dict):
        logger = get_logger(__name__, task_id)
        logger.warning("human_in_loop escalation required context=%s", context)
        # In a real app, this agent would send an API request to Slack/Teams and wait
        # for human resolution before resuming orchestration.
        return {
            "status": "escalated",
            "owner": "human_in_loop",
            "next_action": "await_human_decision",
        }


class HITLManager(HumanInLoopAgent):
    """
    Backwards-compatible alias for older imports.
    """


hitl_manager = HumanInLoopAgent()
