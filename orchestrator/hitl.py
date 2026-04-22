class HITLManager:
    def escalate(self, task_id: str, context: dict):
        print(f"\n[HITL Manager] 🚨 ESCALATION REQUIRED FOR TASK {task_id}")
        print(f"[HITL Manager] Task repeatedly failed. Context: {context}")
        print(f"[HITL Manager] Sending notification to Microsoft Teams / Slack...")
        # In a real app, this would send an API request to Slack/Teams and pause the graph
        # until a human clicks 'Approve' or 'Cancel' in the messaging app.
        return {"status": "escalated"}
        
hitl_manager = HITLManager()
