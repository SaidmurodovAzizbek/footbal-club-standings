from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import get_db
from app.models.standing import Standing
from app.models.club import Club
from app.schemas.standing import StandingResponse, StandingListResponse

router = APIRouter(prefix="/standings", tags=["Standings - Turni jadval"])


@router.get("/league/{league_id}", response_model=List[StandingResponse], summary="Liga jadvali")
async def get_standings_by_league(
    league_id: int,
    season: Optional[int] = Query(None, description="Mavsum yili (masalan: 2024)"),
    lang: str = Query("en", description="Til: 'en' yoki 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Liga turni jadvalini qaytaradi.
    - **league_id**: Liga ID
    - **season**: Mavsum yili (default: eng oxirgi mavsum)
    - **lang**: Javob tili (en/uz)
    """
    query = select(Standing).where(Standing.league_id == league_id)

    if season is not None:
        query = query.where(Standing.season == season)

    query = query.order_by(Standing.position)

    result = await db.execute(query)
    standings = result.scalars().all()

    # Har bir standingga klub ma'lumotlarini qo'shish
    enriched = []
    for standing in standings:
        standing_data = StandingResponse.model_validate(standing)

        club_result = await db.execute(select(Club).where(Club.id == standing.club_id))
        club = club_result.scalar_one_or_none()
        if club:
            standing_data.club_name = club.get_name(lang)
            standing_data.club_crest = club.crest_local or club.crest_url

        enriched.append(standing_data)

    return enriched
