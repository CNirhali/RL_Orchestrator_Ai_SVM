from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
from orchestrator.router import run_orchestrator

app = FastAPI(title="Master Agent Orchestrator")

class TaskRequest(BaseModel):
    repository_url: str
    description: str
    jira_id: str | None = None
    teams_thread_id: str | None = None

@app.post("/webhook/task")
async def receive_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Endpoint to receive tasks from Jira/Teams.
    """
    task_id = str(uuid.uuid4())
    # Spin off the orchestrator in the background
    background_tasks.add_task(run_orchestrator, task_id, request.model_dump())
    
    return {"status": "accepted", "task_id": task_id, "message": "Task queued for orchestration."}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
