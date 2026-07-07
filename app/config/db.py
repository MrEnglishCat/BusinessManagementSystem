from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .settings import settings

async_engine_db = create_async_engine(settings.BMS_DB_URL, echo=True)

AsyncSession = async_sessionmaker(
    bind=async_engine_db,
    class_=AsyncSession,
    expire_on_commit=False,  # Важно для async!
    autocommit=False,  # AsyncSession не поддерживает autocommit
    autoflush=False,  # Рекомендуется False для async
)


async def get_session():
    async with AsyncSession() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()


class BaseAlchemyModel(DeclarativeBase): ...
