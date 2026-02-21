import asyncio
import json
import httpx

API_KEY = "ae68b3b1d55f46d9a8372b4366725ff8"
BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": API_KEY}

async def fetch_and_save():
    async with httpx.AsyncClient() as client:
        # League
        res_league = await client.get(f"{BASE_URL}/competitions/PL", headers=HEADERS)
        league_data = res_league.json()
        
        # Teams
        res_teams = await client.get(f"{BASE_URL}/competitions/PL/teams", headers=HEADERS)
        teams_data = res_teams.json()
        
        # Standings
        res_standings = await client.get(f"{BASE_URL}/competitions/PL/standings", headers=HEADERS)
        standings_data = res_standings.json()
        
        # Matches
        res_matches = await client.get(f"{BASE_URL}/competitions/PL/matches?status=FINISHED&limit=2", headers=HEADERS)
        matches_data = res_matches.json()
        
        with open("api_test_results.json", "w", encoding="utf-8") as f:
            json.dump({
                "league": league_data,
                "team": teams_data.get("teams", [])[0] if teams_data.get("teams") else None,
                "standing": standings_data.get("standings", [{}])[0].get("table", [])[0] if standings_data.get("standings") else None,
                "match": matches_data.get("matches", [])[0] if matches_data.get("matches") else None
            }, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    asyncio.run(fetch_and_save())
