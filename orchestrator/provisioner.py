import os

class Provisioner:
    def provision_workspace(self, task_id: str, prompt: str) -> str:
        print(f"[Provisioner] Received new prompt: '{prompt[:30]}...'")
        workspace_path = f"/tmp/workspace_app_{task_id}"
        print(f"[Provisioner] Creating new empty workspace at {workspace_path}")
        
        # In a real app, we would os.makedirs(workspace_path)
        
        # Generate MEMORIES.md for context
        memories_content = f"""# Consumer App Specs
- Idea: {prompt}
- Constraints: Ensure UI is consumer-friendly and non-technical.
"""
        print(f"[Provisioner] Generated context briefing for agents.")
        return workspace_path

provisioner = Provisioner()
