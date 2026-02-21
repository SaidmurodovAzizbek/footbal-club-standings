import json

with open("api_test_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("Checking empty or null fields in Team:")
team = data.get("team", {})
for k, v in team.items():
    if v is None or v == "" or v == []:
        print(f"  Empty/Null in Team: {k}")

print("\nChecking empty or null fields in Match:")
match = data.get("match", {})
for k, v in match.items():
    if v is None or v == "" or v == []:
        print(f"  Empty/Null in Match: {k}")

# Also check Team's coach and squad
print("\nTeam Coach:", team.get("coach"))
print("Team Squad count:", len(team.get("squad", [])))

# Let's see some Match score details
print("\nMatch Score:")
print(json.dumps(match.get("score"), indent=2))
