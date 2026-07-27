from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from .base_repository import BaseRepository
from ..models import TaskModel, TaskCommentModel


class TaskRepository(BaseRepository):
    model = TaskModel

    async def get_all(self, session: AsyncSession):
        stmt = select(self.model).options(
            selectinload(self.model.team),
            selectinload(self.model.assignee),
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def select_one(self, session: AsyncSession, **filter_by):
        stmt = (
            select(self.model)
            .options(
                selectinload(self.model.team),
                selectinload(self.model.assignee),
            )
            .filter_by(**filter_by)
        )
        search_result = await session.execute(stmt)
        return search_result.scalar_one_or_none()


class TaskCommentRepository(BaseRepository):
    model = TaskCommentModel
