from pydantic import BaseModel, Field
from datetime import datetime
from .base import BasePydanticModel, BaseDataTimePydanticModel


class EvaluationIDSchema(BaseModel):
    id: int = Field(title="Evaluation ID")


class EvaluationBaseSchema(BasePydanticModel):
    score: int = Field(title="Score", ge=1, le=5)
    comment: str = Field(title="Comment")
    employee_id: int = Field(
        title="Employee",
    )  # UserSchema
    reviewer_id: int = Field(title="Reviewer")  # UserSchema
    task_id: int = Field(title="Task")  # TaskSchema


class EvaluationResponseSchema(
    BaseDataTimePydanticModel,
    EvaluationBaseSchema,
    EvaluationIDSchema,
): ...
