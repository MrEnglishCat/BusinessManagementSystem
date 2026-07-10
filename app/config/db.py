from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from .settings import settings
from .response import ResponseFactory

async_engine_db = create_async_engine(settings.BMS_DB_URL, echo=True)

async_session_maker = async_sessionmaker(
    bind=async_engine_db,
    class_=AsyncSession,
    expire_on_commit=False,  # Важно для async!
    autocommit=False,  # AsyncSession не поддерживает autocommit
    autoflush=False,  # Рекомендуется False для async
)


async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session

        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()


class BaseAlchemyModel(DeclarativeBase): ...
