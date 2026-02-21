"""
Background sync tasks (Eski qoldiq fayl).
Ma'lumotlarni sinxronlashtirish endi markaziy football_data_service orqali boshqariladi.
"""
import logging
from app.services.football_data import football_data_service

logger = logging.getLogger(__name__)

# Bepul API rejasi bilan ishlash uchun ligalar kodlari ro'yxati
FREE_TIER_COMPETITIONS = list(football_data_service.SUPPORTED_LEAGUES.keys())

async def sync_leagues():
    """Ligalar ma'lumotlarini sinxronlashtirish."""
    await football_data_service.sync_leagues()

async def sync_teams(competition_code: str):
    """Liga jamoalarini sinxronlashtirish."""
    await football_data_service.sync_clubs(competition_code)

async def sync_standings(competition_code: str):
    """Liga turni jadvalini sinxronlashtirish."""
    await football_data_service.sync_standings(competition_code)

async def sync_matches(competition_code: str):
    """Liga o'yinlarini sinxronlashtirish."""
    await football_data_service.sync_matches(competition_code)

async def run_full_sync():
    """Barcha ma'lumotlarni to'liq sinxronlashtirish."""
    await football_data_service.sync_all()
