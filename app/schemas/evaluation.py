from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime


class EvaluationIDSchema(BaseModel):
    id: int = Field(title="Evaluation ID")


class EvaluationBaseSchema(BaseModel):
    score: int = Field(title="Score")
    comment: str = Field(title="Comment")
    employee_id: int = Field(title="Employee ID")  # UserSchema
    reviewer_id: int = Field(title="Reviewer ID")  # UserSchema
    task_id: int = Field(title="Task ID")  # TaskSchema


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
