import uuid

from orchestrator.router import run_orchestrator

if __name__ == "__main__":
    task_id = str(uuid.uuid4())
    req = {
        "repository_url": "dummy",
        "description": "Fix a small bug in the authentication flow."
    }
    run_orchestrator(task_id, req)
