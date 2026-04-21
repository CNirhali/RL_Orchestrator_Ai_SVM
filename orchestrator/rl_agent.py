import json
import os
import numpy as np

# Simple epsilon-greedy RL agent for selecting an IDE
class RLAgent:
    def __init__(self, state_file="rl_state.json"):
        self.state_file = state_file
        self.epsilon = 0.2  # Exploration rate
        self.ides = ["cursor", "windsurf", "claude", "vscode_cline"]
        self.q_table = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize Q-values for each IDE to 0
            return {ide: 0.0 for ide in self.ides}

    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.q_table, f)

    def choose_ide(self, task_type: str = "general") -> str:
        # In a more advanced version, task_type would be part of the state.
        # For this PoC, we just use a global Q-table for the IDEs.
        if np.random.rand() < self.epsilon:
            # Explore
            chosen = np.random.choice(self.ides)
            print(f"[RL] Exploring: randomly chose {chosen}")
        else:
            # Exploit
            chosen = max(self.q_table, key=self.q_table.get)
            print(f"[RL] Exploiting: chose best known {chosen} (Q={self.q_table[chosen]})")
        return chosen

    def update_q_value(self, ide: str, reward: float, alpha=0.1):
        # Q(s, a) = Q(s, a) + alpha * (reward - Q(s, a))
        current_q = self.q_table[ide]
        new_q = current_q + alpha * (reward - current_q)
        self.q_table[ide] = new_q
        self.save_state()
        print(f"[RL] Updated Q-value for {ide}: {current_q:.2f} -> {new_q:.2f}")

rl_agent = RLAgent()
