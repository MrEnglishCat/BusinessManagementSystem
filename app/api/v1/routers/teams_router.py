from fastapi import APIRouter, Path, Body, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.invite import InviteService
from ....config.response import ResponseFactory, BaseResponse
from ....config.db import get_async_session
from ....utils.enums_service import ServiceTypeEnum
from ....dependencies.service import get_service_dependency
from ....services import BaseService, InviteService
from ....schemas.teams import TeamBaseSchema, TeamLinkUserSchema

teams_router = APIRouter(prefix="/teams", tags=["Teams"])


@teams_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_teams(
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    teams = await team_service.get_all(session=session)
    return ResponseFactory.ok(data=teams)


@teams_router.get(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_team_by_id(
    team_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team = await team_service.get_one(session=session, id=team_id)
    if team:
        return ResponseFactory.ok(data=team)
    return ResponseFactory.error(message="Team is not found")


@teams_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=BaseResponse,
)
async def post_teams(
    team: TeamBaseSchema = Body(),
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team = await team_service.add(session=session, **team.model_dump())
    if team:
        return ResponseFactory.ok(data=team)
    return ResponseFactory.error()


@teams_router.delete(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_team_by_id(
    team_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team_count = await team_service.delete(session=session, id=team_id)
    if team_count:
        return ResponseFactory.ok(data=team_count)
    return ResponseFactory.error(message="Team is not found")


@teams_router.patch("/{team_id}")
async def patch_team_by_id(
    team: TeamBaseSchema,
    team_id: int = Path(),
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    update_team = await team_service.update(
        session=session, id=team_id, **team.model_dump()
    )
    if update_team:
        return ResponseFactory.ok(data=update_team)
    return ResponseFactory.error(message="Team is not found")


@teams_router.post(
    "/{invite_team_code}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def linking_to_command_by_code(
    linked_data: TeamLinkUserSchema,
    session: AsyncSession = Depends(get_async_session),
    invite_service: InviteService = Depends(
        get_service_dependency(ServiceTypeEnum.INVITE)
    ),
):
    invite_result = await invite_service.invite(
        session=session, linked_data=linked_data
    )

    if invite_result:
        return ResponseFactory.ok(data=uname.model_dump())
    return ResponseFactory.error(message="Linked data is not found")
