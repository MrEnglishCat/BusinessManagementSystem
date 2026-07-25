from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime
from .base import BasePydanticModel, BaseDataTimePydanticModel
from ..utils.enums_service import MeetingStatusEmun


class MeetingIDSchema(BaseModel):
    id: int = Field(title="Meeting ID")


class MeetingCreateSchema(BasePydanticModel):

    title: str = Field(title="Title")
    description: str = Field(title="Description")
    start_time: datetime | None = Field(
        title="Start time", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    end_time: datetime | None = Field(
        title="End time", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    status: MeetingStatusEmun = Field(title="Meeting status")
    location: str = Field(title="Location")
    created_by: int = Field(title="Created by")
    team_id: int = Field(title="Team")
    participants: list["UserMeetingSchema"] = Field(
        default_factory=list,
        title="Participants",
    )


class MeetingBaseSchema(BasePydanticModel):
    title: str = Field(title="Title")
    description: str = Field(title="Description")
    start_time: datetime | None = Field(
        title="Start time", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    end_time: datetime | None = Field(
        title="End time", json_schema_extra={"example": "2026-05-29 23:23"}
    )
    status: MeetingStatusEmun = Field(title="Meeting status")
    cancellation_reason: str | None = Field(title="Canceletion reason")
    canceled_at: datetime | None = Field(title="Canceled at")
    canceled_by: int | None = Field(title="Canseceld_by")
    location: str = Field(title="Location")
    created_by: int = Field(title="Created by")
    team_id: int = Field(title="Team")
    participants: list["UserMeetingSchema"] | None = Field(
        default_factory=list,
        title="Participants",
    )


class MeetingResponseSchema(
    BaseDataTimePydanticModel,
    MeetingBaseSchema,
    MeetingIDSchema,
): ...


class MeetingCancelSchema(MeetingIDSchema):
    cancellation_reason: str | None = Field(title="Cancelation reason")
