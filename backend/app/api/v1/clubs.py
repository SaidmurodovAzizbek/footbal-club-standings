from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional

from app.api.deps import get_db
from app.models.club import Club
from app.schemas.club import ClubResponse, ClubListResponse

router = APIRouter(prefix="/clubs", tags=["Clubs - Klublar"])


@router.get("/", response_model=List[ClubListResponse], summary="Barcha klublar ro'yxati")
async def get_clubs(
    league_id: Optional[int] = Query(None, description="Liga bo'yicha filtrlash"),
    search: Optional[str] = Query(None, description="Klub nomi bo'yicha qidirish"),
    lang: str = Query("en", description="Til: 'en' yoki 'uz'"),
    skip: int = Query(0, ge=0, description="O'tkazib yuborish"),
    limit: int = Query(50, ge=1, le=100, description="Cheklov"),
    db: AsyncSession = Depends(get_db),
):
    """
    Klublar ro'yxatini qaytaradi.
    - **league_id**: Liga bo'yicha filtrlash
    - **search**: Klub nomi bo'yicha qidirish
    - **lang**: Javob tili (en/uz)
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


@router.get("/{club_id}", response_model=ClubResponse, summary="Klub tafsilotlari")
async def get_club(
    club_id: int,
    lang: str = Query("en", description="Til: 'en' yoki 'uz'"),
    db: AsyncSession = Depends(get_db),
):
    """
    Klub tafsilotlarini ID bo'yicha qaytaradi (tarix, stadion, Wikipedia ma'lumotlari bilan).
    """
    result = await db.execute(select(Club).where(Club.id == club_id))
    club = result.scalar_one_or_none()

    if not club:
        raise HTTPException(status_code=404, detail="Klub topilmadi")

    return ClubResponse.model_validate(club)
