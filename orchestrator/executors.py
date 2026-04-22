import random
import time
from typing import Callable, Optional

from orchestrator.config import get_settings
from orchestrator.logging_utils import get_logger


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

    def execute(self, ide_name: str, workspace_path: str, task_details: dict) -> dict:
        task_id = task_details.get("task_id") if isinstance(task_details, dict) else None
        logger = get_logger(__name__, task_id)
        logger.info("writer start ide=%s workspace_path=%s", ide_name, workspace_path)
        
        # Simulate execution time and cost
        exec_time = self.rng.uniform(1.0, 5.0)
        if self.sleep_s > 0:
            self.sleep(self.sleep_s)
        cost = self.rng.uniform(0.01, 0.50)  # Simulated API/compute cost
        
        # Simulated outcome: different IDEs might have different simulated baselines
        base_success_chance = 0.7 if ide_name in ["cursor", "claude"] else 0.5
        success = self.rng.random() < base_success_chance
        
        metrics = {
            "time_taken": exec_time,
            "cost": cost,
            "lint_errors": 0 if success else self.rng.randint(1, 10),
            "tests_passed": success
        }
        
        if success:
            logger.info("writer success ide=%s", ide_name)
            return {"status": "success", "metrics": metrics}
        else:
            logger.info("writer failed ide=%s", ide_name)
            return {"status": "failed", "metrics": metrics}

class ReviewerExecutor:
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
        logger.info("reviewer start workspace_path=%s", workspace_path)
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
            logger.info("reviewer approved")
            return {"status": "approved", "metrics": metrics}
        else:
            logger.info("reviewer rejected")
            return {"status": "rejected", "metrics": metrics}

executor = IDEExecutor()
reviewer = ReviewerExecutor()
