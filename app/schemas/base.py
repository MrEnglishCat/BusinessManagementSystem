from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class BasePydanticModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class BaseDataTimePydanticModel(BasePydanticModel):
    created_at: datetime = Field(
        title="Created at", json_schema_extra={"example": "2026-05-29"}
    )
    updated_at: datetime = Field(
        title="Updated at", json_schema_extra={"example": "2026-05-29 23:23"}
    )
