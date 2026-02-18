from pydantic import BaseModel, ConfigDict
from typing import Optional


class ClubBase(BaseModel):
    """Club uchun asosiy maydonlar."""
    name_en: str
    name_uz: Optional[str] = None
    short_name: Optional[str] = None
    tla: Optional[str] = None
    crest_url: Optional[str] = None
    founded: Optional[int] = None
    venue: Optional[str] = None
    website: Optional[str] = None
    club_colors: Optional[str] = None


class ClubCreate(ClubBase):
    """Yangi klub yaratish uchun schema."""
    external_id: int
    league_id: int


class ClubUpdate(BaseModel):
    """Klub yangilash uchun schema."""
    name_en: Optional[str] = None
    name_uz: Optional[str] = None
    short_name: Optional[str] = None
    tla: Optional[str] = None
    crest_url: Optional[str] = None
    crest_local: Optional[str] = None
    founded: Optional[int] = None
    venue: Optional[str] = None
    venue_image_local: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    wiki_summary_en: Optional[str] = None
    wiki_summary_uz: Optional[str] = None
    club_colors: Optional[str] = None


class ClubResponse(ClubBase):
    """Klub javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    league_id: int
    crest_local: Optional[str] = None
    venue_image_local: Optional[str] = None
    address: Optional[str] = None
    wiki_summary_en: Optional[str] = None
    wiki_summary_uz: Optional[str] = None


class ClubListResponse(BaseModel):
    """Klublar ro'yxati javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    league_id: int
    name_en: str
    name_uz: Optional[str] = None
    short_name: Optional[str] = None
    tla: Optional[str] = None
    crest_local: Optional[str] = None
