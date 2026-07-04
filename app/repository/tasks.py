from .base_repository import BaseRepository
from ..models import TaskModel, TaskCommentModel


class TaskRepository(BaseRepository):
    model = TaskModel


class TaskCommentRepository(BaseRepository):
    model = TaskCommentModel
