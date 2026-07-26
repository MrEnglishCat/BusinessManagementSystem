from ...utils.enums_service import TaskStatus
from datetime import datetime
from pydantic import Field
from .base import TaskBaseSchema, TaskIDSchema, TaskCommentBaseSchema
from ..base import BaseDataTimePydanticModel


class TaskResponseSchema(TaskBaseSchema, TaskIDSchema):
    status: TaskStatus
    created_at: datetime = Field(
        title="Created at",
        json_schema_extra={"example": "2026-05-29 23:23"},
    )
    updated_at: datetime = Field(
        title="Updated at",
        json_schema_extra={"example": "2026-05-29 23:23"},
    )


class TaskCommentResponseSchema(
    BaseDataTimePydanticModel,
    TaskCommentBaseSchema,
    TaskIDSchema,
): ...
