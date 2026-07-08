from .base import BaseService
from ..schemas import UserResponseSchema, AfterAuthUserSchema


class UserService(BaseService):

    async def get_user_after_login(self, session, **filter_by):
        user = await super().get_one(session, **filter_by)
        if user:
            # return AfterAuthUserSchema.model_validate(user)
            return user
        return None

    async def get_all(self, session):
        users = await super().get_all(session)
        return [UserResponseSchema.model_validate(user) for user in users]

    async def get_one(self, session, **filter_by):
        user = await super().get_one(session, **filter_by)
        if user:
            return UserResponseSchema.model_validate(user)
        return None

    async def add(self, session, **values):
        new_user = await super().add(session, **values)
        return UserResponseSchema.model_validate(new_user)
