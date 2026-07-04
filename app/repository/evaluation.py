from .base_repository import BaseRepository
from ..models import EvaluationModel


class EvaluationRepository(BaseRepository):
    model = EvaluationModel
