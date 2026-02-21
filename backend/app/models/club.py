from sqlalchemy import String, Integer, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, TYPE_CHECKING

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.league import League
    from app.models.match import Match
    from app.models.standing import Standing


class Club(Base, TimestampMixin):
    """Klub modeli - futbol klublari (Manchester United, Real Madrid, va h.k.)"""

    __tablename__ = "clubs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True, comment="Football-Data.org ID")
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)

    # Lokalizatsiya maydonlari
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, comment="Klub nomi (inglizcha)")
    name_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Klub nomi (o'zbekcha)")

    short_name: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Qisqa nomi")
    tla: Mapped[Optional[str]] = mapped_column(String(5), nullable=True, comment="3-harfli qisqartma (MUN, ARS ...)")

    # Rasm/logo
    crest_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Original club crest URL")
    crest_local: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Lokal saqlangan crest yo'li")

    # Klub ma'lumotlari
    founded: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Tashkil etilgan yili")
    venue: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Stadion nomi")
    venue_image_local: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Stadion rasmi (lokal)")
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Rasmiy veb-sayt")
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Klub manzili")

    # Wikipedia ma'lumotlari
    wiki_summary_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Wikipedia qisqa tavsifi (EN)")
    wiki_summary_uz: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Wikipedia qisqa tavsifi (UZ)")

    # Rang
    club_colors: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Klub ranglari")

    # Murabbiy
    coach_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Bosh murabbiy ismi")

    # Munosabatlar
    league: Mapped["League"] = relationship("League", back_populates="clubs")
    home_matches: Mapped[List["Match"]] = relationship("Match", back_populates="home_team", foreign_keys="Match.home_team_id", lazy="selectin")
    away_matches: Mapped[List["Match"]] = relationship("Match", back_populates="away_team", foreign_keys="Match.away_team_id", lazy="selectin")
    standings: Mapped[List["Standing"]] = relationship("Standing", back_populates="club", lazy="selectin")

    def __repr__(self) -> str:
        return f"<Club(id={self.id}, name='{self.name_en}', tla='{self.tla}')>"

    def get_name(self, lang: str = "en") -> str:
        """Tanlangan tildagi nomni qaytaradi."""
        if lang == "uz" and self.name_uz:
            return self.name_uz
        return self.name_en
