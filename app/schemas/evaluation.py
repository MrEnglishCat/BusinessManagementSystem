from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime


class EvaluationSchema(BaseModel):
    score: int
    comment: str
    employee_id: int
    reviewer_id: int
    task_id: int
    created_at: datetime = Field(
        datetime, json_schema_extra={"example": "29.05.2026 23:23"}
    )

    model_config = ConfigDict()

    @field_validator("created_at", mode="before")
    def validate_created_at(cls, value):
        try:
            parse_value = datetime.strptime(value, "%d.%m.%Y %H:%M")
            return parse_value
        except ValueError, TypeError:
            raise ValueError("Error value datetime")


class EvaluationResponseSchema(EvaluationSchema, BaseModel):
    id: int
