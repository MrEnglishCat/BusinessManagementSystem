from abc import ABC

from app.repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService(ABC):

    def __init__(
        self,
        repository: BaseRepository,
    ):
        self._repository = repository

    async def get_one(self, session: AsyncSession, **filter_by):
        result = await self._repository.select_one(session=session, **filter_by)
        return result

    async def get_all(self, session: AsyncSession):
        result = await self._repository.select(session=session)
        return result

    async def add(self, session: AsyncSession, **values):
        result = await self._repository.insert(session=session, **values)
        return result

    async def edit(self, session: AsyncSession, **values):
        result = await self._repository.update(session=session, **values)
        return result

    async def delete(self, session: AsyncSession, **filter_by):
        result = await self._repository.delete(session=session, **filter_by)
        return result

    async def delete_all(self, session: AsyncSession, **filter_by):
        result = await self._repository.delete_all(session=session, **filter_by)
        return result

    async def update(self, session: AsyncSession, id: int, **values):
        result = await self._repository.update(session=session, id=id, **values)
        return result
