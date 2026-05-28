from .base_repository import BaseRepository
from ..models.evaluation import EvaluationModel


class EvaluationRepository(BaseRepository):
    model = EvaluationModel
