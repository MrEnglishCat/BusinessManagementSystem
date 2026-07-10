from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from app.models.users import UserRole
from app.utils.passwd import get_password_hash
from ..base import BasePydanticModel, BaseDataTimePydanticModel


class UserBaseSchema(BasePydanticModel):
    email: EmailStr = Field(title="e-mail")
    username: str = Field(title="Username")
    full_name: str = Field(title="Full Name")
    role: UserRole = Field(title="User role")
    is_active: bool = Field(default=True, title="Active")
    team_id: int | None = Field(default=None, title="Team")


class LoginSchema(BasePydanticModel):
    username: str
    password: SecretStr


class AfterAuthUserSchema(BasePydanticModel):
    password: SecretStr


class UserIDSchema(BaseModel):
    id: int = Field(title="User")


class UserCreateSchema(UserBaseSchema):
    is_verified: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    repeat_password: SecretStr = Field(
        exclude=True,
        title="Repeat password",
    )
    password: SecretStr = Field(
        title="Password",
        serialization_alias="hashed_password",
    )

    @field_validator("password", mode="after")
    def check_passwords_match(cls, value, info):
        if value.get_secret_value() != info.data["repeat_password"].get_secret_value():
            raise ValueError("Passwords do not match")
        return get_password_hash(value.get_secret_value())


class UserResponseSchema(
    BaseDataTimePydanticModel,
    UserBaseSchema,
    UserIDSchema,
): ...
