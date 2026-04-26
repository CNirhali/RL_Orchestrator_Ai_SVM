import uuid
from typing import Optional

from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
from orchestrator.router import run_orchestrator
from orchestrator.rl_agent import rl_agent

app = FastAPI(title="Master Agent Orchestrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_logging()
logger = get_logger(__name__)

class TaskRequest(BaseModel):
    repository_url: str = "local"
    description: str
    role: Optional[str] = None
    jira_id: Optional[str] = None
    teams_thread_id: Optional[str] = None
app = FastAPI(title="App Factory Orchestrator")

class GenerateRequest(BaseModel):
    user_prompt: str

@app.post("/api/generate")
async def receive_prompt(request: GenerateRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to receive natural language prompts from consumers.
    """
    task_id = str(uuid.uuid4())
    # Spin off the orchestrator in the background
    background_tasks.add_task(run_orchestrator, task_id, request.model_dump())
    
    return {"status": "accepted", "task_id": task_id, "message": "App generation pipeline started."}

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

@app.get("/q_table")
def get_q_table():
    return {"q_table": rl_agent.get_all_scores()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
