from .base_repository import BaseRepository
from ..models.tasks import TaskModel


class TaskRepository(BaseRepository):
    model = TaskModel
