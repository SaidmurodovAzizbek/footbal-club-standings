from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db
from app.models.match import Match
from app.schemas.match import MatchResponse, MatchListResponse

router = APIRouter(prefix="/matches", tags=["Matches - O'yinlar"])


def _enrich_match(match: Match, schema_class):
    """Match ob'yektiga jamoa ma'lumotlarini qo'shish (relationship orqali)."""
    match_data = schema_class.model_validate(match)
    if match.home_team:
        match_data.home_team_name = match.home_team.name_en
        match_data.home_team_crest = match.home_team.crest_local or match.home_team.crest_url
    if match.away_team:
        match_data.away_team_name = match.away_team.name_en
        match_data.away_team_crest = match.away_team.crest_local or match.away_team.crest_url
    return match_data


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
    query = select(Match).options(
        selectinload(Match.home_team),
        selectinload(Match.away_team),
    )

    if league_id is not None:
        query = query.where(Match.league_id == league_id)
    if matchday is not None:
        query = query.where(Match.matchday == matchday)
    if status:
        query = query.where(Match.status == status.upper())

    query = query.order_by(desc(Match.utc_date)).offset(skip).limit(limit)

    result = await db.execute(query)
    matches = result.scalars().all()

    return [_enrich_match(m, MatchListResponse) for m in matches]


@router.get("/live", response_model=List[MatchResponse], summary="Jonli o'yinlar")
async def get_live_matches(
    db: AsyncSession = Depends(get_db),
):
    """
    Hozir o'ynalayotgan jonli o'yinlarni qaytaradi.
    """
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
        )
        .where(Match.status.in_(["IN_PLAY", "PAUSED"]))
    )
    result = await db.execute(query)
    matches = result.scalars().all()

    return [_enrich_match(m, MatchResponse) for m in matches]


@router.get("/{match_id}", response_model=MatchResponse, summary="O'yin tafsilotlari")
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    O'yin tafsilotlarini ID bo'yicha qaytaradi.
    """
    result = await db.execute(
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
        )
        .where(Match.id == match_id)
    )
    match = result.scalar_one_or_none()

    if not match:
        raise HTTPException(status_code=404, detail="O'yin topilmadi")

    return _enrich_match(match, MatchResponse)
