from fastapi import Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.db import get_session


class BaseRepository:
    model = None

    def generate_conditions(self, **filter_by):
        return [
            getattr(
                self.model,
                key,
            )
            == value
            for key, value in filter_by.items()
        ]

    async def insert(self, session: AsyncSession, **values):
        stmt = insert(self.model).values(**values)
        insert_result = await session.execute(stmt)
        return insert_result.scalar_one_or_none()

    async def select(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        search_result = await session.execute(stmt)
        return search_result.scalars().all()

    async def select_one(self, session: AsyncSession, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        search_result = await session.execute(stmt)
        return search_result.scalar()

    async def update(self, session: AsyncSession, **values): ...

    async def delete(self, session: AsyncSession, **filter_by):
        stmt = delete(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.rowcount

    async def delete_all(self, session):
        stmt = delete(self.model)
        result = await session.execute(stmt)
        return result.rowcount

    async def delete_one(self, session: AsyncSession, model_id: int):
        stmt = delete(self.model).where(self.model.id == model_id)
        result = await session.execute(stmt)
        return result.rowcount
