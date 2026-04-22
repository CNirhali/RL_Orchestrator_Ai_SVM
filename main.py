import uuid
from typing import Optional

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from orchestrator.config import get_settings
from orchestrator.logging_utils import configure_logging, get_logger
from orchestrator.router import run_orchestrator

app = FastAPI(title="Master Agent Orchestrator")
configure_logging()
logger = get_logger(__name__)

class TaskRequest(BaseModel):
    repository_url: str
    description: str
    jira_id: Optional[str] = None
    teams_thread_id: Optional[str] = None

_TASKS: dict[str, dict] = {}


@app.post("/webhook/task")
async def receive_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to receive tasks from Jira/Teams.
    """
    task_id = str(uuid.uuid4())
    payload = request.model_dump()
    _TASKS[task_id] = {"status": "queued", "request": payload}
    logger.info("task accepted", extra={"task_id": task_id})

    def _run():
        task_logger = get_logger("orchestrator.run", task_id)
        _TASKS[task_id] = {"status": "running", "request": payload}
        try:
            result = run_orchestrator(task_id, payload)
            _TASKS[task_id] = {"status": "completed", "request": payload, "result": result}
            task_logger.info("task completed")
        except Exception as e:
            _TASKS[task_id] = {"status": "failed", "request": payload, "error": repr(e)}
            task_logger.exception("task failed")

    # Spin off the orchestrator in the background (single-process prototype).
    background_tasks.add_task(_run)
    
    return {"status": "accepted", "task_id": task_id, "message": "Task queued for orchestration."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/ready")
def readiness_check():
    """
    Lightweight readiness for this single-instance prototype:
    verifies configured workspace root exists and RL state path is writable.
    """
    settings = get_settings()
    import os

    # Workspace root
    os.makedirs(settings.workspace_root, exist_ok=True)
    testfile = os.path.join(settings.workspace_root, ".write_test")
    with open(testfile, "w") as f:
        f.write("ok")
    os.remove(testfile)

    # RL state path (directory)
    state_dir = os.path.dirname(settings.rl_state_file) or "."
    os.makedirs(state_dir, exist_ok=True)
    return {"status": "ready"}


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    task = _TASKS.get(task_id)
    if task is None:
        return {"status": "not_found", "task_id": task_id}
    return {"task_id": task_id, **task}


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(app, host=settings.host, port=settings.port)
