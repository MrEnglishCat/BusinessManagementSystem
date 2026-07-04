from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

from app.schemas.teams import TeamIDSchema
from app.schemas.users import UserIDSchema


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRES = "in_progres"
    COMPLETED = "completed"


class TaskIDSchema(BaseModel):
    id: int = Field(title="Task ID")


class TaskBaseSchema(BaseModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    status: TaskStatus = Field(title="Status")
    deadline: datetime = Field(
        title="Deadline", json_schema_extra={"example": "29.05.2026 23:23"}
    )
    created_by: int = Field(title="Createt by")
    assignee_id: int = Field(title="Assignee")
    team_id: int = Field(title="Team ID")


class TaskResponseSchema(TaskBaseSchema, TaskIDSchema):
    created_at: datetime = Field(
        title="Created at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )
    updated_at: datetime = Field(
        title="Updated at",
        json_schema_extra={"example": "29.05.2026 23:23"},
    )
