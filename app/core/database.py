from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings

_settings = Settings()
DATABASE_URL = _settings.DATABASE_URL

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def init_db() -> None:
    from app.core.orm_base import Base

    import app.modules.users.models  # noqa: F401
    import app.modules.requests.models  # noqa: F401
    import app.modules.lawyer_profiles.models  # noqa: F401
    import app.modules.offers.models  # noqa: F401
    import app.modules.deals.models  # noqa: F401
    import app.modules.chat.models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
