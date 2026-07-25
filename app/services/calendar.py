from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from ..schemas import (
    UserResponseSchema,
    MeetingResponseSchema,
    EvaluationResponseSchema,
)


class CalendarService(BaseService): ...
