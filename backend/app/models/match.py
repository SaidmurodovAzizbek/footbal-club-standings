from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.league import League
    from app.models.club import Club


class Match(Base, TimestampMixin):
    """O'yin modeli - futbol o'yinlari natijalari va jadvali."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False, index=True, comment="Football-Data.org ID")
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)

    # O'yin ma'lumotlari
    matchday: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="O'yin kuni raqami")
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="SCHEDULED",
        comment="O'yin holati: SCHEDULED, TIMED, IN_PLAY, PAUSED, FINISHED, POSTPONED, CANCELLED"
    )
    utc_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, comment="O'yin sanasi (UTC)")

    # Jamoalar
    home_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)
    away_team_id: Mapped[int] = mapped_column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)

    # Natijalar
    home_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Uy jamoasi gollari")
    away_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Mehmon jamoasi gollari")
    home_score_ht: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Uy jamoasi gollari (1-taym)")
    away_score_ht: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Mehmon jamoasi gollari (1-taym)")
    winner: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="G'olib: HOME_TEAM, AWAY_TEAM yoki DRAW")

    # UCL uchun maxsus maydonlar
    stage: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Bosqich: REGULAR_SEASON, GROUP_STAGE, ROUND_OF_16, QUARTER_FINALS, SEMI_FINALS, FINAL"
    )
    group_name: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="UCL guruh nomi: Group A, B, C ...")

    # Hakam
    referee: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Bosh hakam ismi")

    # O'yin davomiyligi
    duration: Mapped[Optional[str]] = mapped_column(
        String(20),
        nullable=True,
        default="REGULAR",
        comment="Davomiylik: REGULAR, EXTRA_TIME, PENALTY_SHOOTOUT"
    )

    # Munosabatlar
    league: Mapped["League"] = relationship("League", back_populates="matches")
    home_team: Mapped["Club"] = relationship("Club", back_populates="home_matches", foreign_keys=[home_team_id])
    away_team: Mapped["Club"] = relationship("Club", back_populates="away_matches", foreign_keys=[away_team_id])

    def __repr__(self) -> str:
        return f"<Match(id={self.id}, home={self.home_team_id} vs away={self.away_team_id}, status='{self.status}')>"

    @property
    def is_live(self) -> bool:
        """O'yin hozir o'ynalayotganmi?"""
        return self.status in ("IN_PLAY", "PAUSED")

    @property
    def is_finished(self) -> bool:
        """O'yin tugaganmi?"""
        return self.status == "FINISHED"

    @property
    def score_display(self) -> str:
        """Natijani '2 - 1' formatida qaytaradi."""
        if self.home_score is not None and self.away_score is not None:
            return f"{self.home_score} - {self.away_score}"
        return "- - -"
