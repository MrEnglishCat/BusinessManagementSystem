from .base import BaseService
from ..repository import EvaluationRepository


class EvaluationService(BaseService):
    repository = EvaluationRepository
