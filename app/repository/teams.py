from .base_repository import BaseRepository
from ..models.teams import TeamModel


class TeamRepository(BaseRepository):
    model = TeamModel
