from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from ....config.db import get_async_session
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum
from ....services import BaseService
from ....config.response import BaseResponse, ResponseFactory

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar"])


@calendar_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_class=BaseResponse,
    response_model=BaseResponse,
)
async def get_all_events(
    session: AsyncSession = Depends(get_async_session),
    calendar_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.CALENDAR)
    ),
):
    return ResponseFactory.ok()
