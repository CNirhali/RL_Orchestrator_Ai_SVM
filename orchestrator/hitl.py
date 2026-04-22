from orchestrator.logging_utils import get_logger


class HITLManager:
    def escalate(self, task_id: str, context: dict):
        logger = get_logger(__name__, task_id)
        logger.warning("hitl escalation required context=%s", context)
        # In a real app, this would send an API request to Slack/Teams and pause the graph
        # until a human clicks 'Approve' or 'Cancel' in the messaging app.
        return {"status": "escalated"}
        
hitl_manager = HITLManager()
