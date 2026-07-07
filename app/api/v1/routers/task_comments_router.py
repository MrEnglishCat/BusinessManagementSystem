from fastapi import APIRouter

task_comments_router = APIRouter(prefix="/task_comments", tags=["Task comments"])


@task_comments_router.get("/")
async def get_tasks():
    return {"message": "Все комментарии"}


@task_comments_router.get("/{task_comment_id}")
async def get_tasks_by_id(task_comment_id: int):
    return {"message": "Все комментарии"}


@task_comments_router.post("/")
async def post_tasks():
    return {"message": "Все комментарии"}


@task_comments_router.delete("/{task_comment_id}")
async def delete_tasks_by_id(task_comment_id: int):
    return {"message": "Все комментарии"}
