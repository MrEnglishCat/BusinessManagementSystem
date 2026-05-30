from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from .settings import settings

engine_db = create_async_engine(settings.DB_URL, echo=True)


AsyncSession = async_sessionmaker(
    bind=engine_db,
    class_=AsyncSession,
    expire_on_commit=False,  # Важно для async!
    autocommit=False,  # AsyncSession не поддерживает autocommit
    autoflush=False,  # Рекомендуется False для async
)


async def get_db():

    async with AsyncSession() as session:
        try:
            yield session
        except:
            yield session.rollback()
        finally:
            yield session.close()


class BaseAlchemyModel(DeclarativeBase): ...
