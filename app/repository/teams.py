from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .base_repository import BaseRepository
from ..models import TeamModel


class TeamRepository(BaseRepository):
    model = TeamModel

    async def get_members(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result
