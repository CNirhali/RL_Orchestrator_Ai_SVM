import time
import random

class PlannerAgent:
    def plan(self, task_details: dict) -> dict:
        print(f"[Planner Agent] Analyzing task '{task_details.get('description', 'Unknown Task')}'...")
        time.sleep(1)
        
        # Simulate cost of planning
        cost = random.uniform(0.01, 0.05)
        
        # Determine plan complexity
        desc_len = len(task_details.get('description', ''))
        complexity = "complex" if desc_len > 50 else "simple"
        
        print(f"[Planner Agent] Generated a {complexity} technical specification.")
        
        return {
            "status": "planned",
            "complexity": complexity,
            "metrics": {
                "cost": cost
            }
        }

planner_agent = PlannerAgent()
