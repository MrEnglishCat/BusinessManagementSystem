from fastapi import APIRouter, Path, Body, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from ....config.db import get_async_session
from ....config.response import BaseResponse, ResponseFactory
from ....dependencies.service import get_service_dependency
from ....dependencies.general import get_current_user
from ....utils.enums_service import ServiceTypeEnum
from ....services.base import BaseService
from ....schemas import TaskBaseSchema

tasks_router = APIRouter(prefix="/tasks", tags=["Tasks"])


@tasks_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_tasks(
    session: AsyncSession = Depends(get_async_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    tasks = await task_service.get_all(session=session)
    if tasks:
        return ResponseFactory.ok(data=tasks)
    return ResponseFactory.error(message="Task is not found")


@tasks_router.get(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_task_by_id(
    task_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    task = await task_service.get_one(session=session, id=task_id)
    if task:
        return ResponseFactory.ok(data=task)
    return ResponseFactory.error(message="Task is not found")


@tasks_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_tasks(
    task: TaskBaseSchema = Body(),
    current_user: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    new_task = await task_service.add(session=session, **task.model_dump())
    return ResponseFactory.ok(data=new_task)


@tasks_router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_task_by_id(
    task_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    delete_task_count = await task_service.delete(session=session, id=task_id)
    if delete_task_count:
        return ResponseFactory.ok(data=delete_task_count)
    return ResponseFactory.error(message="Task is not found")


@tasks_router.patch("/{task_id}")
async def patch_team_by_id(
    task: TaskBaseSchema,
    task_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    task_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TASK)),
):
    update_task = await task_service.update(
        session=session, id=task_id, **task.model_dump()
    )
    if update_task:
        return ResponseFactory.ok(data=update_task)
    return ResponseFactory.error(message="Task is not found")
