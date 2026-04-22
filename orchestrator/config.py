import os
from dataclasses import dataclass
from typing import Optional


def _env_str(name: str, default: str) -> str:
    val = os.getenv(name)
    return default if val is None or val == "" else val


def _env_int(name: str, default: int) -> int:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    return int(val)


def _env_float(name: str, default: float) -> float:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    return float(val)


def _env_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None or val == "":
        return default
    return val.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _env_optional_int(name: str) -> Optional[int]:
    val = os.getenv(name)
    if val is None or val == "":
        return None
    return int(val)


@dataclass(frozen=True)
class Settings:
    # Server
    host: str = _env_str("MAO_HOST", "0.0.0.0")
    port: int = _env_int("MAO_PORT", 8000)

    # Orchestration behavior
    max_attempts: int = _env_int("MAO_MAX_ATTEMPTS", 3)

    # Provisioning / persistence (local prototype)
    workspace_root: str = _env_str("MAO_WORKSPACE_ROOT", "/tmp/master_agent_workspaces")
    enable_git_clone: bool = _env_bool("MAO_ENABLE_GIT_CLONE", True)
    git_clone_timeout_s: float = _env_float("MAO_GIT_CLONE_TIMEOUT_S", 60.0)

    rl_state_file: str = _env_str("MAO_RL_STATE_FILE", "rl_state.json")
    rl_epsilon: float = _env_float("MAO_RL_EPSILON", 0.2)

    # Simulation controls (used by executors)
    sim_seed: Optional[int] = _env_optional_int("MAO_SIM_SEED")
    sim_sleep_s: float = _env_float("MAO_SIM_SLEEP_S", 1.0)


def get_settings() -> Settings:
    # Single place to initialize settings (and later, caching if desired).
    return Settings()

