import json

def print_structure(d, indent=0):
    if isinstance(d, dict):
        for k, v in d.items():
            print("  " * indent + str(k))
            if isinstance(v, (dict, list)):
                print_structure(v, indent + 1)
    elif isinstance(d, list) and len(d) > 0:
        print_structure(d[0], indent)

with open("api_test_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== LEAGUE ===")
print_structure(data["league"])
print("\n=== TEAM ===")
print_structure(data["team"])
print("\n=== STANDING ===")
print_structure(data["standing"])
print("\n=== MATCH ===")
print_structure(data["match"])
