from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
from orchestrator.router import run_orchestrator

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
