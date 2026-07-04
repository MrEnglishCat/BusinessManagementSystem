from fastapi import APIRouter

teams_router = APIRouter(prefix="/teams", tags=["teams"])


@teams_router.get("/")
async def get_teams():
    return {"message": "Все оценки"}


@teams_router.get("/{task_id}")
async def get_teams_by_id(task_id: int):
    return {"message": "Все оценки"}


@teams_router.post("/")
async def post_teams():
    return {"message": "Все оценки"}


@teams_router.delete("/{task_id}")
async def delete_teams_by_id(task_id: int):
    return {"message": "Все оценки"}
