from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from ..schemas import (
    UserResponseSchema,
    MeetingResponseSchema,
    EvaluationResponseSchema,
)


class UserService(BaseService):

    async def get_user_after_login(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        user = await super().get_one(session, **filter_by)
        if user:
            return user
        return None

    async def get_all(self, session: AsyncSession):
        users = await super().get_all(session)
        return [UserResponseSchema.model_validate(user) for user in users]

    async def get_one(self, session: AsyncSession, **filter_by):
        user = await super().get_one(session, **filter_by)
        if user:
            return UserResponseSchema.model_validate(user)
        return None

    async def add(self, session: AsyncSession, **values):
        new_user = await super().add(session, **values)
        return UserResponseSchema.model_validate(new_user)

    async def update(
        self,
        session: AsyncSession,
        id: int,
        **values,
    ):
        update_result = await super().update(session, id, **values)

        if update_result:
            return UserResponseSchema.model_validate(update_result)
        return None

    async def get_user_meetings(self, session: AsyncSession, user_id: int):
        user = await self.repository.get_user_meetings(session=session, user_id=user_id)
        if user and user.meetings:
            return [
                MeetingResponseSchema.model_validate(user_meeting)
                for user_meeting in user.meetings
            ]
        return None

    async def get_user_evaluations(self, session: AsyncSession, user_id: int):
        user = await self.repository.get_user_evaluations(
            session=session, user_id=user_id
        )
        print("HERE")
        print(user)
        print(user.evaluations)
        print("HERE")
        if user and user.evaluations:
            return [
                EvaluationResponseSchema.model_validate(user_evaluations)
                for user_evaluations in user.evaluations
            ]
        return None
