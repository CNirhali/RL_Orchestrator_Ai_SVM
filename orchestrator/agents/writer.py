import time
import random

class WriterAgent:
    def execute(self, ide_name: str, workspace_path: str, task_details: dict) -> dict:
        print(f"[Writer Agent] Triggering {ide_name} in {workspace_path}...")
        
        # Simulate execution time and cost
        exec_time = random.uniform(1.0, 5.0)
        time.sleep(1) # just sleep 1s in real life so tests are fast
        cost = random.uniform(0.01, 0.50) # Simulated API/compute cost
        
        # Simulated outcome
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

writer_agent = WriterAgent()
