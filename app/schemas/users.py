from datetime import datetime
from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    model_validator,
)
from app.models.users import UserRole
from app.utils.passwd import get_password_hash


class UserBaseSchema(BaseModel):
    email: EmailStr = Field(title="e-mail")
    username: str = Field(title="Username")
    full_name: str = Field(title="Full Name")
    role: UserRole = Field(title="User role")
    is_active: bool = Field(default=True, title="Active")
    team_id: int | None = Field(default=None, title="Team")


class UserIDSchema(BaseModel):
    id: int = Field(title="User ID")


class UserCreateSchema(UserBaseSchema):
    password: SecretStr = Field(
        title="Password",
    )
    repeat_password: SecretStr = Field(
        exclude=True,
        title="Repeat password",
    )

    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password.get_secret_value() != self.repeat_password.get_secret_value():
            raise ValueError("Passwords do not match")
        self.password = get_password_hash(self.password.get_secret_value())
        return self


class UserResponseSchema(
    UserBaseSchema,
    UserIDSchema,
):
    Field(default_factory=datetime)
    created_at: datetime = Field(
        title="Created at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )
    updated_at: datetime = Field(
        title="Updated at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )

    model_config = {"from_attributes": True}
