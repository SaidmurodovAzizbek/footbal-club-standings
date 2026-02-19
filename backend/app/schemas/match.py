from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class MatchBase(BaseModel):
    """Match uchun asosiy maydonlar."""
    matchday: Optional[int] = None
    status: str = "SCHEDULED"
    utc_date: datetime
    home_team_id: int
    away_team_id: int


class MatchCreate(MatchBase):
    """Yangi o'yin yaratish uchun schema."""
    external_id: int
    league_id: int


class MatchUpdate(BaseModel):
    """O'yin yangilash uchun schema."""
    matchday: Optional[int] = None
    status: Optional[str] = None
    utc_date: Optional[datetime] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_ht: Optional[int] = None
    away_score_ht: Optional[int] = None
    stage: Optional[str] = None
    group_name: Optional[str] = None
    referee: Optional[str] = None
    duration: Optional[str] = None


class MatchResponse(BaseModel):
    """O'yin javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    league_id: int
    matchday: Optional[int] = None
    status: str
    utc_date: datetime
    home_team_id: int
    away_team_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    home_score_ht: Optional[int] = None
    away_score_ht: Optional[int] = None
    stage: Optional[str] = None
    group_name: Optional[str] = None
    referee: Optional[str] = None
    duration: Optional[str] = None

    # Qo'shimcha maydonlar (API dan qaytariladi)
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    home_team_crest: Optional[str] = None
    away_team_crest: Optional[str] = None


class MatchListResponse(BaseModel):
    """O'yinlar ro'yxati javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: int
    league_id: int
    matchday: Optional[int] = None
    status: str
    utc_date: datetime
    home_team_id: int
    away_team_id: int
    home_score: Optional[int] = None
    away_score: Optional[int] = None

    # Qo'shimcha: jamoa nomlari va crest
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    home_team_crest: Optional[str] = None
    away_team_crest: Optional[str] = None

