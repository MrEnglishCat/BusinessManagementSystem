from fastapi import APIRouter

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.get("/")
async def get_tasks():
    return {"message": "Все оценки"}


@tasks_router.get("/{task_id}")
async def get_tasks_by_id(task_id: int):
    return {"message": "Все оценки"}


@tasks_router.post("/")
async def post_tasks():
    return {"message": "Все оценки"}


@tasks_router.delete("/{task_id}")
async def delete_tasks_by_id(task_id: int):
    return {"message": "Все оценки"}
