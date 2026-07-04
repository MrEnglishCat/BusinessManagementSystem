from .base import BaseService
from ..repository import TaskRepository, TaskCommentRepository


class TaskService(BaseService):
    repository = TaskRepository


class TaskCommentService(BaseService):
    repository = TaskCommentRepository
