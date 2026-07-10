from fastapi_users import schemas
from datetime import datetime
from app.models.users import UserRole


class UserRead(schemas.BaseUser[int]):
    id: int
    email: str
    username: str
    full_name: str | None = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    team_id: int | None = None
    created_at: datetime
    updated_at: datetime


class UserCreate(schemas.BaseUserCreate):
    username: str
    full_name: str | None = None
    role: UserRole = UserRole.USER
    team_id: int | None = None
