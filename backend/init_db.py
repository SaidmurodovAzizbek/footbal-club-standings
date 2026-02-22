import logging
from sqlalchemy import create_engine
from app.models.base import Base

# Import all models to ensure they are registered with Base.metadata
from app.models import League, Club, Match, Standing

from app.core.database import get_database_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    # Parolni sirtdan yuklaymiz (hech qachon hardcode qilinmaydi)
    db_url = get_database_url()
    
    # aiosqlite or PostgreSQL+asyncpg driver used dynamically, 
    # but create_engine requires sync driver so we adjust just for this script if it's postgres
    if db_url and db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql+asyncpg://", "postgresql://", 1)
        
    logger.info(f"Connecting to database: {db_url[:30]}...")
    
    # Create an isolated synchronous engine for this script
    engine = create_engine(db_url, echo=True)
    
    try:
        logger.info("Connecting to database and creating tables...")
        # Create all tables synchronously
        Base.metadata.create_all(bind=engine)
        logger.info("Successfully created all database tables!")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
    finally:
        engine.dispose()

if __name__ == "__main__":
    init_db()
