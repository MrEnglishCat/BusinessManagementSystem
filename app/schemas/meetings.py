from pydantic import BaseModel, Field
from datetime import datetime
from app.schemas.users import UserSchema
from app.schemas.teams import TeamSchema


class MeetingSchema(BaseModel):
    title: str
    description: str
    start_time: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "31.07.2026 23:23"}
    )
    end_time: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "01.08.2026 23:23"}
    )
    location: str
    created_by: UserSchema
    team_id: TeamSchema
    user_id: UserSchema
    created_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )


class MeetingResponseSchema(MeetingSchema, BaseModel):
    id: int
