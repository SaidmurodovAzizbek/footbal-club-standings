from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db
from app.models.club import Club
from app.schemas.club import ClubResponse, ClubListResponse

router = APIRouter(prefix="/clubs", tags=["Clubs"])


@router.get("/", response_model=List[ClubListResponse], summary="List of all clubs")
async def get_clubs(
    league_id: Optional[int] = Query(None, description="Filter by league"),
    search: Optional[str] = Query(None, description="Search by club name"),
    lang: str = Query("en", description="Language: 'en' or 'uz'"),
    skip: int = Query(0, ge=0, description="Skip count"),
    limit: int = Query(50, ge=1, le=100, description="Limit count"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns a list of clubs.
    - **league_id**: Filter by league
    - **search**: Search by club name
    - **lang**: Response language (en/uz)
    """
    query = select(Club)

    if league_id is not None:
        query = query.where(Club.league_id == league_id)

    if search:
        query = query.where(
            Club.name_en.ilike(f"%{search}%") | Club.name_uz.ilike(f"%{search}%")
        )

    query = query.order_by(Club.name_en).offset(skip).limit(limit)

    result = await db.execute(query)
    clubs = result.scalars().all()
    return clubs


@router.get("/{club_id}", response_model=ClubResponse, summary="Club details")
async def get_club(
    club_id: int,
    lang: str = Query("en", description="Language: 'en' or 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Returns club details by ID (with history, stadium, Wikipedia data).
    """
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()

    if not club:
        raise HTTPException(status_code=404, detail="Club not found")

    return ClubResponse.model_validate(club)
