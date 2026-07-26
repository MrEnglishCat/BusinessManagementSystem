from fastapi import APIRouter, Path, Body, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.invite import InviteService
from ....config.response import ResponseFactory, BaseResponse
from ....config.db import get_async_session
from ....utils.enums_service import ServiceTypeEnum, UserRole
from ....dependencies.service import get_service_dependency
from ....services import BaseService, InviteService
from ....schemas import (
    TeamBaseSchema,
    TeamLinkUserSchema,
    AddMembersPayload,
    DeleteMembersPayload,
)
from ....models import UserModel
from ....auth.config import current_active_user

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
async def add_teams(
    team: TeamBaseSchema = Body(),
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
    current_user: UserModel = Depends(current_active_user),
):

    if current_user.role != UserRole.ADMIN:
        return ResponseFactory.error(
            message="Only an administrator can create commands"
        )
    if not team.invite_code.startswith("INV-"):
        team.invite_code = f"INV-{team.invite_code}"
    team_dump = team.model_dump()
    team_dump["created_by"] = current_user.id
    team = await team_service.add(session=session, **team_dump)

    if team:
        return ResponseFactory.ok(message="Team is crete")
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


@teams_router.patch(
    "/{team_id}",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
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
    "/invite_user",
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
    invite_result = (
        await invite_service.invite(  # !!!!!!!!!! доделать привязку к команде
            session=session, linked_data=linked_data
        )
    )

    if invite_result:
        return ResponseFactory.ok(data=invite_result)
    return ResponseFactory.error(message="Linked data is not found")


@teams_router.get(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def get_teams_memebers(
    team_id: int,
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team_members = await team_service.get_members(session=session, team_id=team_id)
    if team_members:
        return ResponseFactory.ok(data=team_members)
    return ResponseFactory.error(message="Team members is not found")


@teams_router.post(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def add_teams_memebers(
    team_id: int,
    members: AddMembersPayload,
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team_members = await team_service.add_members(
        session=session, team_id=team_id, members=members
    )
    if team_members:
        return ResponseFactory.ok(message="Team members is add")
    return ResponseFactory.error(message="Team members is not found")


@teams_router.delete(
    "/{team_id}/members",
    status_code=status.HTTP_200_OK,
    response_model=BaseResponse,
)
async def delete_teams_members(
    team_id: int,
    members: DeleteMembersPayload,
    session: AsyncSession = Depends(get_async_session),
    team_service: BaseService = Depends(get_service_dependency(ServiceTypeEnum.TEAM)),
):
    team = await team_service.get_one(session=session, **{"id": team_id})
    if not team:
        return ResponseFactory.error(message="Team is not found")

    success = await team_service.delete_members(
        session=session, team_id=team_id, members=members.usernames
    )

    if success:
        return ResponseFactory.ok(message=f"Members is delete")

    return ResponseFactory.error(message="Members is not found in team")
