"""
Sync API endpointlari — manual trigger va status tekshirish.
"""

from fastapi import APIRouter, Query
from typing import Optional, List

from app.services.football_data import football_data_service
from app.core.scheduler import sync_status

router = APIRouter(prefix="/system", tags=["System - Tizim"])


@router.post("/sync", summary="Manual sinxronizatsiya")
async def trigger_sync(
    league_codes: Optional[List[str]] = Query(
        None, description="Liga kodlari: PL, PD, SA, BL1, FL1, CL"
    ),
    include_wiki: bool = Query(
        True, description="Wikipedia ma'lumotlarini ham sinxronlashtirish"
    ),
):
    """
    Ma'lumotlarni qo'lda sinxronlashtirish.
    - **league_codes**: Sinxronlashtiriladigan ligalar (berilmasa barchasi)
    - **include_wiki**: Wikipedia ma'lumotlarini ham olish
    """
    stats = await football_data_service.sync_all(league_codes)
    return {
        "message": "Sinxronizatsiya tugadi",
        "stats": stats,
    }


@router.post("/sync/standings", summary="Standings sinxronizatsiya")
async def trigger_sync_standings(
    league_codes: Optional[List[str]] = Query(
        None, description="Liga kodlari"
    ),
):
    """Faqat turni jadvallarni sinxronlashtirish."""
    codes = league_codes or list(football_data_service.SUPPORTED_LEAGUES.keys())
    total = 0
    for code in codes:
        result = await football_data_service.sync_standings(code)
        total += len(result)
    return {"message": f"{total} ta standing sinxronlashtirildi"}


@router.post("/sync/matches", summary="Matches sinxronizatsiya")
async def trigger_sync_matches(
    league_codes: Optional[List[str]] = Query(
        None, description="Liga kodlari"
    ),
):
    """Faqat o'yinlarni sinxronlashtirish."""
    codes = league_codes or list(football_data_service.SUPPORTED_LEAGUES.keys())
    total = 0
    for code in codes:
        result = await football_data_service.sync_matches(code)
        total += len(result)
    return {"message": f"{total} ta o'yin sinxronlashtirildi"}


@router.post("/sync/wiki", summary="Wikipedia sinxronizatsiya")
async def trigger_sync_wiki(
    league_code: Optional[str] = Query(None, description="Liga kodi"),
):
    """Faqat Wikipedia ma'lumotlarini sinxronlashtirish."""
    count = await football_data_service.sync_wikipedia(league_code)
    return {"message": f"{count} ta klub Wiki bilan yangilandi"}


@router.get("/sync/status", summary="Sync holati")
async def get_sync_status():
    """
    Oxirgi sinxronizatsiya vaqtlarini qaytaradi.
    """
    return {
        "status": sync_status,
        "schedule": {
            "leagues": "Kuniga 1x (06:00 UTC)",
            "clubs": "Haftalik (Dushanba 06:00 UTC)",
            "standings": "Har 15 daqiqa (matchday kunlarida)",
            "matches": "Kuniga 2x (08:00, 00:00 UTC)",
            "live": "Har 60 soniya (o'yin vaqtida)",
        },
    }
