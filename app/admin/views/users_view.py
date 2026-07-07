from .base_view import BaseModelView
from starlette_admin import PasswordField
from starlette_admin.base import RequestAction
from starlette_admin.exceptions import FormValidationError
from typing import Any
from pydantic_core import ValidationError
from app.models import UserModel
from app.schemas.users import UserBaseSchema, UserCreateSchema
from app.utils.errors import pydantic_errors_to_form_errors
from app.utils.passwd import get_password_hash


class UserView(BaseModelView):
    fields = [
        "id",
        "email",
        "username",
        PasswordField(
            name="password",
            label="password",
            required=True,
            exclude_from_list=True,
            exclude_from_edit=True,
            exclude_from_detail=True,
        ),
        PasswordField(
            name="repeat_password",
            label="repeat_password",
            required=True,
            exclude_from_list=True,
            exclude_from_edit=True,
            exclude_from_detail=True,
        ),
        "full_name",
        "role",
        "is_active",
        "team",
        "created_at",
        "updated_at",
    ]
    label = "Users"

    exclude_fields_from_edit = [
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
        user.password = get_password_hash(user.password)
