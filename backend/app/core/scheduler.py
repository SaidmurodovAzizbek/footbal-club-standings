"""
FCS Scheduled Sync - Automated synchronization based on APScheduler.

Schedule:
  - Leagues:    Daily 1x (06:00 UTC)
  - Clubs:      Weekly (Monday 06:00 UTC)
  - Standings:  Every 15 minutes (on matchdays)
  - Matches:    Daily 2x (08:00, 00:00 UTC)
  - Live:       Every 60 seconds (during live matches)
"""

import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)

# Store latest sync timestamps
sync_status: dict[str, str | None] = {
    "leagues": None,
    "clubs": None,
    "standings": None,
    "matches": None,
    "live": None,
}


def _update_status(key: str):
    """Update sync status."""
    sync_status[key] = datetime.utcnow().isoformat()


# ──────────────────────────────────────────────
#  Job functions
# ──────────────────────────────────────────────

async def sync_leagues_job():
    """League synchronization — 1 time per day."""
    from app.services.football_data import football_data_service
    try:
        logger.info("[SCHEDULER] League sync started")
        result = await football_data_service.sync_leagues()
        _update_status("leagues")
        logger.info(f"[SCHEDULER] {len(result)} leagues synchronized")
    except Exception as e:
        logger.error(f"[SCHEDULER] League sync error: {e}")


async def sync_clubs_job():
    """Club synchronization — weekly."""
    from app.services.football_data import football_data_service
    try:
        logger.info("[SCHEDULER] Club sync started")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_clubs(code)
            total += len(result)

        # Wikipedia processing (only empty summaries)
        wiki_count = await football_data_service.sync_wikipedia()

        _update_status("clubs")
        logger.info(
            f"[SCHEDULER] {total} clubs + {wiki_count} wiki articles synchronized"
        )
    except Exception as e:
        logger.error(f"[SCHEDULER] Club sync error: {e}")


async def sync_standings_job():
    """Standings synchronization — every 15 minutes (on matchdays)."""
    from app.services.football_data import football_data_service
    from app.core.database import async_session
    from app.models.match import Match
    from sqlalchemy import select, func
    from datetime import timedelta

    try:
        # Check if there are matches today
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
            logger.debug("[SCHEDULER] No matches today — skipping standings sync")
            return

        logger.info("[SCHEDULER] Standings sync started")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_standings(code)
            total += len(result)

        _update_status("standings")
        logger.info(f"[SCHEDULER] {total} standings synchronized")
    except Exception as e:
        logger.error(f"[SCHEDULER] Standings sync error: {e}")


async def sync_matches_job():
    """Match synchronization — 2 times per day."""
    from app.services.football_data import football_data_service
    try:
        logger.info("[SCHEDULER] Match sync started")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        total = 0
        for code in codes:
            result = await football_data_service.sync_matches(code)
            total += len(result)

        _update_status("matches")
        logger.info(f"[SCHEDULER] {total} matches synchronized")
    except Exception as e:
        logger.error(f"[SCHEDULER] Match sync error: {e}")


async def sync_live_job():
    """Live match synchronization — every 60 seconds."""
    from app.services.football_data import football_data_service
    from app.core.database import async_session
    from app.models.match import Match
    from sqlalchemy import select, func

    try:
        # Check if there are any games currently played
        async with async_session() as session:
            result = await session.execute(
                select(func.count(Match.id)).where(
                    Match.status.in_(["IN_PLAY", "PAUSED", "LIVE"])
                )
            )
            live_count = result.scalar() or 0

        if live_count == 0:
            logger.debug("[SCHEDULER] No live matches — skipping live sync")
            return

        logger.info(f"[SCHEDULER] {live_count} live matches — sync started")
        codes = list(football_data_service.SUPPORTED_LEAGUES.keys())
        for code in codes:
            await football_data_service.sync_matches(code)

        _update_status("live")
    except Exception as e:
        logger.error(f"[SCHEDULER] Live sync error: {e}")


# ──────────────────────────────────────────────
#  Scheduler initialization
# ──────────────────────────────────────────────

def create_scheduler() -> AsyncIOScheduler:
    """
    Create APScheduler and register all jobs.

    Returns:
        Configured AsyncIOScheduler object
    """
    scheduler = AsyncIOScheduler(timezone="UTC")

    # 1. Leagues — Daily 1x (06:00 UTC)
    scheduler.add_job(
        sync_leagues_job,
        trigger=CronTrigger(hour=6, minute=0),
        id="sync_leagues",
        name="League synchronization (daily)",
        replace_existing=True,
    )

    # 2. Clubs — Weekly (Monday 06:00 UTC)
    scheduler.add_job(
        sync_clubs_job,
        trigger=CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="sync_clubs",
        name="Club synchronization (weekly)",
        replace_existing=True,
    )

    # 3. Standings — Every 15 minutes
    scheduler.add_job(
        sync_standings_job,
        trigger=IntervalTrigger(minutes=15),
        id="sync_standings",
        name="Standings synchronization (15 min)",
        replace_existing=True,
    )

    # 4. Matches — Daily 2x (08:00 and 00:00 UTC)
    scheduler.add_job(
        sync_matches_job,
        trigger=CronTrigger(hour="0,8", minute=0),
        id="sync_matches",
        name="Match synchronization (daily 2x)",
        replace_existing=True,
    )

    # 5. Live — Every 60 seconds
    scheduler.add_job(
        sync_live_job,
        trigger=IntervalTrigger(seconds=60),
        id="sync_live",
        name="Live match synchronization (60s)",
        replace_existing=True,
    )

    logger.info("Scheduler configured — 5 jobs registered")
    return scheduler
