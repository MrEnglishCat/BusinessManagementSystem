from fastapi import Request
from pydantic_core import ValidationError
from starlette_admin.auth import AdminUser, AuthProvider
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.exceptions import LoginFailed

from app.config.db import async_session_maker
from app.dependencies.service import get_service
from app.services.users import UserService
from app.utils.enums_service import ServiceTypeEnum
from app.schemas.users.users import LoginSchema, UserResponseSchema
from argon2 import PasswordHasher

from app.utils.passwd import get_password_hash, verify_password
from app.models.users import UserRole


class WebAuthProvider(AuthProvider):
    async def login(self, username, password, remember_me, request, response):
        try:
            LoginSchema(username=username, password=password)
        except ValidationError:
            raise LoginFailed("Invalid username or password")

        async with async_session_maker() as session:
            user_service = get_service(ServiceTypeEnum.USER)
            user_from_db = await user_service.get_user_after_login(
                session=session,
                **{"username": username},
            )
            if not user_from_db:
                raise LoginFailed("Username or password is invalid")
            if not verify_password(
                hash_password=user_from_db.hashed_password,
                password=password,  # FIXME AttributeError: 'SecretStr' object has no attribute 'encode'
            ):
                raise LoginFailed("Username or password is invalid")
        user = UserResponseSchema.model_validate(user_from_db)
        request.session.update({"username": user.username})
        request.state.admin_user = user
        return response

    async def logout(self, request, response):
        request.session.clear()
        request.state.admin_user = None
        request.state.user = None
        return response

    def get_admin_user(self, request: Request) -> AdminUser:
        user = request.state.admin_user
        return AdminUser(
            username=user.username,
        )

    async def is_authenticated(self, request: Request) -> bool:
        username = request.session.get("username", None)
        if not username:
            return False

        user_service = get_service(ServiceTypeEnum.USER)
        async with async_session_maker() as session:
            user = await user_service.get_one(session, **{"username": username})
            if not user:
                return False
            if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
                return False
            request.state.admin_user = user
            request.state.user = user

        return True
