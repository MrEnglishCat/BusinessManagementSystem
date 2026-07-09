from fastapi import APIRouter, status, Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession


from ....services import BaseService
from ....config.db import get_session
from ....config.response import BaseResponse, ResponseFactory
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum
from ....schemas import MeetingBaseSchema

meeting_router = APIRouter(prefix="/meetings", tags=["Meeting"])


@meeting_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_meetings(
    session: AsyncSession = Depends(get_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    meetings = await meeting_service.get_all(session=session)
    if meetings:
        return ResponseFactory.ok(data=meetings)
    return ResponseFactory.error(message="Meetings is not found")


@meeting_router.get(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_meetings_by_id(
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    meeting = await meeting_service.get_one(session=session, **{"id": meeting_id})
    if meeting:
        return ResponseFactory.ok(data=meeting)
    return ResponseFactory.error(message="Meeting is not found")


@meeting_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_meetings(
    meeting: MeetingBaseSchema = Body(),
    session: AsyncSession = Depends(get_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    new_meeting = await meeting_service.add(session=session, **meeting.model_dump())
    return new_meeting


@meeting_router.delete("/{meeting_id}")
async def delete_meetings_by_id(
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    delete_count = await meeting_service.delete(session=session, **{"id", meeting_id})
    if delete_count:
        return ResponseFactory.ok()
    return ResponseFactory.error(message="Meeting is not found")
