from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService
from ..schemas.tasks import TaskResponseSchema, TaskCommentResponseSchema


class TaskService(BaseService):

    async def get_all(self, session: AsyncSession):
        tasks = await super().get_all(session)
        if tasks:
            return [TaskResponseSchema.model_validate(task) for task in tasks]
        return None

    async def get_one(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        task = await super().get_one(session, **filter_by)
        if task:
            return TaskResponseSchema.model_validate(task)
        return None

    async def add(self, session: AsyncSession, **values):
        new_task = await super().add(session, **values)
        return TaskResponseSchema.model_validate(new_task)

    async def update(self, session, id, **values):
        update_task = await super().update(session, id, **values)
        if update_task:
            return TaskCommentResponseSchema.model_validate(update_task)
        return None


class TaskCommentService(BaseService):

    async def get_all(self, session: AsyncSession):
        task_comments = await super().get_all(session)
        if task_comments:
            return [
                TaskCommentResponseSchema.model_validate(task_comment)
                for task_comment in task_comments
            ]
        return None

    async def get_one(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        task_comment = await super().get_one(session, **filter_by)
        if task_comment:
            return TaskCommentResponseSchema.model_validate(task_comment)
        return None

    async def add(self, session: AsyncSession, **values):
        new_task_comment = await super().add(session, **values)
        return TaskCommentResponseSchema.model_validate(new_task_comment)

    async def update(self, session, id, **values):
        update_task_comment = await super().update(session, id, **values)
        if update_task_comment:
            return TaskCommentResponseSchema.model_validate(update_task_comment)
        return None
