from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseService
from ..schemas import TeamResponseSchema, UserResponseSchema


class TeamService(BaseService):

    async def get_all(self, session: AsyncSession):
        teams = await super().get_all(session)
        if teams:
            return [TeamResponseSchema.model_validate(team) for team in teams]
        return None

    async def get_one(
        self,
        session: AsyncSession,
        **filter_by,
    ):
        team = await super().get_one(session, **filter_by)
        if team:
            return TeamResponseSchema.model_validate(team)
        return None

    async def add(self, session: AsyncSession, **values):
        new_team = await super().add(session, **values)
        return TeamResponseSchema.model_validate(new_team)

    async def update(
        self,
        session: AsyncSession,
        id: int,
        **values,
    ):
        update_team = await super().update(session, id, **values)

        if update_team:
            return TeamResponseSchema.model_validate(update_team)
        return None

    async def get_members(self, session: AsyncSession, **filter_by):
        team = await self.repository.select_one(session=session, **filter_by)
        team_members = team.members
        if team_members:
            return [
                UserResponseSchema.model_validate(team_member)
                for team_member in team_members
            ]

        return None
