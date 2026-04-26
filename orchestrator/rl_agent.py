import sqlite3
import random
import os

from orchestrator.config import get_settings
from orchestrator.logging_utils import get_logger

class RLAgent:
    def __init__(self, state_file="rl_state.db"):
        self.state_file = state_file
        self.epsilon = 0.2  # Exploration rate
        self.ides = ["cursor", "windsurf", "claude", "vscode_cline"]
        self._init_db()

    def _init_db(self):
        # Create directory if it doesn't exist
        state_dir = os.path.dirname(self.state_file)
        if state_dir:
            os.makedirs(state_dir, exist_ok=True)
            
        with sqlite3.connect(self.state_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS q_values (
                    context_hash TEXT,
                    ide TEXT,
                    score REAL,
                    PRIMARY KEY (context_hash, ide)
                )
            """)
            conn.commit()

    def _ensure_context(self, context_hash: str):
        with sqlite3.connect(self.state_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ide, score FROM q_values WHERE context_hash = ?", (context_hash,))
            rows = cursor.fetchall()
            existing_ides = {row[0]: row[1] for row in rows}
            
            # Insert any missing IDEs for this context
            missing = [(context_hash, ide, 0.0) for ide in self.ides if ide not in existing_ides]
            if missing:
                cursor.executemany(
                    "INSERT INTO q_values (context_hash, ide, score) VALUES (?, ?, ?)",
                    missing
                )
                conn.commit()

    def get_context_scores(self, context_hash: str) -> dict:
        self._ensure_context(context_hash)
        with sqlite3.connect(self.state_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT ide, score FROM q_values WHERE context_hash = ?", (context_hash,))
            return {row[0]: row[1] for row in cursor.fetchall()}

    def get_all_scores(self) -> dict:
        """Returns the full Q-table."""
        with sqlite3.connect(self.state_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT context_hash, ide, score FROM q_values")
            results = {}
            for row in cursor.fetchall():
                ctx, ide, score = row
                if ctx not in results:
                    results[ctx] = {}
                results[ctx][ide] = score
            return results

    def choose_ide(self, context_hash: str) -> str:
        logger = get_logger(__name__)
        context_scores = self.get_context_scores(context_hash)
        
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
        
        with sqlite3.connect(self.state_file) as conn:
            cursor = conn.cursor()
            # Atomically update Q-value (thread-safe transaction)
            cursor.execute("SELECT score FROM q_values WHERE context_hash = ? AND ide = ?", (context_hash, ide))
            row = cursor.fetchone()
            current_q = row[0] if row else 0.0
            
            new_q = current_q + alpha * (reward - current_q)
            
            cursor.execute(
                "UPDATE q_values SET score = ? WHERE context_hash = ? AND ide = ?",
                (new_q, context_hash, ide)
            )
            conn.commit()
            
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
