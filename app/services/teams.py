from .base import BaseService
from ..schemas.teams import TeamResponseSchema


class TeamService(BaseService):

    async def get_all(self, session):
        teams = await super().get_all(session)
        if teams:
            return [TeamResponseSchema.model_validate(team) for team in teams]
        return None

    async def get_one(self, session, **filter_by):
        team = await super().get_one(session, **filter_by)
        if team:
            return TeamResponseSchema.model_validate(team)
        return None

    async def add(self, session, **values):
        new_team = await super().add(session, **values)
        return TeamResponseSchema.model_validate(new_team)
