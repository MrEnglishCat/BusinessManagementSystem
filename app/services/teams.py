from .base import BaseService
from ..repository import TeamRepository


class TeamService(BaseService):
    repository = TeamRepository
