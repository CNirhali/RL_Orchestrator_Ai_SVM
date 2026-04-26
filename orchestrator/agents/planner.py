import time
import random

class PlannerAgent:
    def plan(self, task_details: dict) -> dict:
        chat_history = task_details.get("chat_history", [])
        prompt = task_details.get("user_prompt", "")
        
        print(f"[Planner Agent] Analyzing chat history ({len(chat_history)} messages)...")
        time.sleep(1)
        
        cost = random.uniform(0.01, 0.05)
        
        # Simulate needing clarification for the first message if it's short
        if len(chat_history) <= 1 and len(prompt) < 100:
            print(f"[Planner Agent] Prompt is vague. Requesting clarification from user.")
            return {
                "status": "clarification_needed",
                "question": "Great! Will your app need user accounts or a database?",
                "metrics": {"cost": cost}
            }
            
        print(f"[Planner Agent] Generated a comprehensive technical blueprint.")
        return {
            "status": "blueprint_ready",
            "complexity": "complex",
            "blueprint": ["Frontend UI", "Backend API", "Database Schema"],
            "metrics": {"cost": cost}
        }

planner_agent = PlannerAgent()
