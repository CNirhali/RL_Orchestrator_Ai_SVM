import time
import random

class ReviewerAgent:
    def review(self, workspace_path: str, execution_result: dict) -> dict:
        print(f"[Reviewer Agent] Analyzing changes in {workspace_path}...")
        time.sleep(1)
        
        cost = random.uniform(0.01, 0.10)
        
        writer_success = execution_result.get("status") == "success"
        
        if writer_success:
            approved = random.random() < 0.95
        else:
            approved = random.random() < 0.10 # 10% chance a bad PR slips through
            
        metrics = {"cost": cost, "approved": approved}
        
        if approved:
            print(f"[Reviewer Agent] LGTM! Code is approved.")
            return {"status": "approved", "metrics": metrics}
        else:
            print(f"[Reviewer Agent] Changes rejected. Sending back to Writer.")
            return {"status": "rejected", "metrics": metrics}

reviewer_agent = ReviewerAgent()
