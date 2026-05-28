from fastapi import APIRouter

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])


@tasks_router.get("/")
async def get_tasks():
    return {"message": "Все оценки"}
