from .base import BaseService
from ..schemas.tasks import TaskResponseSchema, TaskCommentResponseSchema


class TaskService(BaseService):
    async def get_all(self, session):
        tasks = await super().get_all(session)
        if tasks:
            return [TaskResponseSchema.model_validate(task) for task in tasks]
        return None

    async def get_one(self, session, **filter_by):
        task = await super().get_one(session, **filter_by)
        if task:
            return TaskResponseSchema.model_validate(task)
        return None

    async def add(self, session, **values):
        new_task = await super().add(session, **values)
        return TaskResponseSchema.model_validate(new_task)


class TaskCommentService(BaseService):
    async def get_all(self, session):
        task_comments = await super().get_all(session)
        if task_comments:
            return [
                TaskCommentResponseSchema.model_validate(task_comment)
                for task_comment in task_comments
            ]
        return None
