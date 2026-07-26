from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, select, insert, delete
from datetime import datetime, UTC

from app.repository.users import UserRepository
from .base_repository import BaseRepository
from ..models import MeetingModel, meeting_participants, UserModel
from ..utils.enums_service import MeetingStatusEmun


class MeetingRepository(BaseRepository):
    model = MeetingModel

    async def get_all(self, session: AsyncSession):
        stmt = select(self.model).where(self.model.status != MeetingStatusEmun.CANCELED)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_all_canceled(self, session: AsyncSession):
        stmt = select(self.model).where(self.model.status == MeetingStatusEmun.CANCELED)
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

    async def insert(self, session: AsyncSession, meeting: dict, participants: list):
        stmt = insert(self.model).values(meeting).returning(self.model)
        new_meeting = await session.execute(stmt)

        meeting = new_meeting.scalar_one_or_none()
        if participants:
            users = await UserRepository().select_in(
                session=session, users=participants
            )
            if await self.check_overlap_for_users(
                session,
                [user.id for user in users],
                meeting.get("start_time"),
                meeting.get("end_time"),
            ):

                raise HTTPException(
                    400, "One or more participants are already busy at this time"
                )

            new_meeting_participants = [
                {"meeting_id": meeting.id, "user_id": user.id} for user in users
            ]
            await session.execute(
                meeting_participants.insert().values(new_meeting_participants)
            )
        return meeting

    async def check_overlap_for_users(
        self,
        session: AsyncSession,
        user_ids: list[int],
        start_time: datetime,
        end_time: datetime,
        exclude_meeting_id: int | None = None,
    ) -> bool:

        participant_subquery = (
            select(meeting_participants.c.meeting_id)
            .where(meeting_participants.c.user_id.in_(user_ids))
            .distinct()
        )

        stmt = select(MeetingModel).where(
            MeetingModel.id.in_(participant_subquery),
            MeetingModel.start_time <= end_time,
            MeetingModel.end_time >= start_time,
            MeetingModel.status != MeetingStatusEmun.CANCELED,
        )

        if exclude_meeting_id is not None:
            stmt = stmt.where(MeetingModel.id != exclude_meeting_id)

        stmt = stmt.limit(1)
        result = await session.execute(stmt)
        scalar_result = result.scalar_one_or_none()

        return scalar_result is not None

    async def add_paricipants(
        self, session: AsyncSession, meeting_id: int, participants_username: list
    ):

        stmt = (
            insert(meeting_participants)
            .from_select(
                ["meeting_id", "user_id"],
                select(
                    select(meeting_id).label("meeting_id"),
                    UserModel.id.label("user_id"),
                ).where(UserModel.username.in_(participants_username)),
            )
            .returning(meeting_participants)
        )
        execute_result = await session.execute(stmt)
        return execute_result.all()

    async def delete_paricipants(
        self, session: AsyncSession, meeting_id: int, participants_username: list
    ):

        select_stmt = select(UserModel.id).where(
            UserModel.username.in_(participants_username)
        )

        delete_stmt = delete(meeting_participants).where(
            meeting_participants.c.meeting_id == meeting_id,
            meeting_participants.c.user_id.in_(select_stmt),
        )
        execute_result = await session.execute(delete_stmt)
        return execute_result.rowcount
