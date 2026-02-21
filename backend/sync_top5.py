import asyncio
from app.services.football_data import football_data_service

async def main():
    print("Top 5 ligalarni sinxronlashtirish boshlandi...")
    
    # Faqat top 5 ligalarni kiritamiz
    codes = ['PL', 'PD', 'SA', 'BL1', 'FL1']
    
    try:
        stats = await football_data_service.sync_all(codes)
        print("\nSinxronizatsiya muvaffaqiyatli yakunlandi!")
        print("Natija statistikasi:")
        for k, v in stats.items():
            print(f"  - {k}: {v}")
    except Exception as e:
        print(f"\nXatolik yuz berdi: {e}")

if __name__ == "__main__":
    asyncio.run(main())
