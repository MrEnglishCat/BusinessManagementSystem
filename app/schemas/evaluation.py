from pydantic import BaseModel, Field
from datetime import datetime
from .base import BasePydanticModel


class EvaluationIDSchema(BaseModel):
    id: int = Field(title="Evaluation ID")


class EvaluationBaseSchema(BasePydanticModel):
    score: int = Field(title="Score")
    comment: str = Field(title="Comment")
    employee_id: int = Field(title="Employee")  # UserSchema
    reviewer_id: int = Field(title="Reviewer")  # UserSchema
    task_id: int = Field(title="Task")  # TaskSchema


class EvaluationResponseSchema(
    EvaluationBaseSchema,
    EvaluationIDSchema,
):
    created_at: datetime = Field(
        title="Created at", json_schema_extra={"example": "29.05.2026 23:23"}
    )
    updated_at: datetime = Field(
        title="Updated at", json_schema_extra={"example": "29.05.2026 23:23"}
    )
