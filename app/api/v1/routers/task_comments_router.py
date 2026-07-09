from fastapi import APIRouter, Depends, status, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from ....utils.enums_service import ServiceTypeEnum
from ....services.base import BaseService
from ....config.response import ResponseFactory, BaseResponse
from ....config.db import get_session
from ....dependencies.service import get_service_dependency
from ....schemas import TaskCommentBaseSchema

task_comments_router = APIRouter(prefix="/task_comments", tags=["Task comments"])


@task_comments_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_tasks(
    session: AsyncSession = Depends(get_session),
    task_comment_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.TASK_COMMENT)
    ),
):
    task_comments = await task_comment_service.get_all(session=session)
    if task_comments:
        return ResponseFactory.ok(data=task_comments)
    return ResponseFactory.error(message="Task comment is not found")


@task_comments_router.get(
    "/{task_comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_tasks_by_id(
    task_comment_id: int = Path(),
    session: AsyncSession = Depends(get_session),
    task_comment_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.TASK_COMMENT)
    ),
):
    task_comment = await task_comment_service.get_one(
        session=session, **{"id": task_comment_id}
    )
    if task_comment:
        return ResponseFactory.ok(data=task_comment)
    return ResponseFactory.error(message="Task comment is not found")


@task_comments_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_tasks(
    task_comment: TaskCommentBaseSchema = Body(),
    session: AsyncSession = Depends(get_session),
    task_comment_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.TASK_COMMENT)
    ),
):

    new_task_comment = await task_comment_service.add(
        session=session, **task_comment.model_dump()
    )
    return ResponseFactory.ok(data=new_task_comment)


@task_comments_router.delete(
    "/{task_comment_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_tasks_by_id(
    task_comment_id: int = Path(),
    session: AsyncSession = Depends(get_session),
    task_comment_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.TASK_COMMENT)
    ),
):
    task_comment = await task_comment_service.delete(
        session=session, **{"id": task_comment_id}
    )
    if task_comment:
        return ResponseFactory.ok(data=task_comment)
    return ResponseFactory.error("Task comment is not found")
