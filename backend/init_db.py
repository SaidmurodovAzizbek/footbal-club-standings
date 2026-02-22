import logging
from sqlalchemy import create_engine
from app.models.base import Base

# Import all models to ensure they are registered with Base.metadata
from app.models import League, Club, Match, Standing

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    # URL encode the "@" inside the password so SQLAlchemy doesn't think the host starts at '0514'
    db_url = "postgresql://postgres:FCSPASSWORDSTRONG%400514@db.qanhmbzzauwowtyhnpfj.supabase.co:5432/postgres"
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
