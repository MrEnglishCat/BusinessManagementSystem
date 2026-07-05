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

    async def get(self, session: AsyncSession, **filter_by):
        result = await self.repository.select(session=session, **filter_by)
        return result

    async def add(self, session: AsyncSession, **values):
        result = await self.repository.insert(session=session, **values)
        return result

    async def edit(self, session: AsyncSession, **values):
        result = await self.repository.update(session=session, **values)
        return result

    async def delete(self, session, **filter_by):
        result = await self.repository.delete(session=session, **filter_by)
        return result

    async def delete_all(self, session):
        result = await self.repository.delete_all(session=session)
        return result
