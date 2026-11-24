import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

app = FastAPI(title="Tasks Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://localhost:8001")

TASKS = [
    {"id": 1, "title": "Налаштувати Docker", "user_id": 1, "assignee": "Олена"},
]


class TaskCreate(BaseModel):
    title: str
    user_id: int


@app.get("/health")
def health():
    return {"status": "ok", "service": "tasks-service", "users_service_url": USERS_SERVICE_URL}


@app.get("/tasks")
def get_tasks():
    return TASKS


@app.post("/tasks", status_code=201)
async def create_task(task: TaskCreate):
    # Міжсервісна комунікація по HTTP API: перевіряємо користувача у users-service
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            resp = await client.get(f"{USERS_SERVICE_URL}/users/{task.user_id}")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Users service is unavailable")

    if resp.status_code == 404:
        raise HTTPException(status_code=400, detail="Assigned user does not exist")
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Error from users service")

    user_data = resp.json()
    new_task = {
        "id": len(TASKS) + 1,
        "title": task.title,
        "user_id": task.user_id,
        "assignee": user_data.get("name", "Unknown"),
    }
    TASKS.append(new_task)
    return new_task