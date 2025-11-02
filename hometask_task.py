import sqlite3
import math
import os

DB_FILE = "cities.db"

def init_db():
    """Initialize SQLite database if not exists."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cities (
            name TEXT PRIMARY KEY,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def get_city_coordinates(city_name: str):
    """Retrieve coordinates from DB, or ask user and store them."""
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT latitude, longitude FROM cities WHERE LOWER(name)=LOWER(?)", (city_name,))
    row = cur.fetchone()
    if row:
        conn.close()
        return row[0], row[1]
    else:
        print(f"Coordinates for '{city_name}' not found.")
        lat = float(input(f"Enter latitude for {city_name}: "))
        lon = float(input(f"Enter longitude for {city_name}: "))
        cur.execute("INSERT INTO cities (name, latitude, longitude) VALUES (?, ?, ?)",
                    (city_name, lat, lon))
        conn.commit()
        conn.close()
        print(f"Saved {city_name} ({lat}, {lon}) to database.")
        return lat, lon

def haversine(lat1, lon1, lat2, lon2):
    """Compute great-circle distance using Haversine formula."""
    R = 6371.0  # radius of Earth in km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def main():
    init_db()
    print("Straight-Line Distance Calculator ")
    city1 = input("Enter first city: ").strip()
    city2 = input("Enter second city: ").strip()

    lat1, lon1 = get_city_coordinates(city1)
    lat2, lon2 = get_city_coordinates(city2)

    distance = haversine(lat1, lon1, lat2, lon2)
    print(f"\nStraight-line distance between {city1} and {city2}: {distance:.2f} km\n")

if __name__ == "__main__":
    main()
