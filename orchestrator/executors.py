import time
import random

class IDEExecutor:
    def execute(self, ide_name: str, workspace_path: str, task_details: dict) -> dict:
        print(f"[Writer Agent] Triggering {ide_name} in {workspace_path}...")
        
        # Simulate execution time and cost
        exec_time = random.uniform(1.0, 5.0)
        time.sleep(1) # just sleep 1s in real life so tests are fast
        cost = random.uniform(0.01, 0.50) # Simulated API/compute cost
        
        # Simulated outcome: different IDEs might have different simulated baselines
        base_success_chance = 0.7 if ide_name in ["cursor", "claude"] else 0.5
        success = random.random() < base_success_chance
        
        metrics = {
            "time_taken": exec_time,
            "cost": cost,
            "lint_errors": 0 if success else random.randint(1, 10),
            "tests_passed": success
        }
        
        if success:
            print(f"[Writer Agent] {ide_name} completed the code changes.")
            return {"status": "success", "metrics": metrics}
        else:
            print(f"[Writer Agent] {ide_name} failed or introduced errors.")
            return {"status": "failed", "metrics": metrics}

class ReviewerExecutor:
    def review(self, workspace_path: str, execution_result: dict) -> dict:
        print(f"[Reviewer Agent] Analyzing changes in {workspace_path}...")
        time.sleep(1)
        
        cost = random.uniform(0.01, 0.10)
        
        # The reviewer catches issues. If the writer failed, the reviewer will catch it 90% of the time.
        # If the writer succeeded, the reviewer passes it 95% of the time.
        writer_success = execution_result["status"] == "success"
        
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

executor = IDEExecutor()
reviewer = ReviewerExecutor()
