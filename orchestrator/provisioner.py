import os
import subprocess

from orchestrator.config import get_settings
from orchestrator.logging_utils import get_logger


class Provisioner:
    def __init__(self, base_workspace_dir="/tmp/master_agent_workspaces"):
        self.base_dir = base_workspace_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def provision_workspace(self, task_id: str, repo_url: str, description: str) -> str:
        """
        Clones the repo and creates a briefing document.
        Returns the path to the workspace.
        """
        settings = get_settings()
        logger = get_logger(__name__, task_id)
        workspace_path = os.path.join(self.base_dir, task_id)
        logger.info("provision workspace_path=%s", workspace_path)
        
        # 1. Clone repo (Simulated or actual if git is available and repo is public)
        # For safety in this demo, we'll just create a directory if repo_url is dummy.
        if settings.enable_git_clone and repo_url.startswith("http"):
            try:
                subprocess.run(
                    ["git", "clone", repo_url, workspace_path],
                    check=True,
                    timeout=settings.git_clone_timeout_s,
                )
            except Exception as e:
                logger.warning("git clone failed; creating empty workspace error=%r", e)
                os.makedirs(workspace_path, exist_ok=True)
        else:
            os.makedirs(workspace_path, exist_ok=True)

        # 2. Generate Briefing Document
        briefing_path = os.path.join(workspace_path, "MEMORIES.md")
        with open(briefing_path, "w") as f:
            f.write(f"# Task Briefing\n\n## Description\n{description}\n\n")
            f.write(
                "## Context\nThis workspace was automatically provisioned by the Master Agent.\n"
            )
            
        logger.info("briefing created path=%s", briefing_path)
        return workspace_path

_settings = get_settings()
provisioner = Provisioner(base_workspace_dir=_settings.workspace_root)
