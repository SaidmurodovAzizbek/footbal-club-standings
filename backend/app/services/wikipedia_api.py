import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WikipediaAPIClient:
    """
    Client for Wikipedia API.
    Used to fetch club history and stadium information.
    """

    BASE_URL = "https://en.wikipedia.org/api/rest_v1"
    UZ_BASE_URL = "https://uz.wikipedia.org/api/rest_v1"

    async def _fetch_summary(self, title: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Get Wikipedia page summary."""
        base = self.UZ_BASE_URL if lang == "uz" else self.BASE_URL
        url = f"{base}/page/summary/{title}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Wikipedia page not found: {title} ({lang})")
                return None
        except httpx.RequestError as e:
            logger.error(f"Wikipedia request error: {e}")
            return None

    async def get_club_summary(self, club_name: str, lang: str = "en") -> Optional[str]:
        """
        Get a short summary about the club.
        For example: 'Manchester_United_F.C.' -> summary description
        """
        # Replace spaces in the name for the Wikipedia title
        wiki_title = club_name.replace(" ", "_")
        data = await self._fetch_summary(wiki_title, lang)
        if data and "extract" in data:
            return data["extract"]
        return None

    async def get_club_image(self, club_name: str) -> Optional[str]:
        """Get the main image URL from the club's Wikipedia page."""
        wiki_title = club_name.replace(" ", "_")
        data = await self._fetch_summary(wiki_title)
        if data and "thumbnail" in data:
            return data["thumbnail"].get("source")
        return None

    async def get_stadium_info(self, stadium_name: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Get stadium information."""
        wiki_title = stadium_name.replace(" ", "_")
        data = await self._fetch_summary(wiki_title, lang)
        if data:
            return {
                "summary": data.get("extract"),
                "image": data.get("thumbnail", {}).get("source"),
            }
        return None


# Singleton instance
wikipedia_api = WikipediaAPIClient()
