from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db
from app.models.match import Match
from app.schemas.match import MatchResponse, MatchListResponse

router = APIRouter(prefix="/matches", tags=["Matches"])


def _enrich_match(match: Match, schema_class):
    """Enrich Match object with team data (via relationship)."""
    match_data = schema_class.model_validate(match)
    if match.home_team:
        match_data.home_team_name = match.home_team.name_en
        match_data.home_team_crest = match.home_team.crest_local or match.home_team.crest_url
    if match.away_team:
        match_data.away_team_name = match.away_team.name_en
        match_data.away_team_crest = match.away_team.crest_local or match.away_team.crest_url
    return match_data


@router.get("/", response_model=List[MatchListResponse], summary="List of matches")
async def get_matches(
    league_id: Optional[int] = Query(None, description="Filter by league"),
    matchday: Optional[int] = Query(None, description="Matchday number"),
    status: Optional[str] = Query(None, description="Filter by match status: SCHEDULED, IN_PLAY, FINISHED"),
    club_id: Optional[int] = Query(None, description="Get games participated by club"),
    sort: str = Query("asc", description="Sort order: 'asc' or 'desc'"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a list of matches.
    - **league_id**: Filter by league
    - **matchday**: Matchday number
    - **status**: Filter by match status
    - **club_id**: Get games participated by club
    """
    query = select(Match).options(
        selectinload(Match.home_team),
        selectinload(Match.away_team),
    )

    if league_id is not None:
        query = query.where(Match.league_id == league_id)
    if club_id is not None:
        query = query.where((Match.home_team_id == club_id) | (Match.away_team_id == club_id))
    if matchday is not None:
        query = query.where(Match.matchday == matchday)
    if status:
        statuses = [s.strip().upper() for s in status.split(',')]
        query = query.where(Match.status.in_(statuses))

    if sort == "desc":
        query = query.order_by(Match.utc_date.desc()).offset(skip).limit(limit)
    else:
        query = query.order_by(Match.utc_date.asc()).offset(skip).limit(limit)

    result = await db.execute(query)
    matches = result.scalars().all()

    return [_enrich_match(m, MatchListResponse) for m in matches]


@router.get("/live", response_model=List[MatchResponse], summary="Live matches")
async def get_live_matches(
    league_id: Optional[int] = Query(None, description="Filter by league"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns currently playing live matches.
    """
    query = (
        select(Match)
        .options(
            selectinload(Match.home_team),
            selectinload(Match.away_team),
        )
        .where(Match.status.in_(["IN_PLAY", "PAUSED"]))
    )
    
    if league_id is not None:
        query = query.where(Match.league_id == league_id)
        
    result = await db.execute(query)
    matches = result.scalars().all()

    return [_enrich_match(m, MatchResponse) for m in matches]


@router.get("/{match_id}", response_model=MatchResponse, summary="Match details")
async def get_match(
    match_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Returns match details by ID.
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
        raise HTTPException(status_code=404, detail="Match not found")

    return _enrich_match(match, MatchResponse)
