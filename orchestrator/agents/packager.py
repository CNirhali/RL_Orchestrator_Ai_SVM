import time

class PackagerAgent:
    def package(self, workspace_path: str) -> dict:
        print(f"[Packager Agent] Zipping workspace at {workspace_path}...")
        time.sleep(1)
        zip_path = f"{workspace_path}.zip"
        print(f"[Packager Agent] Successfully packaged product into {zip_path}")
        return {"status": "packaged", "zip_path": zip_path}

packager_agent = PackagerAgent()
