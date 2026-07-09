from sqlalchemy.ext.asyncio import AsyncSession
from .base import BaseService
from ..schemas import MeetingResponseSchema, MeetingBaseSchema


class MeetingService(BaseService):

    async def get_all(self, session: AsyncSession):
        meetings = await super().get_all(session)
        if meetings:
            return [
                MeetingResponseSchema.model_validate(meeting) for meeting in meetings
            ]
        return None

    async def get_one(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        meeting = await super().get_one(session, **filter_by)
        if meeting:
            return MeetingResponseSchema.model_validate(meeting)
        return None

    async def add(self, session: AsyncSession, **values):
        new_meeting = await super().add(session, **values)
        return MeetingResponseSchema.model_validate(new_meeting)

    async def update(self, session, id, **values):
        update_meeting = await super().update(session, id, **values)
        if update_meeting:
            return MeetingResponseSchema.model_validate(update_meeting)
        return None
