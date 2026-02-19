from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional

from app.api.deps import get_db
from app.models.match import Match
from app.models.club import Club
from app.schemas.match import MatchResponse, MatchListResponse

router = APIRouter(prefix="/matches", tags=["Matches - O'yinlar"])


@router.get("/", response_model=List[MatchListResponse], summary="O'yinlar ro'yxati")
async def get_matches(
    league_id: Optional[int] = Query(None, description="Liga bo'yicha filtrlash"),
    matchday: Optional[int] = Query(None, description="O'yin kuni raqami"),
    status: Optional[str] = Query(None, description="O'yin holati: SCHEDULED, IN_PLAY, FINISHED"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    O'yinlar ro'yxatini qaytaradi.
    - **league_id**: Liga bo'yicha filtrlash
    - **matchday**: O'yin kuni raqami
    - **status**: O'yin holati bo'yicha filtrlash
    """
    query = select(Match)

    if league_id is not None:
        query = query.where(Match.league_id == league_id)
    if matchday is not None:
        query = query.where(Match.matchday == matchday)
    if status:
        query = query.where(Match.status == status.upper())

    query = query.order_by(desc(Match.utc_date)).offset(skip).limit(limit)

    result = await db.execute(query)
    matches = result.scalars().all()

    # Har bir o'yinga jamoa nomlarini qo'shish
    enriched = []
    for match in matches:
        match_data = MatchListResponse.model_validate(match)

        home = await db.execute(select(Club).where(Club.id == match.home_team_id))
        home_club = home.scalar_one_or_none()
        if home_club:
            match_data.home_team_name = home_club.name_en
            match_data.home_team_crest = home_club.crest_local or home_club.crest_url

        away = await db.execute(select(Club).where(Club.id == match.away_team_id))
        away_club = away.scalar_one_or_none()
        if away_club:
            match_data.away_team_name = away_club.name_en
            match_data.away_team_crest = away_club.crest_local or away_club.crest_url

        enriched.append(match_data)

    return enriched


@router.get("/live", response_model=List[MatchResponse], summary="Jonli o'yinlar")
async def get_live_matches(
    db: AsyncSession = Depends(get_db),
):
    """
    Hozir o'ynalayotgan jonli o'yinlarni qaytaradi.
    """
    query = select(Match).where(Match.status.in_(["IN_PLAY", "PAUSED"]))
    result = await db.execute(query)
    matches = result.scalars().all()

    # Har bir o'yinga jamoa ma'lumotlarini qo'shish
    enriched = []
    for match in matches:
        match_data = MatchResponse.model_validate(match)

        # Home team
        home = await db.execute(select(Club).where(Club.id == match.home_team_id))
        home_club = home.scalar_one_or_none()
        if home_club:
            match_data.home_team_name = home_club.name_en
            match_data.home_team_crest = home_club.crest_local or home_club.crest_url

        # Away team
        away = await db.execute(select(Club).where(Club.id == match.away_team_id))
        away_club = away.scalar_one_or_none()
        if away_club:
            match_data.away_team_name = away_club.name_en
            match_data.away_team_crest = away_club.crest_local or away_club.crest_url

        enriched.append(match_data)

    return enriched


@router.get("/{match_id}", response_model=MatchResponse, summary="O'yin tafsilotlari")
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    O'yin tafsilotlarini ID bo'yicha qaytaradi.
    """
    result = await db.execute(select(Match).where(Match.id == match_id))
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="O'yin topilmadi")

    match_data = MatchResponse.model_validate(match)

    # Jamoa ma'lumotlarini qo'shish
    home = await db.execute(select(Club).where(Club.id == match.home_team_id))
    home_club = home.scalar_one_or_none()
    if home_club:
        match_data.home_team_name = home_club.name_en
        match_data.home_team_crest = home_club.crest_local or home_club.crest_url

    away = await db.execute(select(Club).where(Club.id == match.away_team_id))
    away_club = away.scalar_one_or_none()
    if away_club:
        match_data.away_team_name = away_club.name_en
        match_data.away_team_crest = away_club.crest_local or away_club.crest_url

    return match_data
