import httpx
from typing import Optional, Dict, Any, List
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class FootballAPIClient:
    """
    Football-Data.org API bilan ishlash uchun klient.
    Free-tier: 10 request/daqiqa cheklovi mavjud.
    """

    def __init__(self):
        self.base_url = settings.FOOTBALL_API_BASE_URL
        self.headers = {
            "X-Auth-Token": settings.FOOTBALL_API_KEY,
        }

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """API ga so'rov yuborish."""
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API xato: {e.response.status_code} - {endpoint}")
            return None
        except httpx.RequestError as e:
            logger.error(f"So'rov xatosi: {e} - {endpoint}")
            return None

    async def get_competitions(self) -> Optional[Dict[str, Any]]:
        """Barcha mavjud ligalarni olish."""
        return await self._make_request("/competitions")

    async def get_competition(self, competition_id: int) -> Optional[Dict[str, Any]]:
        """Bitta liga ma'lumotlarini olish."""
        return await self._make_request(f"/competitions/{competition_id}")

    async def get_standings(self, competition_id: int, season: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Liga turni jadvalini olish."""
        params = {}
        if season:
            params["season"] = season
        return await self._make_request(f"/competitions/{competition_id}/standings", params)

    async def get_matches(
        self,
        competition_id: int,
        matchday: Optional[int] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Liga o'yinlarini olish."""
        params = {}
        if matchday:
            params["matchday"] = matchday
        if status:
            params["status"] = status
        if date_from:
            params["dateFrom"] = date_from
        if date_to:
            params["dateTo"] = date_to
        return await self._make_request(f"/competitions/{competition_id}/matches", params)

    async def get_team(self, team_id: int) -> Optional[Dict[str, Any]]:
        """Jamoa tafsilotlarini olish."""
        return await self._make_request(f"/teams/{team_id}")

    async def get_competition_teams(self, competition_id: int) -> Optional[Dict[str, Any]]:
        """Ligadagi barcha jamoalarni olish."""
        return await self._make_request(f"/competitions/{competition_id}/teams")


# Singleton instance
football_api = FootballAPIClient()
