from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.api.deps import get_db
from app.models.league import League
from app.schemas.league import LeagueResponse, LeagueListResponse

router = APIRouter(prefix="/leagues", tags=["Leagues"])


@router.get("/", response_model=List[LeagueListResponse], summary="List of all leagues")
async def get_leagues(
    is_active: Optional[bool] = Query(None, description="Filter active leagues"),
    lang: str = Query("en", description="Language: 'en' or 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a list of all leagues.
    - **is_active**: True for active leagues only
    - **lang**: Response language (en/uz)
    """
    query = select(League)
    if is_active is not None:
        query = query.where(League.is_active == is_active)
    query = query.order_by(League.id)

    result = await db.execute(query)
    leagues = result.scalars().all()
    return leagues


@router.get("/{league_id}", response_model=LeagueResponse, summary="League details")
async def get_league(
    league_id: int,
    lang: str = Query("en", description="Language: 'en' or 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns league details by ID.
    """
    result = await db.execute(select(League).where(League.id == league_id))
    league = result.scalar_one_or_none()

    if not league:
        raise HTTPException(status_code=404, detail="League not found")

    # Add localized name
    response_data = LeagueResponse.model_validate(league)
    response_data.name = league.get_name(lang)
    return response_data
