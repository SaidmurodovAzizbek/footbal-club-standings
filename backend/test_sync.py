import asyncio
import httpx
import sqlite3

async def test_sync_and_verify():
    print("Triggering sync for PL...")
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Since the argument might be interpreted as query or body, let's send body
        response = await client.post("http://127.0.0.1:8000/api/v1/sync", json=["PL"])
        print("Sync Response:", response.status_code, response.json())
        
    print("\nVerifying database...")
    conn = sqlite3.connect("fcs.db")
    cursor = conn.cursor()
    
    # Check clubs for coach
    cursor.execute("SELECT name_en, coach_name FROM clubs WHERE tla='ARS'")
    row = cursor.fetchone()
    print("Arsenal Coach:", row)
    
    # Check matches for winner
    cursor.execute("SELECT home_team_id, away_team_id, winner FROM matches LIMIT 5")
    rows = cursor.fetchall()
    print("Recent matches winner fields:")
    for r in rows:
        print(f"  Match {r[0]} vs {r[1]} -> Winner: {r[2]}")
        
    conn.close()

if __name__ == "__main__":
    asyncio.run(test_sync_and_verify())
