from .base_repository import BaseRepository
from ..models import TeamModel


class TeamRepository(BaseRepository):
    model = TeamModel
