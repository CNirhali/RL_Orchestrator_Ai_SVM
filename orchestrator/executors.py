import random
import time
from typing import Callable, Dict, Optional

from orchestrator.config import get_settings
from orchestrator.logging_utils import get_logger


class BaseIDEAgent:
    agent_name = "base"
    base_success_chance = 0.5

    def execute(self, rng: random.Random, workspace_path: str, task_details: dict) -> dict:
        task_id = task_details.get("task_id") if isinstance(task_details, dict) else None
        logger = get_logger(__name__, task_id)
        logger.info(
            "ide_agent start agent=%s workspace_path=%s",
            self.agent_name,
            workspace_path,
        )

        exec_time = rng.uniform(1.0, 5.0)
        cost = rng.uniform(0.01, 0.50)
        success = rng.random() < self.base_success_chance
        metrics = {
            "time_taken": exec_time,
            "cost": cost,
            "lint_errors": 0 if success else rng.randint(1, 10),
            "tests_passed": success,
            "agent_name": self.agent_name,
        }
        status = "success" if success else "failed"
        logger.info("ide_agent finished agent=%s status=%s", self.agent_name, status)
        return {"status": status, "metrics": metrics}


class CursorIDEAgent(BaseIDEAgent):
    agent_name = "cursor"
    base_success_chance = 0.7


class ClaudeIDEAgent(BaseIDEAgent):
    agent_name = "claude"
    base_success_chance = 0.7


class WindsurfIDEAgent(BaseIDEAgent):
    agent_name = "windsurf"
    base_success_chance = 0.5


class VSCodeClineIDEAgent(BaseIDEAgent):
    agent_name = "vscode_cline"
    base_success_chance = 0.5


class IDEExecutor:
    def __init__(
        self,
        rng: Optional[random.Random] = None,
        sleep: Optional[Callable[[float], None]] = None,
        sleep_s: Optional[float] = None,
    ):
        settings = get_settings()
        seed = settings.sim_seed
        self.rng = rng or (random.Random(seed) if seed is not None else random.Random())
        self.sleep = sleep or time.sleep
        self.sleep_s = settings.sim_sleep_s if sleep_s is None else sleep_s
        self.ide_agents: Dict[str, BaseIDEAgent] = {
            "cursor": CursorIDEAgent(),
            "claude": ClaudeIDEAgent(),
            "windsurf": WindsurfIDEAgent(),
            "vscode_cline": VSCodeClineIDEAgent(),
        }

    def execute(self, ide_name: str, workspace_path: str, task_details: dict) -> dict:
        task_id = task_details.get("task_id") if isinstance(task_details, dict) else None
        logger = get_logger(__name__, task_id)
        logger.info("writer route ide_agent=%s workspace_path=%s", ide_name, workspace_path)

        if self.sleep_s > 0:
            self.sleep(self.sleep_s)
        ide_agent = self.ide_agents.get(ide_name, BaseIDEAgent())
        return ide_agent.execute(self.rng, workspace_path, task_details)


class ReviewerAgent:
    def __init__(
        self,
        rng: Optional[random.Random] = None,
        sleep: Optional[Callable[[float], None]] = None,
        sleep_s: Optional[float] = None,
    ):
        settings = get_settings()
        seed = settings.sim_seed
        self.rng = rng or (random.Random(seed + 1) if seed is not None else random.Random())
        self.sleep = sleep or time.sleep
        self.sleep_s = settings.sim_sleep_s if sleep_s is None else sleep_s

    def review(self, workspace_path: str, execution_result: dict) -> dict:
        logger = get_logger(__name__)
        logger.info("reviewer_agent start workspace_path=%s", workspace_path)
        if self.sleep_s > 0:
            self.sleep(self.sleep_s)
        
        cost = self.rng.uniform(0.01, 0.10)
        
        # The reviewer catches issues: high approval if writer succeeded, low otherwise.
        # If the writer succeeded, the reviewer passes it 95% of the time.
        writer_success = execution_result["status"] == "success"
        
        if writer_success:
            approved = self.rng.random() < 0.95
        else:
            approved = self.rng.random() < 0.10  # 10% chance a bad PR slips through
            
        metrics = {"cost": cost, "approved": approved}
        
        if approved:
            logger.info("reviewer_agent approved")
            return {"status": "approved", "metrics": metrics}
        else:
            logger.info("reviewer_agent rejected")
            return {"status": "rejected", "metrics": metrics}


executor = IDEExecutor()
reviewer = ReviewerAgent()
