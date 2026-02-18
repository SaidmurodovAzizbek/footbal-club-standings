import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class WikipediaAPIClient:
    """
    Wikipedia API bilan ishlash uchun klient.
    Klub tarixi va stadion ma'lumotlarini olish uchun ishlatiladi.
    """

    BASE_URL = "https://en.wikipedia.org/api/rest_v1"
    UZ_BASE_URL = "https://uz.wikipedia.org/api/rest_v1"

    async def _fetch_summary(self, title: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Wikipedia sahifa xulosasini olish."""
        base = self.UZ_BASE_URL if lang == "uz" else self.BASE_URL
        url = f"{base}/page/summary/{title}"
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"Wikipedia sahifa topilmadi: {title} ({lang})")
                return None
        except httpx.RequestError as e:
            logger.error(f"Wikipedia so'rov xatosi: {e}")
            return None

    async def get_club_summary(self, club_name: str, lang: str = "en") -> Optional[str]:
        """
        Klub haqida qisqa ma'lumot olish.
        Masalan: 'Manchester_United_F.C.' -> qisqa tavsif
        """
        # Wikipedia sarlavhasi uchun nomdagi bo'shliqlarni almashtirish
        wiki_title = club_name.replace(" ", "_")
        data = await self._fetch_summary(wiki_title, lang)
        if data and "extract" in data:
            return data["extract"]
        return None

    async def get_club_image(self, club_name: str) -> Optional[str]:
        """Klub Wikipedia sahifasidagi asosiy rasmni URL sini olish."""
        wiki_title = club_name.replace(" ", "_")
        data = await self._fetch_summary(wiki_title)
        if data and "thumbnail" in data:
            return data["thumbnail"].get("source")
        return None

    async def get_stadium_info(self, stadium_name: str, lang: str = "en") -> Optional[Dict[str, Any]]:
        """Stadion haqida ma'lumot olish."""
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
