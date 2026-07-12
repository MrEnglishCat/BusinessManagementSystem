from starlette_admin.exceptions import FormValidationError
from starlette_admin import HasMany
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request
from typing import Any
from email_validator import validate_email, EmailSyntaxError
from .base_view import BaseModelView
from ...services import TeamService, BaseService
from ...dependencies.service import get_service
from ...config.db import get_async_session, async_session_maker
from ...utils.enums_service import ServiceTypeEnum
from ...models import TeamModel


class TeamView(BaseModelView):

    fields = [
        "id",
        "name",
        "description",
        "invite_code",
        "creator",
        "members",
        "meetings",
        "created_at",
        "updated_at",
    ]
    label = "Teams"

    searchable_fields = [
        "id",
        "name",
        "description",
        "invite_code",
        "created_by",
        "created_at",
        "updated_at",
    ]

    exclude_fields_from_edit = ["creator", "created_by", "created_at", "updated_at"]
    exclude_fields_from_create = ["creator", "created_by", "created_at", "updated_at"]

    async def before_create(
        self,
        request: Request,
        data: dict,
        team: TeamModel,
    ):
        team_service = get_service(ServiceTypeEnum.TEAM)
        invite_code = f"INV-{team.invite_code}"

        await self.check_constraint(
            invite_code=invite_code,
            team_service=team_service,
        )
        team.created_by = request.state.user.id
        team.invite_code = f"INV-{team.invite_code}"

    async def before_edit(
        self,
        request: Request,
        data: dict,
        team: TeamModel,
    ):
        if not team.invite_code.startswith("INV-"):
            team.invite_code = f"INV-{team.invite_code}"
        team_service = get_service(ServiceTypeEnum.TEAM)

        await self.check_constraint(
            invite_code=team.invite_code,
            team_service=team_service,
            exclude_self=True,
            team=team,
        )

    async def check_constraint(
        self,
        invite_code: str,
        team_service: TeamService,
        exclude_self: bool = False,
        team: TeamModel = None,
    ):
        async with async_session_maker() as session:
            if not exclude_self:
                team_db = await team_service.get_one(
                    session=session, invite_code=invite_code
                )
            else:
                team_db = [
                    item
                    for item in await team_service.get_all(session=session)
                    if item.invite_code == invite_code and item.name != team.name
                ]
                # Продолжить с обработки ошибки при добавлении или редактировании TeamModel  поля Ivite Code
            if team_db:
                raise FormValidationError(errors={"invite_code": "Code is dublicate"})
