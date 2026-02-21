from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db
from app.models.standing import Standing
from app.schemas.standing import StandingResponse

router = APIRouter(prefix="/standings", tags=["Standings"])


@router.get("/league/{league_id}", response_model=List[StandingResponse], summary="League standings")
async def get_standings_by_league(
    league_id: int,
    season: Optional[int] = Query(None, description="Season year (e.g. 2024)"),
    lang: str = Query("en", description="Language: 'en' or 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns league standings.
    - **league_id**: League ID
    - **season**: Season year (default: latest season)
    - **lang**: Response language (en/uz)
    """
    query = (
        select(Standing)
        .options(selectinload(Standing.club))
        .where(Standing.league_id == league_id)
    )

    if season is not None:
        query = query.where(Standing.season == season)

    query = query.order_by(Standing.position)

    result = await db.execute(query)
    standings = result.scalars().all()

    # Enrich each standing with club data (via relationship)
    enriched = []
    for standing in standings:
        standing_data = StandingResponse.model_validate(standing)
        if standing.club:
            standing_data.club_name = standing.club.get_name(lang)
            standing_data.club_crest = standing.club.crest_local or standing.club.crest_url
        enriched.append(standing_data)

    return enriched
