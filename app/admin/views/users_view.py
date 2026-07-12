from fastapi import Request

from .base_view import BaseModelView
from starlette_admin import PasswordField
from starlette_admin.base import RequestAction
from starlette_admin.exceptions import ActionFailed, FormValidationError
from typing import Any
from pydantic_core import ValidationError

from ...models import UserModel, TeamModel
from ...schemas import UserBaseSchema, UserCreateSchema
from ...utils.errors import pydantic_errors_to_form_errors
from ...utils.db_errors import handle_integrity_error
from ...utils.passwd import get_password_hash
from sqlalchemy.exc import IntegrityError


class UserView(BaseModelView):
    fields = [
        "id",
        "email",
        "username",
        PasswordField(
            name="password",
            label="Password",
            required=True,
            exclude_from_list=True,
            exclude_from_edit=True,
            exclude_from_detail=True,
        ),
        PasswordField(
            name="repeat_password",
            label="Repeat Password",
            help_text="Reenter password",
            required=True,
            exclude_from_list=True,
            exclude_from_edit=True,
            exclude_from_detail=True,
        ),
        "full_name",
        "role",
        "is_active",
        "team",
        "meetings",
        "assigned_tasks",
        "created_at",
        "updated_at",
    ]
    label = "Users"

    exclude_fields_from_create = [
        # "meetings",
        "team",
        "assigned_tasks",
        "created_at",
        "updated_at",
    ]
    exclude_fields_from_edit = [
        "meetings",
        "team",
        "password",
        "repeat_password",
        "created_at",
        "updated_at",
    ]
    searchable_fields = [
        "id",
        "email",
        "username",
        "full_name",
        "role",
        "is_active",
        "team",
        "created_at",
        "updated_at",
    ]

    async def validate(self, request, data):
        try:
            match request.state.action:
                case RequestAction.CREATE:
                    UserCreateSchema(**data)
                case RequestAction.EDIT:
                    UserBaseSchema(**data)
        except ValidationError as err:
            errors = pydantic_errors_to_form_errors(err)
            raise FormValidationError(errors=errors)
        return await super().validate(request, data)

    async def before_create(
        self, request, data: dict[str, Any], user: UserModel
    ) -> None:
        user.hashed_password = get_password_hash(data.get("password"))

    async def delete(self, request: Request, pks: list) -> int:
        try:
            return await super().delete(request, pks)
        except IntegrityError as e:
            raise ActionFailed(handle_integrity_error(e))
