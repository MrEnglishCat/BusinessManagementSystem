from datetime import datetime

from pydantic import BaseModel, Field


class TeamIDSchema(BaseModel):
    id: int = Field(title="Team")


class TeamBaseSchema(BaseModel):
    name: str = Field(title="Name")
    description: str = Field(title="Description")
    invite_code: str = Field(title="Invite code")
    created_by: int = Field(title="Created by")


class TeamResponseSchema(TeamBaseSchema, TeamIDSchema):
    created_at: datetime = Field(
        title="Created at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )
    updated_at: datetime = Field(
        title="Updated at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )
