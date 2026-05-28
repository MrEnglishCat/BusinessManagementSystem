from .base_repository import BaseRepository
from ..models.meetings import MeetingModel


class MeetingRepository(BaseRepository):
    model = MeetingModel
