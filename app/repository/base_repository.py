from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    model = None

    async def insert(self, session: AsyncSession, **values): ...

    async def select(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).where(**filter_by)
        search_result = await session.execute(stmt)

        return search_result

    async def select_one(self, session: AsyncSession, model_id: int):
        stmt = select(self.model).where(self.model.id == model_id)
        search_result = await session.execute(stmt)
        return search_result

    async def update(self, session: AsyncSession, **values): ...

    async def delete(self, session: AsyncSession, **filter_by):
        stmt = delete(self.model).where(**filter_by)
        result = await session.execute(stmt)
        return result

    async def delete_one(self, session: AsyncSession, model_id: int):
        stmt = delete(self.model).where(self.model.id == model_id)
        result = await session.execute(stmt)
        return result
