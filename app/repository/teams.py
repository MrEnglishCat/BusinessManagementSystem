from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from ..models import TeamModel, UserModel


class TeamRepository(BaseRepository):
    model = TeamModel

    async def get_members(self, session: AsyncSession, team_id: int):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.members))
            .where(self.model.id == team_id)
        )
        result = await session.execute(stmt)
        return result.scalar()
