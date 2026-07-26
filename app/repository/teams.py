from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from .base_repository import BaseRepository
from ..models import TeamModel, UserModel


class TeamRepository(BaseRepository):
    model = TeamModel

    async def get_members(self, session: AsyncSession, team_id: int):
        stmt = (
            select(self.model)
            .options(selectinload(self.model.members))
            .where(self.model.id == team_id)
        )
        result = await session.execute(stmt)
        return result.scalar()

    async def add_members(self, session: AsyncSession, team_id: int, members: list):
        team_result = await session.execute(
            select(TeamModel).where(TeamModel.id == team_id)
        )
        team = team_result.scalar_one_or_none()
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        users_result = await session.execute(
            select(UserModel).where(UserModel.username.in_(members.usernames))
        )
        users = users_result.scalars().all()

        if len(users) != len(members.usernames):
            found_usernames = {u.username for u in users}
            missing = set(members.usernames) - found_usernames
            raise HTTPException(
                status_code=404, detail=f"Пользователи не найдены: {', '.join(missing)}"
            )

        added_count = 0
        already_in_team = []
        in_other_team = []

        for user in users:
            if user.team_id == team_id:
                already_in_team.append(user.username)
            elif user.team_id is not None and user.team_id != team_id:
                in_other_team.append(user.username)
            else:
                user.team_id = team_id
                added_count += 1

        await session.commit()

        return True

    async def delete_members(self, session: AsyncSession, team_id: int, members: list):

        if not members:
            return False

        result = await session.execute(
            select(UserModel).where(
                UserModel.username.in_(members), UserModel.team_id == team_id
            )
        )
        users_to_remove = result.scalars().all()

        if not users_to_remove:
            return False

        for user in users_to_remove:
            user.team_id = None

        return True
