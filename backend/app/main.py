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
from app.api.v1.router import api_v1_router

# Logging sozlash
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle - startup va shutdown eventlar.
    """
    # === STARTUP ===
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} ishga tushmoqda...")
    logger.info(f"📌 Muhit: {settings.APP_ENV}")
    logger.info(f"📌 Database: {settings.DATABASE_URL[:30]}...")

    # Media papkasini yaratish
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "crests"), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "emblems"), exist_ok=True)
    os.makedirs(os.path.join(settings.MEDIA_DIR, "stadiums"), exist_ok=True)

    logger.info("✅ Server muvaffaqiyatli ishga tushdi!")

    yield

    # === SHUTDOWN ===
    logger.info("🛑 Server to'xtatilmoqda...")


# FastAPI app yaratish
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "FCS (Football Club Standings) - Futbol ligalari, turni jadvallar, "
        "jonli natijalar va klub tarixi uchun API. "
        "O'zbek va ingliz tillarida qo'llab-quvvatlanadi."
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

# Static files (media: logos, stadion rasmlari)
if os.path.exists(settings.MEDIA_DIR):
    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

# === ROUTES ===

# API v1 routerini ulash
app.include_router(api_v1_router)


# Salomlashish endpoint
@app.get("/", tags=["Root"])
async def root():
    """API salomlashish sahifasi."""
    return {
        "message": f"⚽ {settings.APP_NAME} ga xush kelibsiz!",
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
    """Server sog'ligi tekshiruvi."""
    return {"status": "healthy", "environment": settings.APP_ENV}
