from abc import ABC, abstractmethod

from fastapi import Depends
from app.config.db import get_session
from app.repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.tasks import TaskCommentResponseSchema


class BaseService(ABC):

    def __init__(
        self,
        repository: BaseRepository,
    ):
        self.repository = repository

    async def get_one(self, session: AsyncSession, **filter_by):
        result = await self.repository.select_one(session=session, **filter_by)
        return result

    async def get_all(self, session: AsyncSession):
        result = await self.repository.select(session=session)
        return result

    async def add(self, session: AsyncSession, **values):
        result = await self.repository.insert(session=session, **values)
        return result

    async def edit(self, session: AsyncSession, **values):
        result = await self.repository.update(session=session, **values)
        return result

    async def delete(self, session: AsyncSession, **filter_by):
        result = await self.repository.delete(session=session, **filter_by)
        return result

    async def delete_all(self, session: AsyncSession):
        result = await self.repository.delete_all(session=session)
        return result

    async def update(self, session: AsyncSession, id: int, **values):
        result = await self.repository.update(session=session, id=id, **values)
        return result
