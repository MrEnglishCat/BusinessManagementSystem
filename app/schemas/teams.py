from datetime import datetime

from pydantic import BaseModel, Field, EmailStr


class TeamSchema(BaseModel):
    name: str
    description: str
    invite_code: str
    created_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )
    updated_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )


class TeamResponseScheme(TeamSchema, BaseModel):
    id: int
