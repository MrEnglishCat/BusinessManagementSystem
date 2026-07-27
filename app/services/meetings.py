from sqlalchemy.ext.asyncio import AsyncSession


from .base import BaseService
from ..schemas import (
    MeetingResponseSchema,
    MeetingCancelSchema,
    MeetingParticipantUpdateSchema,
)


class MeetingService(BaseService):

    async def get_all(self, session: AsyncSession):
        meetings = await self._repository.get_all(session)
        if meetings:
            return [
                MeetingResponseSchema.model_validate(meeting) for meeting in meetings
            ]
        return None

    async def get_all_canceled(self, session: AsyncSession):
        meetings = await self._repository.get_all_canceled(session)
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
        new_meeting = await self._repository.insert(session, meeting, participants)
        if new_meeting:
            return MeetingResponseSchema.model_validate(new_meeting)
        return None

    async def update(self, session, id, **values):
        update_meeting = await super().update(session, id, **values)
        if update_meeting:
            return MeetingResponseSchema.model_validate(update_meeting)
        return None

    async def cancel_meeting(
        self, session: AsyncSession, meeting: MeetingCancelSchema, current_user
    ):
        canceled_meeting_id = await self._repository.cancel_meeting(
            session=session, meeting=meeting, current_user=current_user
        )
        if canceled_meeting_id:
            return canceled_meeting_id
        return None

    async def add_participants(
        self,
        session: AsyncSession,
        meeting_id: int,
        participants_schema: MeetingParticipantUpdateSchema,
    ):
        participants_username = [
            participant.username for participant in participants_schema.participants
        ]
        db_result = await self._repository.add_paricipants(
            session=session,
            meeting_id=meeting_id,
            participants_username=participants_username,
        )
        if db_result:
            return db_result
        return None

    async def delete_participants(
        self,
        session: AsyncSession,
        meeting_id: int,
        participants_schema: MeetingParticipantUpdateSchema,
    ):
        participants_username = [
            participant.username for participant in participants_schema.participants
        ]
        db_result = await self._repository.delete_paricipants(
            session=session,
            meeting_id=meeting_id,
            participants_username=participants_username,
        )
        if db_result:
            return db_result
        return None
