from sqlalchemy import delete, update, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .base_repository import BaseRepository
from ..models import UserModel, MeetingModel


class UserRepository(BaseRepository):
    model = UserModel

    async def get_users_without_teams(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).where(self.model.team_id == None)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_all_with_teams(self, session: AsyncSession):
        stmt = select(self.model).options(selectinload(self.model.team))
        coro_result = await session.execute(stmt)
        return coro_result.scalars().all()

    async def get_user_meetings(self, session: AsyncSession, user_id: int):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.meetings))
            .where(self.model.id == user_id)
        )
        user_meetings = await session.execute(stmt)

        return user_meetings.all()

    async def get_user_evaluations(self, session: AsyncSession, user_id: int):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.evaluations))
            .where(self.model.id == user_id)
        )
        user_meetings = await session.execute(stmt)

        return user_meetings.scalar()

    async def bulk_delete(self, session: AsyncSession):
        stmt = delete(self.model).where(self.model.is_superuser == False)
        await session.execute(stmt)
