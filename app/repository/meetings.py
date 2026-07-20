from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select
from datetime import datetime, UTC
from .base_repository import BaseRepository
from ..models import MeetingModel
from ..utils.enums_service import MeetingStatusEmun


class MeetingRepository(BaseRepository):
    model = MeetingModel

    async def get_all(self, session: AsyncSession):
        stmt = select(self.model).where(self.model.status != MeetingStatusEmun.CANCELED)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def cancel_meeting(self, session: AsyncSession, meeting: int):
        stmt = (
            update(self.model)
            .where(self.model.id == meeting.id)
            .values(
                {
                    "status": MeetingStatusEmun.CANCELED,
                    "cancellation_reason": meeting.cancellation_reason,
                    "canceled_at": datetime.now(UTC),
                    # "canceled_by": "current_user" # DEVELOPMENT
                }
            )
            .returning(self.model.id)
        )

        result = await session.execute(stmt)

        return result.scalar()
