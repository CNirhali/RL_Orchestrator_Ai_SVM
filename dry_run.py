import hashlib
import random
import time

class RLAgent:
    def __init__(self):
        self.epsilon = 0.2
        self.ides = ["cursor", "windsurf", "claude", "vscode_cline"]
        self.q_table = {}

    def _ensure_context(self, context_hash: str):
        if context_hash not in self.q_table:
            self.q_table[context_hash] = {ide: 0.0 for ide in self.ides}

    def choose_ide(self, context_hash: str) -> str:
        self._ensure_context(context_hash)
        scores = self.q_table[context_hash]
        if random.random() < self.epsilon:
            chosen = random.choice(self.ides)
            print(f"[RL Brain] EXPLORING: chose {chosen} for context '{context_hash}'")
        else:
            chosen = max(scores, key=scores.get)
            print(f"[RL Brain] EXPLOITING: chose {chosen} (Q={scores[chosen]:.2f}) for context '{context_hash}'")
        return chosen

    def calculate_reward(self, success, cost, time_taken, lint_errors):
        base = 10.0 if success else -10.0
        return base - (cost * 0.1) - (lint_errors * 0.5) - (time_taken * 0.05)

    def update_q_value(self, context_hash, ide, reward):
        self._ensure_context(context_hash)
        old_q = self.q_table[context_hash][ide]
        new_q = old_q + 0.1 * (reward - old_q)
        self.q_table[context_hash][ide] = new_q
        print(f"[RL Brain] Updated Q-value for {ide} in context '{context_hash}': {old_q:.2f} -> {new_q:.2f}")

class IDEExecutor:
    def execute(self, ide_name, attempt):
        print(f"[Writer Agent] Triggering {ide_name}... (Attempt {attempt})")
        time.sleep(1)
        base_chance = 0.8 if ide_name in ["cursor", "claude"] else 0.4
        success = random.random() < base_chance
        metrics = {"time_taken": random.uniform(1, 5), "cost": random.uniform(0.1, 0.5), "lint_errors": 0 if success else random.randint(1, 5)}
        if success:
            print(f"[Writer Agent] {ide_name} completed the code changes.")
        else:
            print(f"[Writer Agent] {ide_name} introduced errors.")
        return {"status": "success" if success else "failed", "metrics": metrics}

class ReviewerExecutor:
    def review(self, writer_status):
        print(f"[Reviewer Agent] Analyzing changes...")
        time.sleep(1)
        cost = random.uniform(0.01, 0.10)
        approved = (random.random() < 0.95) if writer_status == "success" else (random.random() < 0.10)
        
        if approved:
            print(f"[Reviewer Agent] LGTM! Code is approved.")
        else:
            print(f"[Reviewer Agent] Changes rejected. Sending back to Writer.")
        return {"status": "approved" if approved else "rejected", "metrics": {"cost": cost}}

class HITLManager:
    def escalate(self, task_id):
        print(f"\n[HITL Manager] 🚨 ESCALATION REQUIRED FOR TASK {task_id}")
        print(f"[HITL Manager] Sending notification to Microsoft Teams / Slack...")
        time.sleep(1)
        return {"status": "escalated"}

def run_dry_run():
    print("Starting Stage 2 Advanced Pipeline Dry Run...\n")
    
    rl_agent = RLAgent()
    executor = IDEExecutor()
    reviewer = ReviewerExecutor()
    hitl = HITLManager()
    
    tasks = [
        {"id": "task-001", "desc": "Fix typo in frontend header."},
        {"id": "task-002", "desc": "Refactor backend microservice to use Redis pub/sub queueing. Very complex distributed system problem."},
        {"id": "task-003", "desc": "Fix typo in footer."}
    ]
    
    for task in tasks:
        task_id = task["id"]
        context_hash = hashlib.md5((task["desc"]).encode()).hexdigest()[:8]
        print(f"\n==========================================")
        print(f"       STARTING TASK {task_id}")
        print(f"       Context Hash: {context_hash}")
        print(f"==========================================")
        
        attempt = 1
        total_cost = 0.0
        total_time = 0.0
        total_lint = 0
        final_status = "failed"
        
        chosen_ide = rl_agent.choose_ide(context_hash)
        
        while attempt <= 3:
            exec_res = executor.execute(chosen_ide, attempt)
            total_cost += exec_res["metrics"]["cost"]
            total_time += exec_res["metrics"]["time_taken"]
            total_lint += exec_res["metrics"]["lint_errors"]
            
            rev_res = reviewer.review(exec_res["status"])
            total_cost += rev_res["metrics"]["cost"]
            
            if rev_res["status"] == "approved":
                final_status = "approved"
                break
                
            attempt += 1
            
        if final_status == "approved":
            reward = rl_agent.calculate_reward(True, total_cost, total_time, total_lint)
            rl_agent.update_q_value(context_hash, chosen_ide, reward)
        else:
            hitl.escalate(task_id)
            # Massive penalty for requiring human escalation
            rl_agent.update_q_value(context_hash, chosen_ide, -50.0)
            
if __name__ == "__main__":
    run_dry_run()
