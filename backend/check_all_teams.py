import asyncio
import json
import httpx

API_KEY = "ae68b3b1d55f46d9a8372b4366725ff8"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

async def fetch_all_teams():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{BASE_URL}/competitions/PL/teams", headers=HEADERS)
        data = res.json()
        teams = data.get("teams", [])
        
        null_counts = {}
        empty_str_counts = {}
        for t in teams:
            for k, v in t.items():
                if v is None:
                    null_counts[k] = null_counts.get(k, 0) + 1
                elif v == "":
                    empty_str_counts[k] = empty_str_counts.get(k, 0) + 1
                
        print("Total teams:", len(teams))
        print("Null field counts:", null_counts)
        print("Empty string field counts:", empty_str_counts)

if __name__ == "__main__":
    asyncio.run(fetch_all_teams())
