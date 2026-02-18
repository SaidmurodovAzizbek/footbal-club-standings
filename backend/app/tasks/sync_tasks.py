"""
Background sync tasks - Football-Data.org dan ma'lumotlarni sinxronlashtirish.

Strategiya:
- Standings: Har 1 soatda yangilanadi
- Live matches: O'yin bo'layotganda har 60 sekundda
- Clubs/Leagues: Serverga birinchi ishga tushganda yoki administrator so'rovida
"""
import asyncio
import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.league import League
from app.models.club import Club
from app.models.match import Match
from app.models.standing import Standing
from app.services.football_api import football_api

logger = logging.getLogger(__name__)

# Bepul API rejasi bilan ishlash uchun ligalar ro'yxati
# Football-Data.org bepul rejada faqat ba'zi ligalar mavjud
FREE_TIER_COMPETITIONS = [
    2021,  # Premier League (England)
    2014,  # La Liga (Spain)
    2002,  # Bundesliga (Germany)
    2019,  # Serie A (Italy)
    2015,  # Ligue 1 (France)
    2001,  # UEFA Champions League
]


async def sync_leagues():
    """Ligalar ma'lumotlarini sinxronlashtirish."""
    logger.info("Ligalar sinxronizatsiyasi boshlandi...")

    async with async_session() as session:
        for comp_id in FREE_TIER_COMPETITIONS:
            data = await football_api.get_competition(comp_id)
            if not data:
                continue

            # Bormi yoki yangi yaratish kerakmi tekshirish
            result = await session.execute(
                select(League).where(League.external_id == comp_id)
            )
            league = result.scalar_one_or_none()

            season_data = data.get("currentSeason", {})

            if league:
                # Mavjud ligani yangilash
                league.name_en = data.get("name", league.name_en)
                league.code = data.get("code", league.code)
                league.country = data.get("area", {}).get("name", league.country)
                league.emblem_url = data.get("emblem", league.emblem_url)
                league.current_matchday = season_data.get("currentMatchday")
            else:
                # Yangi liga yaratish
                league = League(
                    external_id=comp_id,
                    name_en=data.get("name", "Unknown"),
                    code=data.get("code", "UNK"),
                    country=data.get("area", {}).get("name", "Unknown"),
                    emblem_url=data.get("emblem"),
                    current_matchday=season_data.get("currentMatchday"),
                    is_active=True,
                )
                session.add(league)

            await session.commit()
            # API rate limitni hurmat qilish (10 req/min)
            await asyncio.sleep(7)

    logger.info("Ligalar sinxronizatsiyasi tugadi.")


async def sync_teams(competition_id: int):
    """Liga jamoalarini sinxronlashtirish."""
    logger.info(f"Jamoalar sinxronizatsiyasi boshlandi: competition={competition_id}")

    data = await football_api.get_competition_teams(competition_id)
    if not data or "teams" not in data:
        logger.warning(f"Jamoalar topilmadi: competition={competition_id}")
        return

    async with async_session() as session:
        # Liga IDni olish
        result = await session.execute(
            select(League).where(League.external_id == competition_id)
        )
        league = result.scalar_one_or_none()
        if not league:
            logger.error(f"Liga topilmadi: external_id={competition_id}")
            return

        for team_data in data["teams"]:
            team_ext_id = team_data["id"]

            result = await session.execute(
                select(Club).where(Club.external_id == team_ext_id)
            )
            club = result.scalar_one_or_none()

            if club:
                club.name_en = team_data.get("name", club.name_en)
                club.short_name = team_data.get("shortName", club.short_name)
                club.tla = team_data.get("tla", club.tla)
                club.crest_url = team_data.get("crest", club.crest_url)
                club.founded = team_data.get("founded", club.founded)
                club.venue = team_data.get("venue", club.venue)
                club.website = team_data.get("website", club.website)
                club.address = team_data.get("address", club.address)
                club.club_colors = team_data.get("clubColors", club.club_colors)
            else:
                club = Club(
                    external_id=team_ext_id,
                    league_id=league.id,
                    name_en=team_data.get("name", "Unknown"),
                    short_name=team_data.get("shortName"),
                    tla=team_data.get("tla"),
                    crest_url=team_data.get("crest"),
                    founded=team_data.get("founded"),
                    venue=team_data.get("venue"),
                    website=team_data.get("website"),
                    address=team_data.get("address"),
                    club_colors=team_data.get("clubColors"),
                )
                session.add(club)

        await session.commit()

    logger.info(f"Jamoalar sinxronizatsiyasi tugadi: competition={competition_id}")


