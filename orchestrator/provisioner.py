import os
import subprocess

class Provisioner:
    def __init__(self, base_workspace_dir="/tmp/master_agent_workspaces"):
        self.base_dir = base_workspace_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def provision_workspace(self, task_id: str, repo_url: str, description: str) -> str:
        """
        Clones the repo and creates a briefing document.
        Returns the path to the workspace.
        """
        workspace_path = os.path.join(self.base_dir, task_id)
        print(f"[Provisioner] Setting up workspace for task {task_id} at {workspace_path}")
        
        # 1. Clone repo (Simulated or actual if git is available and repo is public)
        # For safety in this demo, we'll just create a directory if repo_url is dummy.
        if repo_url.startswith("http"):
            try:
                subprocess.run(["git", "clone", repo_url, workspace_path], check=True)
            except Exception as e:
                print(f"[Provisioner] Git clone failed (maybe private repo?): {e}")
                os.makedirs(workspace_path, exist_ok=True)
        else:
            os.makedirs(workspace_path, exist_ok=True)

        # 2. Generate Briefing Document
        briefing_path = os.path.join(workspace_path, "MEMORIES.md")
        with open(briefing_path, "w") as f:
            f.write(f"# Task Briefing\n\n## Description\n{description}\n\n")
            f.write("## Context\nThis workspace was automatically provisioned by the Master Agent.\n")
            
        print(f"[Provisioner] Created briefing document at {briefing_path}")
        return workspace_path

provisioner = Provisioner()
