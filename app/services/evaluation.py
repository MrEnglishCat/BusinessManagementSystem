from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService
from ..schemas import EvaluationBaseSchema, EvaluationResponseSchema


class EvaluationService(BaseService):

    async def get_all(self, session: AsyncSession):
        evaluations = await super().get_all(session)
        if evaluations:
            return [
                EvaluationResponseSchema.model_validate(evaluation)
                for evaluation in evaluations
            ]
        return None

    async def get_one(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        evaluation = await super().get_one(session, **filter_by)
        if evaluation:
            return EvaluationResponseSchema.model_validate(evaluation)
        return None

    async def add(self, session: AsyncSession, **values):
        new_evaluation = await super().add(session, **values)
        if new_evaluation:
            return EvaluationResponseSchema.model_validate(new_evaluation)
        return None

    async def update(self, session, id, **values):
        update_evaluation = await super().update(session, id, **values)
        if update_evaluation:
            return EvaluationBaseSchema.model_validate(update_evaluation)
        return None
