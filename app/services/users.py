from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from ..schemas import UserResponseSchema


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
