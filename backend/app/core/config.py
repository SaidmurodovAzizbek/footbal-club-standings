from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """FCS Application sozlamalari - .env fayldan yuklanadi."""

    # App
    APP_NAME: str = "FCS - Football Club Standings"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./fcs.db"
    SUPABASE_DB_URL: str | None = None

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    UPSTASH_REDIS_URL: str | None = None

    # Football-Data.org API
    FOOTBALL_API_KEY: str = "your_api_key_here"
    FOOTBALL_API_BASE_URL: str = "https://api.football-data.org/v4"

    # CORS
    CORS_ORIGINS: str = '["http://localhost:3000","http://localhost:5173"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """CORS origins ro'yxatini qaytaradi."""
        return json.loads(self.CORS_ORIGINS)

    # Rate Limiting
    RATE_LIMIT: str = "100/minute"

    # Sync Task Intervals (sekundlarda)
    STANDINGS_SYNC_INTERVAL: int = 3600  # 1 soat
    LIVE_MATCHES_SYNC_INTERVAL: int = 60  # 1 daqiqa

    # Media
    MEDIA_DIR: str = "media"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
        "extra": "ignore",  # Qoshimcha env qiymatlarini (.env dagi) inobatga olmaslik uchun
    }


settings = Settings()
