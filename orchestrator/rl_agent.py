import json
import os
import random

from orchestrator.config import get_settings
from orchestrator.logging_utils import get_logger


class RLAgent:
    def __init__(self, state_file="rl_state.json"):
        self.state_file = state_file
        self.epsilon = 0.2  # Exploration rate
        self.ides = ["cursor", "windsurf", "claude", "vscode_cline"]
        self.q_table = self.load_state()

    def load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                return {}
        return {} # 2D structure: {context_hash: {ide: score}}

    def save_state(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.q_table, f)
            
    def _ensure_context(self, context_hash: str):
        if context_hash not in self.q_table:
            self.q_table[context_hash] = {ide: 0.0 for ide in self.ides}

    def choose_ide(self, context_hash: str) -> str:
        logger = get_logger(__name__)
        self._ensure_context(context_hash)
        context_scores = self.q_table[context_hash]
        
        if random.random() < self.epsilon:
            # Explore
            chosen = random.choice(self.ides)
            logger.info("rl explore chosen=%s context_hash=%s", chosen, context_hash)
        else:
            # Exploit
            chosen = max(context_scores, key=context_scores.get)
            logger.info(
                "rl exploit chosen=%s q=%.2f context_hash=%s",
                chosen,
                context_scores[chosen],
                context_hash,
            )
        return chosen

    def calculate_reward(
        self, success: bool, cost: float, time_taken: float, lint_errors: int
    ) -> float:
        """
        Multi-objective reward function.
        Base points for success/failure, minus penalties for cost and low quality.
        """
        base = 10.0 if success else -10.0
        cost_penalty = cost * 0.1
        quality_penalty = lint_errors * 0.5
        time_penalty = time_taken * 0.05
        
        total_reward = base - cost_penalty - quality_penalty - time_penalty
        return total_reward

    def update_q_value(self, context_hash: str, ide: str, reward: float, alpha=0.1):
        logger = get_logger(__name__)
        self._ensure_context(context_hash)
        current_q = self.q_table[context_hash][ide]
        new_q = current_q + alpha * (reward - current_q)
        self.q_table[context_hash][ide] = new_q
        self.save_state()
        logger.info(
            "rl q_update ide=%s context_hash=%s old_q=%.2f new_q=%.2f",
            ide,
            context_hash,
            current_q,
            new_q,
        )

_settings = get_settings()
rl_agent = RLAgent(state_file=_settings.rl_state_file)
rl_agent.epsilon = _settings.rl_epsilon
