import sqlite3

def verify():
    conn = sqlite3.connect("fcs.db")
    cursor = conn.cursor()
    
    print("--- CLUBS ---")
    cursor.execute("SELECT name_en, coach_name FROM clubs LIMIT 5")
    for r in cursor.fetchall():
        print(f"Club: {r[0]}, Coach: {r[1]}")
        
    print("\n--- MATCHES ---")
    cursor.execute("SELECT id, home_team_id, away_team_id, winner FROM matches WHERE winner IS NOT NULL LIMIT 5")
    for r in cursor.fetchall():
        print(f"Match {r[0]}: Team {r[1]} vs Team {r[2]} -> Winner: {r[3]}")
        
    conn.close()

if __name__ == "__main__":
    verify()
