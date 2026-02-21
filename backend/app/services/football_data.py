"""
FootballDataService - Football-Data.org API dan ma'lumotlarni olish va bazaga sinxronlashtirish.

Bu servis:
  1. Async HTTP (httpx) orqali tashqi API ga so'rov yuboradi
  2. Rate-limiting (10 req/min) ni hurmat qiladi (adaptive sleep + retry)
  3. Upsert (Update or Create) mantiq bilan ma'lumotlarni DB ga saqlaydi
  4. Liga, Klub, O'yin va Turni jadval ma'lumotlarini sinxronlashtiradi
"""

import asyncio
import time
import logging
from typing import Optional, Any
from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session
from app.models.league import League
from app.models.club import Club
from app.models.match import Match
from app.models.standing import Standing
from app.services.wikipedia_api import wikipedia_api

logger = logging.getLogger(__name__)


class FootballDataService:
    """
    Football-Data.org API bilan ishlash va bazaga sinxronlashtirish uchun to'liq servis.

    Xususiyatlar:
      - Adaptive rate-limiting: har bir so'rov orasida 6.5s kutish (10 req/min)
      - Retry mantiq: 429 xato bo'lsa qayta urinish (max 3 marta)
      - Upsert: external_id bo'yicha bormi tekshirib, kerak bo'lsa yangilaydi
    """

    # Football-Data.org bepul rejalari uchun liga kodlari
    SUPPORTED_LEAGUES: dict[str, int] = {
        "PL": 2021,    # Premier League (England)
        "PD": 2014,    # La Liga (Spain - Primera División)
        "SA": 2019,    # Serie A (Italy)
        "BL1": 2002,   # Bundesliga (Germany)
        "FL1": 2015,   # Ligue 1 (France)
        "CL": 2001,    # UEFA Champions League
    }

    def __init__(self):
        self.base_url = settings.FOOTBALL_API_BASE_URL
        self.api_key = settings.FOOTBALL_API_KEY
        self.headers = {"X-Auth-Token": self.api_key}

        # Rate-limiting holati
        self._request_timestamps: list[float] = []
        self._max_requests_per_minute = 10
        self._min_interval = 6.5  # 60s / 10 = 6s, + 0.5s xavfsizlik

    # ──────────────────────────────────────────────
    #  HTTP Layer - Rate Limiting + Retry
    # ──────────────────────────────────────────────

    async def _wait_for_rate_limit(self) -> None:
        """
        Rate-limit cheklovini kutish.
        Oxirgi 60 sekund ichida 10 tadan ko'p so'rov yuborilgan bo'lsa,
        yetarli vaqt o'tguncha kutadi.
        """
        now = time.monotonic()

        # Eskirgan timestamplarni tozalash (60s dan eski)
        self._request_timestamps = [
            ts for ts in self._request_timestamps if now - ts < 60.0
        ]

        # Agar 60s ichida 9 ta yoki undan ko'p so'rov bo'lsa, kutamiz
        if len(self._request_timestamps) >= self._max_requests_per_minute - 1:
            oldest = self._request_timestamps[0]
            wait_time = 60.0 - (now - oldest) + 1.0  # +1s xavfsizlik
            if wait_time > 0:
                logger.info(f"⏳ Rate-limit kutilmoqda: {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
        else:
            # Minimal interval (so'rovlar orasida)
            if self._request_timestamps:
                last = self._request_timestamps[-1]
                elapsed = now - last
                if elapsed < self._min_interval:
                    await asyncio.sleep(self._min_interval - elapsed)

        self._request_timestamps.append(time.monotonic())

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        max_retries: int = 3,
    ) -> Optional[dict[str, Any]]:
        """
        API ga so'rov yuborish - rate-limit + retry mantiq bilan.

        Args:
            endpoint: API yo'li (masalan, '/competitions/PL')
            params: Query parametrlar
            max_retries: Qayta urinishlar soni (429/5xx xatolar uchun)

        Returns:
            API javob dict yoki None (xato bo'lsa)
        """
        url = f"{self.base_url}{endpoint}"

        for attempt in range(1, max_retries + 1):
            await self._wait_for_rate_limit()

            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        url, headers=self.headers, params=params
                    )

                    # Rate limit xatosi - kutib qayta urinish
                    if response.status_code == 429:
                        retry_after = int(
                            response.headers.get("X-RequestCounter-Reset", 60)
                        )
                        logger.warning(
                            f"⚠️ 429 Rate Limited! {retry_after}s kutilmoqda "
                            f"(urinish {attempt}/{max_retries})..."
                        )
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    data = response.json()
                    logger.debug(f"✅ API so'rov muvaffaqiyatli: {endpoint}")
                    return data

            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                logger.error(
                    f"❌ API HTTP xato [{status}]: {endpoint} "
                    f"(urinish {attempt}/{max_retries})"
                )
                # 5xx server xatolari uchun qayta urinish
                if status >= 500 and attempt < max_retries:
                    await asyncio.sleep(5 * attempt)
                    continue
                return None

            except httpx.RequestError as e:
                logger.error(
                    f"❌ Tarmoq xatosi: {e} - {endpoint} "
                    f"(urinish {attempt}/{max_retries})"
                )
                if attempt < max_retries:
                    await asyncio.sleep(5 * attempt)
                    continue
                return None

            except Exception as e:
                logger.error(f"❌ Kutilmagan xato: {e} - {endpoint}")
                return None

        logger.error(f"❌ Barcha urinishlar tugadi: {endpoint}")
        return None

    # ──────────────────────────────────────────────
    #  FETCH Methods - API dan ma'lumot olish
    # ──────────────────────────────────────────────

    async def fetch_leagues(
        self, league_codes: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """
        Ligalar ma'lumotlarini API dan olish.

        Args:
            league_codes: Liga kodlari ro'yxati ['PL','PD','SA','BL1','FL1']
                          Berilmasa barcha qo'llab-quvvatlanadigan ligalar olinadi.

        Returns:
            Liga ma'lumotlari ro'yxati
        """
        codes = league_codes or list(self.SUPPORTED_LEAGUES.keys())
        results: list[dict[str, Any]] = []

        for code in codes:
            comp_id = self.SUPPORTED_LEAGUES.get(code)
            if not comp_id:
                logger.warning(f"⚠️ Noma'lum liga kodi: {code}")
                continue

            data = await self._make_request(f"/competitions/{code}")
            if data:
                results.append(data)
                logger.info(f"📋 Liga olingan: {data.get('name', code)}")
            else:
                logger.error(f"❌ Liga olinmadi: {code}")

        return results

    async def fetch_clubs(self, league_code: str) -> list[dict[str, Any]]:
        """
        Liga jamoalarini API dan olish.

        Args:
            league_code: Liga kodi (masalan 'PL')

        Returns:
            Jamoalar ro'yxati
        """
        data = await self._make_request(f"/competitions/{league_code}/teams")
        if not data or "teams" not in data:
            logger.error(f"❌ Jamoalar olinmadi: {league_code}")
            return []

        teams = data["teams"]
        logger.info(f"👥 {len(teams)} ta jamoa olingan: {league_code}")
        return teams

    async def fetch_matches(
        self, league_code: str, season: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Liga o'yinlarini API dan olish.

        Args:
            league_code: Liga kodi
            season: Mavsum yili (masalan 2024). None bo'lsa joriy mavsum.

        Returns:
            O'yinlar ro'yxati
        """
        params = {}
        if season is not None:
            params["season"] = season

        data = await self._make_request(
            f"/competitions/{league_code}/matches", params=params
        )
        if not data or "matches" not in data:
            logger.error(f"❌ O'yinlar olinmadi: {league_code}")
            return []

        matches = data["matches"]
        logger.info(f"⚽ {len(matches)} ta o'yin olingan: {league_code}")
        return matches

    async def fetch_standings(
        self, league_code: str, season: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Liga turni jadvalini API dan olish.

        Args:
            league_code: Liga kodi
            season: Mavsum yili. None bo'lsa joriy mavsum.

        Returns:
            Jadval yozuvlari (TOTAL turdagi)
        """
        params = {}
        if season is not None:
            params["season"] = season

        data = await self._make_request(
            f"/competitions/{league_code}/standings", params=params
        )
        if not data or "standings" not in data:
            logger.error(f"❌ Jadval olinmadi: {league_code}")
            return []

        # Faqat TOTAL turni olish (HOME/AWAY emas)
        standings_data: list[dict[str, Any]] = []
        season_info = data.get("season", {})

        for standing_group in data["standings"]:
            if standing_group.get("type") == "TOTAL":
                for entry in standing_group.get("table", []):
                    entry["_season_info"] = season_info
                standings_data.extend(standing_group.get("table", []))

        logger.info(
            f"📊 {len(standings_data)} ta jadval yozuvi olingan: {league_code}"
        )
        return standings_data

    # ──────────────────────────────────────────────
    #  UPSERT Helpers - DB ga saqlash
    # ──────────────────────────────────────────────

    async def _upsert_league(
        self, session: AsyncSession, api_data: dict[str, Any]
    ) -> League | None:
        """
        Ligani bazaga saqlash (upsert).
        external_id bo'yicha bormi tekshiradi, bo'lsa yangilaydi.
        """
        external_id = api_data.get("id")
        if external_id is None:
            return None

        try:
            result = await session.execute(
                select(League).where(League.external_id == external_id)
            )
            league = result.scalar_one_or_none()

            season_data = api_data.get("currentSeason") or {}

            # Mavsum sanalarini parse qilish
            season_start = None
            season_end = None
            if season_data.get("startDate"):
                try:
                    season_start = datetime.strptime(
                        season_data["startDate"], "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    pass
            if season_data.get("endDate"):
                try:
                    season_end = datetime.strptime(
                        season_data["endDate"], "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError):
                    pass

            league_values = {
                "name_en": api_data.get("name", "Unknown"),
                "code": api_data.get("code", "UNK"),
                "country": api_data.get("area", {}).get("name", "Unknown"),
                "emblem_url": api_data.get("emblem"),
                "current_matchday": season_data.get("currentMatchday"),
                "season_start": season_start,
                "season_end": season_end,
                "is_active": True,
            }

            if league:
                # UPDATE
                for key, value in league_values.items():
                    if value is not None:
                        setattr(league, key, value)
                logger.debug(f"🔄 Liga yangilandi: {league.name_en}")
            else:
                # CREATE
                league = League(external_id=external_id, **league_values)
                session.add(league)
                logger.info(f"➕ Yangi liga qo'shildi: {league_values['name_en']}")

            await session.flush()
            return league

        except Exception as e:
            logger.error(f"❌ Liga upsert xatosi (ext_id={external_id}): {e}")
            return None

    async def _upsert_club(
        self, session: AsyncSession, api_data: dict[str, Any], league_id: int
    ) -> Club | None:
        """
        Klubni bazaga saqlash (upsert).
        external_id bo'yicha bormi tekshiradi.
        """
        external_id = api_data.get("id")
        if external_id is None:
            return None

        try:
            result = await session.execute(
                select(Club).where(Club.external_id == external_id)
            )
            club = result.scalar_one_or_none()

            club_values = {
                "league_id": league_id,
                "name_en": api_data.get("name", "Unknown Team"),
                "short_name": api_data.get("shortName"),
                "tla": api_data.get("tla"),
                "crest_url": api_data.get("crest"),
                "founded": api_data.get("founded"),
                "venue": api_data.get("venue"),
                "website": api_data.get("website"),
                "address": api_data.get("address"),
                "club_colors": api_data.get("clubColors"),
                "coach_name": api_data.get("coach", {}).get("name"),
            }

            if club:
                for key, value in club_values.items():
                    if value is not None:
                        setattr(club, key, value)
                logger.debug(f"🔄 Klub yangilandi: {club.name_en}")
            else:
                club = Club(external_id=external_id, **club_values)
                session.add(club)
                logger.info(f"➕ Yangi klub: {club_values['name_en']}")

            await session.flush()
            return club

        except Exception as e:
            logger.error(f"❌ Klub upsert xatosi (ext_id={external_id}): {e}")
            return None

    async def _upsert_match(
        self,
        session: AsyncSession,
        api_data: dict[str, Any],
        league_id: int,
    ) -> Match | None:
        """
        O'yinni bazaga saqlash (upsert).
        external_id bo'yicha bormi tekshiradi.
        home_team va away_team external_id lar orqali DB dan topiladi.
        """
        external_id = api_data.get("id")
        if external_id is None:
            return None

        try:
            # Uy va mehmon jamoalarining DB id larini topish
            home_ext_id = api_data.get("homeTeam", {}).get("id")
            away_ext_id = api_data.get("awayTeam", {}).get("id")

            if not home_ext_id or not away_ext_id:
                logger.warning(
                    f"⚠️ O'yin jamoalari topilmadi: match_ext_id={external_id}"
                )
                return None

            home_result = await session.execute(
                select(Club.id).where(Club.external_id == home_ext_id)
            )
            home_club_id = home_result.scalar_one_or_none()

            away_result = await session.execute(
                select(Club.id).where(Club.external_id == away_ext_id)
            )
            away_club_id = away_result.scalar_one_or_none()

            if not home_club_id or not away_club_id:
                logger.warning(
                    f"⚠️ DB da jamoa topilmadi: home={home_ext_id}, "
                    f"away={away_ext_id} (match={external_id})"
                )
                return None

            # Natija ma'lumotlari
            score = api_data.get("score", {})
            full_time = score.get("fullTime") or {}
            half_time = score.get("halfTime") or {}

            # UTC sana parse
            utc_date_str = api_data.get("utcDate")
            utc_date = None
            if utc_date_str:
                try:
                    utc_date = datetime.fromisoformat(
                        utc_date_str.replace("Z", "+00:00")
                    )
                except (ValueError, TypeError):
                    utc_date = datetime.utcnow()
            else:
                utc_date = datetime.utcnow()

            # Hakam
            referees = api_data.get("referees", [])
            referee_name = referees[0].get("name") if referees else None

            match_values = {
                "league_id": league_id,
                "matchday": api_data.get("matchday"),
                "status": api_data.get("status", "SCHEDULED"),
                "utc_date": utc_date,
                "home_team_id": home_club_id,
                "away_team_id": away_club_id,
                "home_score": full_time.get("home"),
                "away_score": full_time.get("away"),
                "home_score_ht": half_time.get("home"),
                "away_score_ht": half_time.get("away"),
                "stage": api_data.get("stage"),
                "group_name": api_data.get("group"),
                "duration": score.get("duration"),
                "winner": score.get("winner"),
                "referee": referee_name,
            }

            # Upsert
            result = await session.execute(
                select(Match).where(Match.external_id == external_id)
            )
            match = result.scalar_one_or_none()

            if match:
                for key, value in match_values.items():
                    setattr(match, key, value)
                logger.debug(f"🔄 O'yin yangilandi: {external_id}")
            else:
                match = Match(external_id=external_id, **match_values)
                session.add(match)
                logger.debug(f"➕ Yangi o'yin: {external_id}")

            await session.flush()
            return match

        except Exception as e:
            logger.error(f"❌ O'yin upsert xatosi (ext_id={external_id}): {e}")
            return None

    async def _upsert_standing(
        self,
        session: AsyncSession,
        api_data: dict[str, Any],
        league_id: int,
        season: int,
        matchday: int | None = None,
    ) -> Standing | None:
        """
        Turni jadval yozuvini bazaga saqlash (upsert).
        league_id + club_id + season unikal kombinatsiyasi bo'yicha tekshiradi.
        """
        try:
            team_ext_id = api_data.get("team", {}).get("id")
            if not team_ext_id:
                return None

            # Klub DB id sini topish
            club_result = await session.execute(
                select(Club.id).where(Club.external_id == team_ext_id)
            )
            club_id = club_result.scalar_one_or_none()

            if not club_id:
                logger.warning(
                    f"⚠️ Standing uchun klub topilmadi: ext_id={team_ext_id}"
                )
                return None

            standing_values = {
                "position": api_data.get("position", 0),
                "played": api_data.get("playedGames", 0),
                "won": api_data.get("won", 0),
                "draw": api_data.get("draw", 0),
                "lost": api_data.get("lost", 0),
                "goals_for": api_data.get("goalsFor", 0),
                "goals_against": api_data.get("goalsAgainst", 0),
                "goal_difference": api_data.get("goalDifference", 0),
                "points": api_data.get("points", 0),
                "form": api_data.get("form"),
                "matchday": matchday,
            }

            # Unikal: league_id + club_id + season
            result = await session.execute(
                select(Standing).where(
                    Standing.league_id == league_id,
                    Standing.club_id == club_id,
                    Standing.season == season,
                )
            )
            standing = result.scalar_one_or_none()

            if standing:
                for key, value in standing_values.items():
                    setattr(standing, key, value)
                logger.debug(
                    f"🔄 Standing yangilandi: club_id={club_id}, pos={standing_values['position']}"
                )
            else:
                standing = Standing(
                    league_id=league_id,
                    club_id=club_id,
                    season=season,
                    **standing_values,
                )
                session.add(standing)
                logger.debug(f"➕ Yangi standing: club_id={club_id}")

            await session.flush()
            return standing

        except Exception as e:
            logger.error(f"❌ Standing upsert xatosi: {e}")
            return None

    # ──────────────────────────────────────────────
    #  SYNC Methods - Orchestration
    # ──────────────────────────────────────────────

    async def sync_leagues(
        self, league_codes: list[str] | None = None
    ) -> list[League]:
        """
        Ligalarni API dan olib, bazaga sinxronlashtirish.

        Returns:
            Saqlangan League ob'yektlari ro'yxati
        """
        logger.info("="*50)
        logger.info("📋 LIGALAR SINXRONIZATSIYASI BOSHLANDI")
        logger.info("="*50)

        leagues_data = await self.fetch_leagues(league_codes)
        synced: list[League] = []

        async with async_session() as session:
            for data in leagues_data:
                league = await self._upsert_league(session, data)
                if league:
                    synced.append(league)

            await session.commit()

        logger.info(f"✅ {len(synced)} ta liga sinxronlashtirildi")
        return synced

    async def sync_clubs(self, league_code: str) -> list[Club]:
        """
        Liga jamoalarini API dan olib, bazaga sinxronlashtirish.

        Args:
            league_code: Liga kodi (masalan 'PL')

        Returns:
            Saqlangan Club ob'yektlari ro'yxati
        """
        logger.info(f"👥 JAMOALAR SINXRONIZATSIYASI: {league_code}")

        teams_data = await self.fetch_clubs(league_code)
        synced: list[Club] = []

        async with async_session() as session:
            # Liga DB id sini olish
            result = await session.execute(
                select(League).where(League.code == league_code)
            )
            league = result.scalar_one_or_none()

            if not league:
                logger.error(f"❌ Liga topilmadi DB da: {league_code}")
                return []

            for team_data in teams_data:
                club = await self._upsert_club(session, team_data, league.id)
                if club:
                    synced.append(club)

            await session.commit()

        logger.info(f"✅ {len(synced)} ta jamoa sinxronlashtirildi: {league_code}")
        return synced

    async def sync_wikipedia(self, league_code: str | None = None) -> int:
        """
        Klublar uchun Wikipedia summary'larini olish va bazaga saqlash.
        Faqat wiki_summary_en bo'sh bo'lgan klublar uchun ishlaydi.

        Args:
            league_code: Liga kodi. None bo'lsa barcha klublar.

        Returns:
            Yangilangan klublar soni
        """
        logger.info(f"📚 WIKIPEDIA SINXRONIZATSIYASI BOSHLANDI")
        updated_count = 0

        async with async_session() as session:
            query = select(Club).where(Club.wiki_summary_en.is_(None))

            if league_code:
                league_result = await session.execute(
                    select(League).where(League.code == league_code)
                )
                league = league_result.scalar_one_or_none()
                if league:
                    query = query.where(Club.league_id == league.id)

            result = await session.execute(query)
            clubs = result.scalars().all()

            logger.info(f"📚 {len(clubs)} ta klub uchun Wikipedia ma'lumotlari olinadi")

            for club in clubs:
                try:
                    # Inglizcha summary
                    summary_en = await wikipedia_api.get_club_summary(
                        club.name_en, lang="en"
                    )
                    if summary_en:
                        club.wiki_summary_en = summary_en
                        logger.debug(f"📖 Wiki EN: {club.name_en}")

                    # O'zbekcha summary
                    summary_uz = await wikipedia_api.get_club_summary(
                        club.name_en, lang="uz"
                    )
                    if summary_uz:
                        club.wiki_summary_uz = summary_uz
                        logger.debug(f"📖 Wiki UZ: {club.name_en}")

                    if summary_en or summary_uz:
                        updated_count += 1

                    # Wikipedia API uchun kichik pauza
                    await asyncio.sleep(0.5)

                except Exception as e:
                    logger.warning(f"⚠️ Wiki xato ({club.name_en}): {e}")
                    continue

            await session.commit()

        logger.info(f"✅ {updated_count} ta klub Wiki bilan yangilandi")
        return updated_count

    async def sync_matches(
        self, league_code: str, season: int | None = None
    ) -> list[Match]:
        """
        Liga o'yinlarini API dan olib, bazaga sinxronlashtirish.

        Args:
            league_code: Liga kodi
            season: Mavsum yili (None = joriy)

        Returns:
            Saqlangan Match ob'yektlari ro'yxati
        """
        logger.info(f"⚽ O'YINLAR SINXRONIZATSIYASI: {league_code}")

        matches_data = await self.fetch_matches(league_code, season)
        synced: list[Match] = []

        async with async_session() as session:
            result = await session.execute(
                select(League).where(League.code == league_code)
            )
            league = result.scalar_one_or_none()

            if not league:
                logger.error(f"❌ Liga topilmadi DB da: {league_code}")
                return []

            for match_data in matches_data:
                match = await self._upsert_match(session, match_data, league.id)
                if match:
                    synced.append(match)

            await session.commit()

        logger.info(f"✅ {len(synced)} ta o'yin sinxronlashtirildi: {league_code}")
        return synced

    async def sync_standings(
        self, league_code: str, season: int | None = None
    ) -> list[Standing]:
        """
        Liga turni jadvalini API dan olib, bazaga sinxronlashtirish.

        Args:
            league_code: Liga kodi
            season: Mavsum yili (None = joriy)

        Returns:
            Saqlangan Standing ob'yektlari ro'yxati
        """
        logger.info(f"📊 JADVAL SINXRONIZATSIYASI: {league_code}")

        standings_data = await self.fetch_standings(league_code, season)
        synced: list[Standing] = []

        async with async_session() as session:
            result = await session.execute(
                select(League).where(League.code == league_code)
            )
            league = result.scalar_one_or_none()

            if not league:
                logger.error(f"❌ Liga topilmadi DB da: {league_code}")
                return []

            # Mavsum yilini aniqlash
            actual_season = season
            if actual_season is None:
                # API javobdagi season_info dan olish
                if standings_data and "_season_info" in standings_data[0]:
                    season_info = standings_data[0]["_season_info"]
                    start_date = season_info.get("startDate", "")
                    actual_season = int(start_date[:4]) if start_date else 2024
                else:
                    actual_season = datetime.utcnow().year

            for entry in standings_data:
                # _season_info ichki maydonini tozalash
                entry.pop("_season_info", None)

                standing = await self._upsert_standing(
                    session,
                    entry,
                    league.id,
                    actual_season,
                    league.current_matchday,
                )
                if standing:
                    synced.append(standing)

            await session.commit()

        logger.info(
            f"✅ {len(synced)} ta jadval yozuvi sinxronlashtirildi: {league_code}"
        )
        return synced

    async def sync_all(
        self, league_codes: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Barcha ma'lumotlarni to'liq sinxronlashtirish.

        Tartib:
          1. Ligalar
          2. Har bir liga uchun: Jamoalar → O'yinlar → Jadval
          3. Wikipedia ma'lumotlari

        Args:
            league_codes: Liga kodlari ['PL','PD',...]. None bo'lsa barchasi.

        Returns:
            Sinxronizatsiya natijalari statistikasi
        """
        codes = league_codes or list(self.SUPPORTED_LEAGUES.keys())
        start_time = time.monotonic()

        logger.info("=" * 60)
        logger.info("🚀 TO'LIQ SINXRONIZATSIYA BOSHLANDI")
        logger.info(f"📌 Ligalar: {', '.join(codes)}")
        logger.info("=" * 60)

        stats: dict[str, Any] = {
            "leagues": 0,
            "clubs": 0,
            "matches": 0,
            "standings": 0,
            "wiki": 0,
            "errors": [],
        }

        # 1-qadam: Ligalarni sinxronlashtirish
        try:
            synced_leagues = await self.sync_leagues(codes)
            stats["leagues"] = len(synced_leagues)
        except Exception as e:
            logger.error(f"❌ Ligalar sync xatosi: {e}")
            stats["errors"].append(f"Ligalar: {e}")

        # 2-qadam: Har bir liga uchun jamoalar, o'yinlar, jadval
        for code in codes:
            # Jamoalar
            try:
                synced_clubs = await self.sync_clubs(code)
                stats["clubs"] += len(synced_clubs)
            except Exception as e:
                logger.error(f"❌ Jamoalar sync xatosi ({code}): {e}")
                stats["errors"].append(f"Jamoalar ({code}): {e}")

            # O'yinlar
            try:
                synced_matches = await self.sync_matches(code)
                stats["matches"] += len(synced_matches)
            except Exception as e:
                logger.error(f"❌ O'yinlar sync xatosi ({code}): {e}")
                stats["errors"].append(f"O'yinlar ({code}): {e}")

            # Jadval
            try:
                synced_standings = await self.sync_standings(code)
                stats["standings"] += len(synced_standings)
            except Exception as e:
                logger.error(f"❌ Jadval sync xatosi ({code}): {e}")
                stats["errors"].append(f"Jadval ({code}): {e}")

        # 3-qadam: Wikipedia ma'lumotlari (faqat bo'sh bo'lganlar uchun)
        try:
            wiki_count = await self.sync_wikipedia()
            stats["wiki"] = wiki_count
        except Exception as e:
            logger.error(f"❌ Wikipedia sync xatosi: {e}")
            stats["errors"].append(f"Wikipedia: {e}")

        elapsed = time.monotonic() - start_time
        stats["elapsed_seconds"] = round(elapsed, 1)

        logger.info("=" * 60)
        logger.info("🏁 TO'LIQ SINXRONIZATSIYA TUGADI")
        logger.info(f"📊 Natija: {stats}")
        logger.info(f"⏱️ Vaqt: {elapsed:.1f}s")
        logger.info("=" * 60)

        return stats


# Singleton instance - boshqa modullardan import qilish uchun
football_data_service = FootballDataService()
