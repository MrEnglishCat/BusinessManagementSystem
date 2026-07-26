from .base_repository import BaseRepository
from ..models import EvaluationModel, UserModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime


class EvaluationRepository(BaseRepository):
    model = EvaluationModel

    async def average_evaluation(
        self, session: AsyncSession, start_date: datetime, end_date: datetime
    ):
        stmt = (
            select(
                UserModel.id,
                UserModel.username,
                func.avg(self.model.score).label("avg_score"),
            )
            .join(self.model, self.model.employee_id == UserModel.id)
            .where(
                and_(
                    self.model.created_at >= start_date,
                    self.model.created_at <= end_date,
                )
            )
            .group_by(UserModel.id, UserModel.username)
            .order_by(func.avg(self.model.score).desc())
        )

        result = await session.execute(stmt)
        return result.all()
