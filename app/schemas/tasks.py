from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from .base import BasePydanticModel, BaseDataTimePydanticModel


class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRES = "in_progres"
    COMPLETED = "completed"


class TaskIDSchema(BaseModel):
    id: int = Field(title="Task ID")


class TaskBaseSchema(BasePydanticModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    status: TaskStatus = Field(title="Status")
    deadline: datetime = Field(
        title="Deadline", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    created_by: int = Field(title="Createt by")
    assignee_id: int | None = Field(default=None, title="Assignee")
    team_id: int | None = Field(default=None, title="Team")


class TaskResponseSchema(TaskBaseSchema, TaskIDSchema):
    created_at: datetime = Field(
        title="Created at",
        json_schema_extra={"example": "2026-05-29 23:23"},
    )
    updated_at: datetime = Field(
        title="Updated at",
        json_schema_extra={"example": "2026-05-29 23:23"},
    )


class TaskCommentBaseSchema(BasePydanticModel):
    content: str = Field(title="Content")
    task_id: int = Field(title="Task")
    user_id: int = Field(title="User")


class TaskCommentResponseSchema(
    BaseDataTimePydanticModel,
    TaskCommentBaseSchema,
    TaskIDSchema,
): ...
