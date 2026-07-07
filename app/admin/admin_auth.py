from fastapi import Request
from pydantic_core import ValidationError
from starlette_admin.auth import AdminUser, AuthProvider
from starlette.requests import Request
from starlette.responses import Response
from starlette_admin.exceptions import LoginFailed

from app.config.db import AsyncSession
from app.dependencies.service import get_service
from app.services.users import UserService
from app.utils.enums_service import ServiceTypeEnum
from app.schemas.users import LoginSchema
from argon2 import PasswordHasher

from app.utils.passwd import get_password_hash, verify_password
from app.models.users import UserRole


class WebAuthProvider(AuthProvider):
    async def login(self, username, password, remember_me, request, response):
        try:
            LoginSchema(username=username, password=password)
        except ValidationError:
            raise LoginFailed("Invalid username or password")

        async with AsyncSession() as session:
            user_service = get_service(ServiceTypeEnum.USER)
            username_from_db = await user_service.get_one(
                session=session,
                **{"username": username},
            )
            if not username_from_db:
                raise LoginFailed("Username or password is invalid")
            if not verify_password(
                hash_password=username_from_db.password, password=password
            ):
                raise LoginFailed("Username or password is invalid")
        request.session.update({"username": username_from_db.username})
        request.state.admin_user = username_from_db
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
        async with AsyncSession() as session:
            user = await user_service.get_one(session, **{"username": username})
            if not user:
                return False
            if user.role not in (UserRole.ADMIN, UserRole.MANAGER):
                return False
            request.state.admin_user = user
            request.state.user = user

        return True
