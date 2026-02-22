from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import date


class LeagueBase(BaseModel):
    """League uchun asosiy maydonlar."""
    name_en: str
    name_uz: Optional[str] = None
    code: str
    country: str
    emblem_url: Optional[str] = None
    season_start: Optional[date] = None
    season_end: Optional[date] = None
    is_active: bool = True


class LeagueCreate(LeagueBase):
    """Yangi liga yaratish uchun schema."""
    external_id: int


class LeagueUpdate(BaseModel):
    """Liga yangilash uchun schema - barcha maydonlar ixtiyoriy."""
    name_en: Optional[str] = None
    name_uz: Optional[str] = None
    code: Optional[str] = None
    country: Optional[str] = None
    emblem_url: Optional[str] = None
    emblem_local: Optional[str] = None
    season_start: Optional[date] = None
    season_end: Optional[date] = None
    current_matchday: Optional[int] = None
    is_active: Optional[bool] = None


class LeagueResponse(LeagueBase):
    """Liga javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    name: Optional[str] = None  # Lokalizatsiya qilingan nom
    emblem_local: Optional[str] = None
    current_matchday: Optional[int] = None


class LeagueListResponse(BaseModel):
    """Ligalar ro'yxati javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    name_en: str
    name_uz: Optional[str] = None
    code: str
    country: str
    emblem_local: Optional[str] = None
    is_active: bool
    current_matchday: Optional[int] = None
