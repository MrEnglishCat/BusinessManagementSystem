from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from ..base import BasePydanticModel
from ..users import UserResponseSchema
from ..teams import TeamResponseSchema
from ...utils.enums_service import TaskStatus
from pydantic import ConfigDict


class TaskIDSchema(BaseModel):
    id: int = Field(title="Task ID")

    model_config = ConfigDict(from_attributes=True)


class TaskBaseSchema(BasePydanticModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    deadline: datetime | None = Field(
        title="Deadline", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    team: TeamResponseSchema | None = Field(default=None, title="Team")
    assignee: UserResponseSchema | None = Field(default=None, title="Assignee")


class TaskCreateSchema(BasePydanticModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    deadline: datetime | None = Field(
        title="Deadline", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    team_id: int | None = Field(default=None, title="Team")
    assignee_id: int | None = Field(default=None, title="Assignee")


class TaskUpdateSchema(BasePydanticModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    status: TaskStatus = Field(title="Status")
    deadline: datetime | None = Field(
        title="Deadline", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    team_id: int | None = Field(default=None, title="Team")
    assignee_id: int | None = Field(default=None, title="Assignee")


class TaskCommentBaseSchema(BasePydanticModel):
    content: str = Field(title="Content")
    task_id: int = Field(title="Task")
    user_id: int = Field(title="User")


class TaskCommentCreateSchema(BasePydanticModel):
    content: str = Field(title="Content")
    task_id: int = Field(title="Task")
