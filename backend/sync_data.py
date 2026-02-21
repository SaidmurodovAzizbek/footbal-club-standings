"""
FCS Sinxronizatsiya Scripti.
Football-Data.org dan ma'lumotlarni bazaga tortish.

Foydalanish:
  python sync_data.py PL           # Faqat Premier League
  python sync_data.py PL PD SA     # Bir nechta liga
  python sync_data.py              # Barcha ligalar
"""
import asyncio
import sys
import signal
import logging

# Logging yoqish
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
# SQLAlchemy engine loglarini o'chirish (juda ko'p chiqadi)
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# Windows uchun signal handling
if sys.platform == "win32":
    signal.signal(signal.SIGINT, signal.SIG_DFL)


async def main():
    from app.services.football_data import football_data_service

    # Qaysi ligalarni sinxronlashtirish
    league_codes = sys.argv[1:] if len(sys.argv) > 1 else ["PL"]

    print(f"\n{'='*60}")
    print(f"🚀 FCS Sinxronizatsiya boshlandi!")
    print(f"📌 Ligalar: {', '.join(league_codes)}")
    print(f"{'='*60}\n")

    try:
        stats = await football_data_service.sync_all(league_codes)

        print(f"\n{'='*60}")
        print(f"🏁 Natija:")
        print(f"  📋 Ligalar:  {stats.get('leagues', 0)}")
        print(f"  👥 Jamoalar: {stats.get('clubs', 0)}")
        print(f"  ⚽ O'yinlar: {stats.get('matches', 0)}")
        print(f"  📊 Jadval:   {stats.get('standings', 0)}")
        print(f"  📚 Wiki:     {stats.get('wiki', 0)}")
        print(f"  ⏱️  Vaqt:     {stats.get('elapsed_seconds', 0)}s")
        if stats.get("errors"):
            print(f"  ❌ Xatolar:")
            for err in stats["errors"]:
                print(f"     - {err}")
        print(f"{'='*60}\n")
    except KeyboardInterrupt:
        print("\n⛔ Sinxronizatsiya foydalanuvchi tomonidan to'xtatildi.")
    except Exception as e:
        print(f"\n❌ Xato: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Windows uchun ProactorEventLoop muammosini hal qilish
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
