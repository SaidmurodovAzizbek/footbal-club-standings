from sqlalchemy import String, Integer, Boolean, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List
from datetime import date

from app.models.base import Base, TimestampMixin


class League(Base, TimestampMixin):
    """Liga modeli - futbol ligalari (Premier League, La Liga, va h.k.)"""

    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True, comment="Football-Data.org ID")

    # Lokalizatsiya maydonlari
    name_en: Mapped[str] = mapped_column(String(255), nullable=False, comment="Liga nomi (inglizcha)")
    name_uz: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Liga nomi (o'zbekcha)")

    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, comment="Liga kodi (PL, BL1, SA ...)")
    country: Mapped[str] = mapped_column(String(100), nullable=False, comment="Mamlakat nomi")

    # Emblem/rasm
    emblem_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Original emblem URL")
    emblem_local: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Lokal saqlangan emblem yo'li")

    # Mavsum ma'lumotlari
    season_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="Mavsum boshlanish sanasi")
    season_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True, comment="Mavsum tugash sanasi")
    current_matchday: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Hozirgi o'yin kuni")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Liga faolmi?")

    # Munosabatlar (relationships)
    clubs: Mapped[List["Club"]] = relationship("Club", back_populates="league", lazy="selectin")
    matches: Mapped[List["Match"]] = relationship("Match", back_populates="league", lazy="selectin")
    standings: Mapped[List["Standing"]] = relationship("Standing", back_populates="league", lazy="selectin")

    def __repr__(self) -> str:
        return f"<League(id={self.id}, name='{self.name_en}', code='{self.code}')>"

    def get_name(self, lang: str = "en") -> str:
        """Tanlangan tildagi nomni qaytaradi."""
        if lang == "uz" and self.name_uz:
            return self.name_uz
        return self.name_en
