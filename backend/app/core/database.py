from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings


# Async SQLAlchemy engine
def get_database_url() -> str:
    """Return the currently configured Database URL. Enforce SQLite for this deployment."""
    return settings.DATABASE_URL

engine = create_async_engine(
    get_database_url(),
    echo=settings.DEBUG,
    future=True,
)

# Async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency - har bir request uchun yangi database session yaratadi.
    Request tugaganda session yopiladi.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
