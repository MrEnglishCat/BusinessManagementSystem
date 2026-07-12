from ..config.response import ResponseFactory
from ..schemas.teams import TeamLinkUserSchema
from ..repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class InviteService:
    def __init__(self, repositories: tuple[BaseRepository, BaseRepository]):
        user_repositoty, team_repository = repositories
        self.user_repositoty = user_repositoty()
        self.team_repository = team_repository()

    async def invite(self, session: AsyncSession, linked_data: TeamLinkUserSchema):
        model_invite_code = await self.team_repository.select_one(
            session=session, invite_code=linked_data.invite_code
        )
        user = await self.user_repositoty.select_one(
            session=session, username=linked_data.username
        )

        if user:
            if user.team_id:
                return ResponseFactory.error(
                    message="The user is already linked by code"
                )
            user.team_id = model_invite_code.id
