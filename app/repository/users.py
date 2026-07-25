from sqlalchemy import delete, update, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .base_repository import BaseRepository
from ..models import UserModel, MeetingModel


class UserRepository(BaseRepository):
    model = UserModel

    async def get_user_meetings(self, session: AsyncSession, user_id):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.meetings))
            .where(self.model.id == user_id)
        )
        user_meetings = await session.execute(stmt)

        return user_meetings.scalar()
