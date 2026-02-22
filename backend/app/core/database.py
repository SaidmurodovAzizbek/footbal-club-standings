from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings


# Async SQLAlchemy engine
def get_database_url() -> str:
    """Supabase DB URL bo'lsa, moslashtirib qaytaradi (asyncpg + port pooling 6543)"""
    if settings.SUPABASE_DB_URL:
        db_url = settings.SUPABASE_DB_URL
        # Ensure it uses the asyncpg driver
        if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
            db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
            db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        # Pooling port: 6543 (transaction pooling)
        if ":5432" in db_url:
             db_url = db_url.replace(":5432", ":6543", 1)
        return db_url
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
