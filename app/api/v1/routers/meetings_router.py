from fastapi import APIRouter, status, Depends, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession


from ....services import BaseService
from ....config.db import get_async_session
from ....config.response import BaseResponse, ResponseFactory
from ....dependencies.service import get_service_dependency
from ....utils.enums_service import ServiceTypeEnum
from ....schemas import (
    MeetingCancelSchema,
    MeetingCreateSchema,
    MeetingUpdateSchema,
    MeetingParticipantUpdateSchema,
)
from ....models import UserModel
from ....auth.config import current_active_user

meeting_router = APIRouter(prefix="/meetings", tags=["Meeting"])


@meeting_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_meetings(
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    meetings = await meeting_service.get_all(
        session=session,
    )
    if meetings:
        return ResponseFactory.ok(data=meetings)
    return ResponseFactory.error(message="Meetings is not found")


@meeting_router.get(
    "/canceled",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_all_canceled(
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    meetings = await meeting_service.get_all_canceled(
        session=session,
    )
    if meetings:
        return ResponseFactory.ok(data=meetings)
    return ResponseFactory.error(message="Meetings is not found")


@meeting_router.get(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_meeting_by_id(
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    meeting = await meeting_service.get_one(session=session, id=meeting_id)
    if meeting:
        return ResponseFactory.ok(data=meeting)
    return ResponseFactory.error(message="Meeting is not found")


@meeting_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_meetings(
    meeting: MeetingCreateSchema = Body(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
    current_user: UserModel = Depends(current_active_user),
):

    new_meeting = await meeting_service.add(
        session=session, meeting_create_schema=meeting, current_user=current_user
    )
    return ResponseFactory.ok(message=f"Meeting {new_meeting.title} is created")


@meeting_router.delete(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_meeting_by_id(
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    delete_count = await meeting_service.delete(session=session, id=meeting_id)
    if delete_count:
        return ResponseFactory.ok()
    return ResponseFactory.error(message="Meeting is not found")


@meeting_router.patch(
    "/cancel",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def cancel_meeting(
    meeting_input: MeetingCancelSchema = Body(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
    current_user: UserModel = Depends(current_active_user),
):
    meeting = await meeting_service.cancel_meeting(
        session=session, meeting=meeting_input, current_user=current_user
    )
    if meeting:
        return ResponseFactory.ok(data=meeting)
    return ResponseFactory.error(message="Meeting is not found")


@meeting_router.post(
    "/{meeting_id}/add_participants",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def add_team_partipitians(
    participants_schema: MeetingParticipantUpdateSchema = Body(),
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    update_meeting = await meeting_service.add_participants(
        session=session,
        meeting_id=meeting_id,
        participants_schema=participants_schema,
    )
    if update_meeting:
        return ResponseFactory.ok(message="Participants is success add")
    return ResponseFactory.error(message="Participants is not found")


@meeting_router.delete(
    "/{meeting_id}/participants",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_team_partipitians(
    participants_schema: MeetingParticipantUpdateSchema = Body(),
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):
    result = await meeting_service.delete_participants(
        session=session,
        meeting_id=meeting_id,
        participants_schema=participants_schema,
    )
    if result:
        return ResponseFactory.ok(message="Participants is delete")
    return ResponseFactory.error(message="Participants is not found")


@meeting_router.patch(
    "/{meeting_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def patch_team_by_id(
    meeting: MeetingUpdateSchema,
    meeting_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    meeting_service: BaseService = Depends(
        get_service_dependency(ServiceTypeEnum.MEETING)
    ),
):

    update_meeting = await meeting_service.update(
        session=session, id=meeting_id, **meeting.model_dump()
    )
    if update_meeting:
        return ResponseFactory.ok(message="Meeting is success canceled")
    return ResponseFactory.error(message="Meeting is not found")
