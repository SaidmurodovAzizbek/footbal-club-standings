from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.league import League
    from app.models.club import Club


class Standing(Base, TimestampMixin):
    """Turni jadval modeli - ligada klublarning o'rni va statistikasi."""

    __tablename__ = "standings"

    # Unikal cheklov: bir ligada bir klubning bir mavsumda bitta standing bo'lishi kerak
    __table_args__ = (
        UniqueConstraint("league_id", "club_id", "season", name="uq_standing_league_club_season"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    league_id: Mapped[int] = mapped_column(Integer, ForeignKey("leagues.id"), nullable=False, index=True)
    club_id: Mapped[int] = mapped_column(Integer, ForeignKey("clubs.id"), nullable=False, index=True)

    # Mavsum
    season: Mapped[int] = mapped_column(Integer, nullable=False, comment="Mavsum yili (2024/2025 -> 2024)")
    matchday: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="Hozirgi o'yin kuni")

    # Pozitsiya va statistikalar
    position: Mapped[int] = mapped_column(Integer, nullable=False, comment="Jadvaldagi o'rni")
    played: Mapped[int] = mapped_column(Integer, default=0, comment="O'ynalgan o'yinlar soni")
    won: Mapped[int] = mapped_column(Integer, default=0, comment="G'alabalar")
    draw: Mapped[int] = mapped_column(Integer, default=0, comment="Duranglar")
    lost: Mapped[int] = mapped_column(Integer, default=0, comment="Mag'lubiyatlar")
    goals_for: Mapped[int] = mapped_column(Integer, default=0, comment="Urilgan gollar")
    goals_against: Mapped[int] = mapped_column(Integer, default=0, comment="Yeyilgan gollar")
    goal_difference: Mapped[int] = mapped_column(Integer, default=0, comment="Gollar farqi")
    points: Mapped[int] = mapped_column(Integer, default=0, comment="Ochkolar")

    # Oxirgi natijalar
    form: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Oxirgi natijalar: W,W,D,L,W")

    # Munosabatlar
    league: Mapped["League"] = relationship("League", back_populates="standings")
    club: Mapped["Club"] = relationship("Club", back_populates="standings")

    def __repr__(self) -> str:
        return f"<Standing(position={self.position}, club_id={self.club_id}, points={self.points})>"
