from pydantic import BaseModel, ConfigDict
from typing import Optional


class StandingBase(BaseModel):
    """Standing uchun asosiy maydonlar."""
    season: int
    matchday: Optional[int] = None
    position: int
    played: int = 0
    won: int = 0
    draw: int = 0
    lost: int = 0
    goals_for: int = 0
    goals_against: int = 0
    goal_difference: int = 0
    points: int = 0
    form: Optional[str] = None


class StandingCreate(StandingBase):
    """Yangi standing yaratish uchun schema."""
    league_id: int
    club_id: int


class StandingUpdate(BaseModel):
    """Standing yangilash uchun schema."""
    matchday: Optional[int] = None
    position: Optional[int] = None
    played: Optional[int] = None
    won: Optional[int] = None
    draw: Optional[int] = None
    lost: Optional[int] = None
    goals_for: Optional[int] = None
    goals_against: Optional[int] = None
    goal_difference: Optional[int] = None
    points: Optional[int] = None
    form: Optional[str] = None


class StandingResponse(StandingBase):
    """Standing javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    league_id: int
    club_id: int

    # Qo'shimcha maydonlar (API dan)
    club_name: Optional[str] = None
    club_crest: Optional[str] = None


class StandingListResponse(BaseModel):
    """Standinglar ro'yxati javob schemasi."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    league_id: int
    club_id: int
    position: int
    played: int
    won: int
    draw: int
    lost: int
    goals_for: int
    goals_against: int
    goal_difference: int
    points: int
    form: Optional[str] = None
