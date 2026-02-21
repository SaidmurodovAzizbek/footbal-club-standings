from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging
import os

from app.core.config import settings
from app.core.security import limiter
from app.core.scheduler import create_scheduler
from app.api.v1.router import api_v1_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle - startup and shutdown events.
    """
    # === STARTUP ===
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}...")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Database: {settings.DATABASE_URL[:30]}...")

    # Create media directories
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "crests"), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "emblems"), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "stadiums"), exist_ok=True)

    # Initialize scheduler
    scheduler = create_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    logger.info("APScheduler started successfully.")

    logger.info("Server started successfully.")

    yield

    # === SHUTDOWN ===
    logger.info("Stopping server...")
    if hasattr(app.state, "scheduler"):
        app.state.scheduler.shutdown()
        logger.info("APScheduler stopped.")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "FCS (Football Club Standings) - API for football leagues, standings, "
        "live scores, and club history. "
        "Supported in English and Uzbek."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# === MIDDLEWARE ===

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Static files (media: logos, stadium images)
if os.path.exists(settings.MEDIA_DIR):
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# === ROUTES ===

# Mount API v1 router
app.include_router(api_v1_router)


# Welcome endpoint
@app.get("/", tags=["Root"])
async def root():
    """API welcome page."""
    return {
        "message": f"Welcome to {settings.APP_NAME}!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "leagues": "/api/v1/leagues",
            "clubs": "/api/v1/clubs",
            "matches": "/api/v1/matches",
            "live_matches": "/api/v1/matches/live",
            "standings": "/api/v1/standings/league/{league_id}",
        },
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Server health check."""
    return {"status": "healthy", "environment": settings.APP_ENV}


@app.post("/api/v1/sync", tags=["Sync"])
async def trigger_sync(
    league_codes: list[str] | None = None,
):
    """
    Synchronize data from Football-Data.org.
    If league_codes is not provided in the body, all supported leagues will be synchronized.
    """
    from app.services.football_data import football_data_service

    stats = await football_data_service.sync_all(league_codes)
    return {
        "message": "Synchronization complete.",
        "stats": stats,
    }
