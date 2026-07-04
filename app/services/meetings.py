from .base import BaseService
from ..repository import MeetingRepository


class MeetingService(BaseService):
    repository = MeetingRepository
