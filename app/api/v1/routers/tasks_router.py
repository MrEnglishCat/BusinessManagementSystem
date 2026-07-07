from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ....config.db import get_session
from ....config.response import BaseResponse, ResponseFactory
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum
from ....services.base import BaseService

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.get("/", status_code=status.HTTP_200_OK, response_model=BaseResponse)
async def get_tasks(
    session: AsyncSession = Depends(get_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    tasks = await task_service.get_all(session=session)
    if tasks:
        return ResponseFactory.ok(data=tasks)
    return ResponseFactory.error(message="No task found")


@tasks_router.get("/{task_id}")
async def get_tasks_by_id(task_id: int):
    return {"message": "Все оценки"}


@tasks_router.post("/")
async def post_tasks():
    return {"message": "Все оценки"}


@tasks_router.delete("/{task_id}")
async def delete_tasks_by_id(task_id: int):
    return {"message": "Все оценки"}
