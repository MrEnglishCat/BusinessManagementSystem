from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from ..schemas import MeetingResponseSchema, MeetingCancelSchema, MeetingCreateSchema


class MeetingService(BaseService):

    async def get_all(self, session: AsyncSession):
        meetings = await self.repository.get_all(session)
        if meetings:
            return [
                MeetingResponseSchema.model_validate(meeting) for meeting in meetings
            ]
        return None

    async def get_all_canceled(self, session: AsyncSession):
        meetings = await self.repository.get_all_canceled(session)
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

    async def add(self, session: AsyncSession, meeting_create_schema, current_user):
        meeting = meeting_create_schema.model_dump()
        meeting["created_by"] = current_user.id
        participants = [user.get("username") for user in meeting.pop("participants")]
        new_meeting = await self.repository.insert(session, meeting, participants)
        if new_meeting:
            return MeetingResponseSchema.model_validate(new_meeting)
        return None

    async def update(self, session, id, **values):
        update_meeting = await super().update(session, id, **values)
        if update_meeting:
            return MeetingResponseSchema.model_validate(update_meeting)
        return None

    async def cancel_meeting(self, session: AsyncSession, meeting: MeetingCancelSchema):
        canceled_meeting_id = await self.repository.cancel_meeting(
            session=session, meeting=meeting
        )
        if canceled_meeting_id:
            return canceled_meeting_id
        return None