async def sync_standings(competition_id: int):
    """Liga turni jadvalini sinxronlashtirish."""
    logger.info(f"Standings sinxronizatsiyasi boshlandi: competition={competition_id}")

    data = await football_api.get_standings(competition_id)
    if not data or "standings" not in data:
        return

    async with async_session() as session:
        result = await session.execute(
            select(League).where(League.external_id == competition_id)
        )
        league = result.scalar_one_or_none()
        if not league:
            return

        season_data = data.get("season", {})
        season_year = int(str(season_data.get("startDate", "2024"))[:4])

        # TOTAL jadval turini olish
        for standing_type in data["standings"]:
            if standing_type.get("type") != "TOTAL":
                continue

            for entry in standing_type.get("table", []):
                team_ext_id = entry.get("team", {}).get("id")
                if not team_ext_id:
                    continue

                # Klubni external_id bo'yicha topish
                club_result = await session.execute(
                    select(Club).where(Club.external_id == team_ext_id)
                )
                club = club_result.scalar_one_or_none()
                if not club:
                    continue

                # Mavjud standingni qidirish
                standing_result = await session.execute(
                    select(Standing).where(
                        Standing.league_id == league.id,
                        Standing.club_id == club.id,
                        Standing.season == season_year,
                    )
                )
                standing = standing_result.scalar_one_or_none()

                standing_data = {
                    "position": entry.get("position", 0),
                    "played": entry.get("playedGames", 0),
                    "won": entry.get("won", 0),
                    "draw": entry.get("draw", 0),
                    "lost": entry.get("lost", 0),
                    "goals_for": entry.get("goalsFor", 0),
                    "goals_against": entry.get("goalsAgainst", 0),
                    "goal_difference": entry.get("goalDifference", 0),
                    "points": entry.get("points", 0),
                    "form": entry.get("form"),
                    "matchday": league.current_matchday,
                }

                if standing:
                    for key, value in standing_data.items():
                        setattr(standing, key, value)
                else:
                    standing = Standing(
                        league_id=league.id,
                        club_id=club.id,
                        season=season_year,
                        **standing_data,
                    )
                    session.add(standing)

        await session.commit()

    logger.info(f"Standings sinxronizatsiyasi tugadi: competition={competition_id}")


async def sync_matches(competition_id: int):
    """Liga o'yinlarini sinxronlashtirish."""
    logger.info(f"O'yinlar sinxronizatsiyasi boshlandi: competition={competition_id}")

    data = await football_api.get_matches(competition_id)
    if not data or "matches" not in data:
        return

    async with async_session() as session:
        result = await session.execute(
            select(League).where(League.external_id == competition_id)
        )
        league = result.scalar_one_or_none()
        if not league:
            return

        for match_data in data["matches"]:
            match_ext_id = match_data["id"]

            home_ext_id = match_data.get("homeTeam", {}).get("id")
            away_ext_id = match_data.get("awayTeam", {}).get("id")

            if not home_ext_id or not away_ext_id:
                continue

            # Klublarni topish
            home_result = await session.execute(
                select(Club).where(Club.external_id == home_ext_id)
            )
            home_club = home_result.scalar_one_or_none()

            away_result = await session.execute(
                select(Club).where(Club.external_id == away_ext_id)
            )
            away_club = away_result.scalar_one_or_none()

            if not home_club or not away_club:
                continue

            # Natija ma'lumotlari
            score = match_data.get("score", {})
            full_time = score.get("fullTime", {})
            half_time = score.get("halfTime", {})

            match_values = {
                "league_id": league.id,
                "matchday": match_data.get("matchday"),
                "status": match_data.get("status", "SCHEDULED"),
                "utc_date": match_data.get("utcDate"),
                "home_team_id": home_club.id,
                "away_team_id": away_club.id,
                "home_score": full_time.get("home"),
                "away_score": full_time.get("away"),
                "home_score_ht": half_time.get("home"),
                "away_score_ht": half_time.get("away"),
                "stage": match_data.get("stage"),
                "group_name": match_data.get("group"),
                "duration": score.get("duration"),
            }

            # Referee
            referees = match_data.get("referees", [])
            if referees:
                match_values["referee"] = referees[0].get("name")

            # Mavjud o'yinni qidirish
            result = await session.execute(
                select(Match).where(Match.external_id == match_ext_id)
            )
            existing = result.scalar_one_or_none()

            if existing:
                for key, value in match_values.items():
                    setattr(existing, key, value)
            else:
                match = Match(external_id=match_ext_id, **match_values)
                session.add(match)

        await session.commit()

    logger.info(f"O'yinlar sinxronizatsiyasi tugadi: competition={competition_id}")


async def run_full_sync():
    """Barcha ma'lumotlarni to'liq sinxronlashtirish (birinchi marta yoki qo'lda)."""
    logger.info("=== TO'LIQ SINXRONIZATSIYA BOSHLANDI ===")

    await sync_leagues()

    for comp_id in FREE_TIER_COMPETITIONS:
        await sync_teams(comp_id)
        await asyncio.sleep(7)  # Rate limit

        await sync_standings(comp_id)
        await asyncio.sleep(7)

        await sync_matches(comp_id)
        await asyncio.sleep(7)

    logger.info("=== TO'LIQ SINXRONIZATSIYA TUGADI ===")
