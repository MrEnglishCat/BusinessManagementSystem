from .base import BaseService
from ..schemas.tasks import TaskResponseSchema, TaskCommentResponseSchema


class TaskService(BaseService):
    async def get_all(self, session):
        tasks = await super().get_all(session)
        if tasks:
            return [TaskResponseSchema.model_validate(task) for task in tasks]
        return None


class TaskCommentService(BaseService): ...
