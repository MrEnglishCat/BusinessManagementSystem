from datetime import datetime

from pydantic import BaseModel, Field, EmailStr

from app.schemas.teams import TeamResponseScheme
from enum import StrEnum
class UserRole(StrEnum):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

class UserSchema(BaseModel): 
    email:EmailStr
    username:str
    hased_password:str
    full_name:str
    role: UserRole
    is_active:bool
    team_id: TeamResponseScheme

    created_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )
    updated_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )



class UserResponseSchema(BaseModel):
    if:int