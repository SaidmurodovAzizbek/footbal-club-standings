"""
FCS Scheduled Sync - APScheduler asosida avtomatik sinxronizatsiya.

Schedule:
  - Leagues:    Kuniga 1x (06:00 UTC)
  - Clubs:      Haftalik (Dushanba 06:00 UTC)
  - Standings:  Har 15 daqiqa (matchday kunlarida)
  - Matches:    Kuniga 2x (08:00, 00:00 UTC)
  - Live:       Har 60 soniya (o'yin vaqtida)
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Oxirgi sync vaqtlarini saqlash
sync_status: dict[str, str | None] = {
    "leagues": None,
    "clubs": None,
    "standings": None,
    "matches": None,
    "live": None,
}


def _update_status(key: str):
    """Sync statusini yangilash."""
    sync_status[key] = datetime.utcnow().isoformat()


# ──────────────────────────────────────────────
#  Job funksiyalari
# ──────────────────────────────────────────────

async def sync_leagues_job():
    """Ligalar sinxronizatsiyasi — kuniga 1 marta."""
    from app.services.football_data import football_data_service
    try:
        logger.info("⏰ [SCHEDULER] Ligalar sinxronizatsiyasi boshlandi")
        result = await football_data_service.sync_leagues()
        _update_status("leagues")
        logger.info(f"⏰ [SCHEDULER] {len(result)} ta liga sinxronlashtirildi")
    except Exception as e:
        logger.error(f"⏰ [SCHEDULER] Ligalar xato: {e}")


async def sync_clubs_job():
    """Klublar sinxronizatsiyasi — haftalik."""
    from app.services.football_data import football_data_service
    try:
        logger.info("⏰ [SCHEDULER] Klublar sinxronizatsiyasi boshlandi")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_clubs(code)
            total += len(result)

        # Wikipedia ham (faqat bo'sh bo'lganlar)
        wiki_count = await football_data_service.sync_wikipedia()

        _update_status("clubs")
        logger.info(
            f"⏰ [SCHEDULER] {total} ta klub + {wiki_count} ta wiki sinxronlashtirildi"
        )
    except Exception as e:
        logger.error(f"⏰ [SCHEDULER] Klublar xato: {e}")


async def sync_standings_job():
    """Turni jadval sinxronizatsiyasi — har 15 daqiqada (matchday kunlarida)."""
    from app.services.football_data import football_data_service
    from app.core.database import async_session
    from app.models.match import Match
    from sqlalchemy import select, func
    from datetime import timedelta

    try:
        # Bugun o'yin bormi tekshirish
        async with async_session() as session:
            today_start = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            today_end = today_start + timedelta(days=1)

            result = await session.execute(
                select(func.count(Match.id)).where(
                    Match.utc_date >= today_start,
                    Match.utc_date < today_end,
                )
            )
            match_count = result.scalar() or 0

        if match_count == 0:
            logger.debug("⏰ [SCHEDULER] Bugun o'yin yo'q — standings o'tkazildi")
            return

        logger.info("⏰ [SCHEDULER] Standings sinxronizatsiyasi boshlandi")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_standings(code)
            total += len(result)

        _update_status("standings")
        logger.info(f"⏰ [SCHEDULER] {total} ta standing sinxronlashtirildi")
    except Exception as e:
        logger.error(f"⏰ [SCHEDULER] Standings xato: {e}")


async def sync_matches_job():
    """O'yinlar sinxronizatsiyasi — kuniga 2 marta."""
    from app.services.football_data import football_data_service
    try:
        logger.info("⏰ [SCHEDULER] O'yinlar sinxronizatsiyasi boshlandi")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_matches(code)
            total += len(result)

        _update_status("matches")
        logger.info(f"⏰ [SCHEDULER] {total} ta o'yin sinxronlashtirildi")
    except Exception as e:
        logger.error(f"⏰ [SCHEDULER] O'yinlar xato: {e}")


async def sync_live_job():
    """Jonli o'yinlar sinxronizatsiyasi — har 60 soniyada."""
    from app.services.football_data import football_data_service
    from app.core.database import async_session
    from app.models.match import Match
    from sqlalchemy import select, func

    try:
        # Hozir o'ynalayotgan o'yin bormi tekshirish
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Match.id)).where(
                    Match.status.in_(["IN_PLAY", "PAUSED", "LIVE"])
                )
            )
            live_count = result.scalar() or 0

        if live_count == 0:
            logger.debug("⏰ [SCHEDULER] Jonli o'yin yo'q — live sync o'tkazildi")
            return

        logger.info(f"⏰ [SCHEDULER] {live_count} ta jonli o'yin — sync boshlandi")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        for code in codes:
            await football_data_service.sync_matches(code)

        _update_status("live")
    except Exception as e:
        logger.error(f"⏰ [SCHEDULER] Live sync xato: {e}")


# ──────────────────────────────────────────────
#  Scheduler yaratish va ishga tushirish
# ──────────────────────────────────────────────

def create_scheduler() -> AsyncIOScheduler:
    """
    APScheduler yaratish va barcha joblarni ro'yxatdan o'tkazish.

    Returns:
        Sozlangan AsyncIOScheduler obyekti
    """
    scheduler = AsyncIOScheduler(timezone="UTC")

    # 1. Leagues — Kuniga 1x (06:00 UTC)
    scheduler.add_job(
        sync_leagues_job,
        trigger=CronTrigger(hour=6, minute=0),
        id="sync_leagues",
        name="Liga sinxronizatsiyasi (kunlik)",
        replace_existing=True,
    )

    # 2. Clubs — Haftalik (Dushanba 06:00 UTC)
    scheduler.add_job(
        sync_clubs_job,
        trigger=CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="sync_clubs",
        name="Klub sinxronizatsiyasi (haftalik)",
        replace_existing=True,
    )

    # 3. Standings — Har 15 daqiqada
    scheduler.add_job(
        sync_standings_job,
        trigger=IntervalTrigger(minutes=15),
        id="sync_standings",
        name="Standings sinxronizatsiyasi (15 min)",
        replace_existing=True,
    )

    # 4. Matches — Kuniga 2x (08:00 va 00:00 UTC)
    scheduler.add_job(
        sync_matches_job,
        trigger=CronTrigger(hour="0,8", minute=0),
        id="sync_matches",
        name="O'yinlar sinxronizatsiyasi (kunlik 2x)",
        replace_existing=True,
    )

    # 5. Live — Har 60 soniyada
    scheduler.add_job(
        sync_live_job,
        trigger=IntervalTrigger(seconds=60),
        id="sync_live",
        name="Jonli o'yinlar sinxronizatsiyasi (60s)",
        replace_existing=True,
    )

    logger.info("📅 Scheduler sozlandi — 5 ta job ro'yxatdan o'tkazildi")
    return scheduler
