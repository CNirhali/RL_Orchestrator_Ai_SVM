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

class PlannerAgent:
    def plan(self, chat_history: list):
        print(f"[Planner Agent] Analyzing chat history ({len(chat_history)} messages)...")
        time.sleep(1)
        
        if len(chat_history) <= 1:
            print(f"[Planner Agent] ⚠️ Prompt is too vague. Requesting clarification.")
            return {"status": "clarification_needed", "question": "Will your app need user accounts or a database?", "cost": 0.02}
            
        print(f"[Planner Agent] ✅ Gathered enough info. Generated a technical blueprint.")
        return {"status": "blueprint_ready", "cost": 0.04}

class ArchitectAgent:
    def design(self, plan_status):
        print(f"[Architect Agent] Designing system architecture and selecting tech stack...")
        time.sleep(1)
        cost = random.uniform(0.02, 0.05)
        print(f"[Architect Agent] Architecture blueprint generated. (Cost: ${cost:.3f})")
        return {"status": "architecture_ready", "metrics": {"cost": cost}}
        time.sleep(1)
        
        if len(chat_history) <= 1:
            print(f"[Planner Agent] ⚠️ Prompt is too vague. Requesting clarification.")
            return {"status": "clarification_needed", "question": "Will your app need user accounts or a database?", "cost": 0.02}
            
        print(f"[Planner Agent] ✅ Gathered enough info. Generated a technical blueprint.")
        return {"status": "blueprint_ready", "cost": 0.04}

class WriterAgent:
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

class ReviewerAgent:
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

class SecurityAgent:
    def scan(self):
        print(f"[Security Agent] Scanning code for vulnerabilities (SAST/DAST)...")
        time.sleep(1)
        passed = random.random() < 0.90
        if passed:
            print(f"[Security Agent] No critical vulnerabilities found. 🛡️")
        else:
            print(f"[Security Agent] ⚠️ High severity vulnerability detected! Needs patching.")
        return {"status": "safe" if passed else "vulnerable"}

class QAAgent:
    def test(self):
        print(f"[QA Agent] Running test suite and calculating coverage...")
        time.sleep(1)
        coverage = random.uniform(70.0, 95.0)
        passed = coverage >= 80.0
        if passed:
            print(f"[QA Agent] All tests passed! Coverage: {coverage:.1f}%")
        else:
            print(f"[QA Agent] Tests failed! Coverage too low: {coverage:.1f}%")
        return {"status": "passed" if passed else "failed"}

class DevOpsAgent:
    def deploy(self):
        print(f"[DevOps Agent] Initiating CI/CD pipeline...")
        time.sleep(1)
        print(f"[DevOps Agent] Building docker image and deploying to staging... 🚀")
        return {"status": "deployed"}
class PackagerAgent:
    def package(self):
        print(f"[Packager Agent] Zipping workspace into App.zip...")
        time.sleep(1)
        return {"status": "packaged"}

def run_dry_run():
    print("==========================================")
    print("   Guided Co-Creation CLI Simulation      ")
    print("==========================================\n")
    
    rl_agent = RLAgent()
    planner = PlannerAgent()
    architect = ArchitectAgent()
    writer = WriterAgent()
    reviewer = ReviewerAgent()
    security = SecurityAgent()
    qa = QAAgent()
    devops = DevOpsAgent()
    
    # Simulate User Chat
    chat_history = [{"role": "user", "content": "A bakery website"}]
    context_hash = hashlib.md5("bakery website".encode()).hexdigest()[:8]
    
    print(f"👤 USER: {chat_history[0]['content']}")
    
    packager = PackagerAgent()
    
    # Simulate User Chat
    chat_history = [{"role": "user", "content": "A bakery website"}]
    context_hash = hashlib.md5("bakery website".encode()).hexdigest()[:8]
    
    print(f"👤 USER: {chat_history[0]['content']}")
    
    # 1. Plan Phase 1 (Needs Clarification)
    plan_res = planner.plan(chat_history)
    if plan_res["status"] == "clarification_needed":
        chat_history.append({"role": "ai", "content": plan_res["question"]})
        print(f"🤖 AI: {plan_res['question']}")
        
        # Simulate User Response
        user_reply = "No, just a static menu display please."
        chat_history.append({"role": "user", "content": user_reply})
        print(f"👤 USER: {user_reply}")
        
    # 2. Plan Phase 2 (Blueprint Ready)
    plan_res2 = planner.plan(chat_history)
    
    # Pipeline execution after approval
    if plan_res2["status"] == "blueprint_ready":
        print(f"🤖 AI: Great! Generating your app now...\n")
        
        # 3. Architecture Phase
        arch_res = architect.design(plan_res2["status"])
        
        chosen_ide = rl_agent.choose_ide(context_hash)
        attempt = 1
        final_status = "failed"
        
        while attempt <= 3:
            # 4. Writing
            exec_res = writer.execute(chosen_ide, attempt)
            
            # 5. Reviewing
            rev_res = reviewer.review(exec_res["status"])
            
            if rev_res["status"] == "approved":
                # 6. Security Scan
                sec_res = security.scan()
                if sec_res["status"] == "safe":
                    # 7. QA Testing
                    qa_res = qa.test()
                    if qa_res["status"] == "passed":
                        final_status = "approved"
                        break
                    else:
                        print(f"🔁 Sending back to Writer due to QA failure.")
                else:
                    print(f"🔁 Sending back to Writer due to Security vulnerabilities.")
            
            attempt += 1
            
        if final_status == "approved":
            # 8. DevOps Deployment
            devops.deploy()
            rl_agent.update_q_value(context_hash, chosen_ide, 10.0)
            print(f"\n🎉 App generation and deployment complete! Ready for production.")
        else:
            rl_agent.update_q_value(context_hash, chosen_ide, -5.0)
            print(f"\n❌ Pipeline failed after maximum attempts. Please intervene.")
            exec_res = writer.execute(chosen_ide, attempt)
            rev_res = reviewer.review(exec_res["status"])
            
            if rev_res["status"] == "approved":
                final_status = "approved"
                break
            attempt += 1
            
        if final_status == "approved":
            packager.package()
            rl_agent.update_q_value(context_hash, chosen_ide, 10.0)
            print(f"\n🎉 App generation complete! Ready for download.")
        else:
            print(f"\n❌ Pipeline failed. Please try again.")
            
if __name__ == "__main__":
    run_dry_run()
