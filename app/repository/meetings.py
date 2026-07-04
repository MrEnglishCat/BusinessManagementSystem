from .base_repository import BaseRepository
from ..models import MeetingModel


class MeetingRepository(BaseRepository):
    model = MeetingModel
