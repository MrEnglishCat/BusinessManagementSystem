from pydantic import BaseModel, Field
from enum import StrEnum
from datetime import datetime

from app.schemas.teams import TeamSchema
from app.schemas.users import UserSchema


class TaskStatus(StrEnum):
    OPEN = "open"
    IN_PROGRES = "in_progres"
    COMPLETED = "completed"


class TaskSchema(BaseModel):
    title: str
    description: str
    status: TaskStatus
    deadlite: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )
    created_by: UserSchema
    assignee_id: UserSchema
    team_id: TeamSchema
    created_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )
    updated_at: datetime = Field(
        default_factory=datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )


class TaskResponseSchema(TaskSchema, BaseModel):
    id: int
