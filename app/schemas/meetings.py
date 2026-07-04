from pydantic import BaseModel, Field
from datetime import datetime


class MeetingIDSchema(BaseModel):
    id: int = Field(title="Meeting ID")


class MeetingBaseSchema(BaseModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    start_time: datetime = Field(
        title="Start time", json_schema_extra={"example": "31.07.2026 23:23"}
    )
    end_time: datetime = Field(
        title="End time", json_schema_extra={"example": "01.08.2026 23:23"}
    )
    location: str = Field(title="Location")
    created_by: int = Field(title="Created by")
    team_id: int = Field(title="Team")


class MeetingResponseSchema(MeetingBaseSchema, MeetingIDSchema):
    created_at: datetime = Field(
        title="Created at", json_schema_extra={"example": "29.05.2026 23:23"}
    )
    updated_at: datetime = Field(
        title="Updated at", json_schema_extra={"example": "29.05.2026 23:23"}
    )
