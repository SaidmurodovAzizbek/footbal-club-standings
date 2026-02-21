"""
Sync API endpoints — manual trigger and status check.
"""

from fastapi import APIRouter, Query
from typing import Optional, List

from app.services.football_data import football_data_service
from app.core.scheduler import sync_status

router = APIRouter(prefix="/system", tags=["System"])


@router.post("/sync", summary="Manual synchronization")
async def trigger_sync(
    league_codes: Optional[List[str]] = Query(
        None, description="League codes: PL, PD, SA, BL1, FL1, CL"
    ),
    include_wiki: bool = Query(
        True, description="Also synchronize Wikipedia data"
    ),
):
    """
    Synchronize data manually.
    - **league_codes**: Leagues to synchronize (all if not provided)
    - **include_wiki**: Fetch Wikipedia data as well
    """
    stats = await football_data_service.sync_all(league_codes)
    return {
        "message": "Synchronization complete",
        "stats": stats,
    }


@router.post("/sync/standings", summary="Standings synchronization")
async def trigger_sync_standings(
    league_codes: Optional[List[str]] = Query(
        None, description="League codes"
    ),
):
    """Synchronize only standings."""
    codes = league_codes or list(football_data_service.SUPPORTED_LEAGUES.keys())
    total = 0
    for code in codes:
        result = await football_data_service.sync_standings(code)
        total += len(result)
    return {"message": f"{total} standings synchronized"}


@router.post("/sync/matches", summary="Matches synchronization")
async def trigger_sync_matches(
    league_codes: Optional[List[str]] = Query(
        None, description="League codes"
    ),
):
    """Synchronize only matches."""
    codes = league_codes or list(football_data_service.SUPPORTED_LEAGUES.keys())
    total = 0
    for code in codes:
        result = await football_data_service.sync_matches(code)
        total += len(result)
    return {"message": f"{total} matches synchronized"}


@router.post("/sync/wiki", summary="Wikipedia synchronization")
async def trigger_sync_wiki(
    league_code: Optional[str] = Query(None, description="League code"),
):
    """Synchronize only Wikipedia data."""
    count = await football_data_service.sync_wikipedia(league_code)
    return {"message": f"{count} clubs updated with Wiki data"}


@router.get("/sync/status", summary="Sync status")
async def get_sync_status():
    """
    Returns the last synchronization timestamps.
    """
    return {
        "status": sync_status,
        "schedule": {
            "leagues": "Daily 1x (06:00 UTC)",
            "clubs": "Weekly (Monday 06:00 UTC)",
            "standings": "Every 15 minutes (on matchdays)",
            "matches": "Daily 2x (08:00, 00:00 UTC)",
            "live": "Every 60 seconds (during live matches)",
        },
    }
