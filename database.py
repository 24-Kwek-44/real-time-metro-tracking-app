import csv
import sqlite3
import os
import time
from geopy.geocoders import Nominatim
from config import DATABASE_NAME

DB_FILE = DATABASE_NAME
FARE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Fare.csv')
ROUTE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Route.csv')

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_database_schema():
    print("[INFO] Creating database schema with coordinate support...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS fares')
    cursor.execute('DROP TABLE IF EXISTS connections')
    cursor.execute('DROP TABLE IF EXISTS stations')
    
    # The stations table now includes latitude and longitude
    cursor.execute('CREATE TABLE stations (name TEXT PRIMARY KEY, latitude REAL, longitude REAL)')
    cursor.execute('CREATE TABLE connections (origin_name TEXT, destination_name TEXT)')
    cursor.execute('CREATE TABLE fares (origin_name TEXT, destination_name TEXT, price REAL)')
    conn.commit()
    conn.close()
    print("[INFO] Database schema created successfully.")

def initialize_database():
    create_database_schema()
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Step 1: Discover all unique stations ---
    print("\n--- Step 1: Discovering all unique stations from Fare.csv ---")
    station_names = set()
    with open(FARE_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)[1:]
        station_names.update(h.strip() for h in headers)
        for row in reader:
            station_names.add(row[0].strip())
    
    # --- Step 2: Geocode stations and insert into database ---
    print(f"\n--- Step 2: Geocoding {len(station_names)} stations (this will take a few minutes) ---")
    geolocator = Nominatim(user_agent="metro_tracker_app_kwek_v1")
    stations_to_insert = []
    
    for name in sorted(list(station_names)):
        lat, lon = None, None
        try:
            # Add context to the query for better accuracy
            query = f"{name} Station, Kuala Lumpur"
            location = geolocator.geocode(query, timeout=10)
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"  [SUCCESS] Found coordinates for {name}: ({lat:.4f}, {lon:.4f})")
            else:
                print(f"  [WARNING] Could not find coordinates for {name}.")
            
            # IMPORTANT: Nominatim has a strict usage policy of 1 request per second.
            time.sleep(1.1) # Wait slightly more than 1 second to be safe.
        except Exception as e:
            print(f"  [ERROR] An error occurred while geocoding {name}: {e}")
        
        stations_to_insert.append((name, lat, lon))

    cursor.executemany('INSERT INTO stations (name, latitude, longitude) VALUES (?, ?, ?)', stations_to_insert)
    conn.commit()
    print("[SUCCESS] Finished geocoding and inserting stations.")

    # --- Step 3 & 4: Ingest fares and connections (no changes to this logic) ---
    print("\n--- Step 3: Ingesting fares ---")
    # ... (fare ingestion logic is the same) ...
    fares_added = 0
    with open(FARE_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        dest_names = next(reader)[1:]
        for row in reader:
            origin_name = row[0].strip()
            for i, cell_value in enumerate(row[1:]):
                if cell_value and cell_value.strip() not in ['', '-']:
                    dest_name = dest_names[i].strip()
                    price = float(cell_value)
                    cursor.execute('INSERT INTO fares (origin_name, destination_name, price) VALUES (?, ?, ?)', (origin_name, dest_name, price))
                    fares_added += 1
    conn.commit()
    print(f"[SUCCESS] Ingested {fares_added} fare entries.")

    print("\n--- Step 4: Ingesting connections ---")
    # ... (connection ingestion logic is the same) ...
    connections_added = 0
    with open(ROUTE_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        dest_names = next(reader)[1:]
        for row in reader:
            origin_name = row[0].strip()
            for i, cell_value in enumerate(row[1:]):
                if cell_value and cell_value.strip() not in ['', '-']:
                    dest_name = dest_names[i].strip()
                    cursor.execute('INSERT INTO connections (origin_name, destination_name) VALUES (?, ?)', (origin_name, dest_name))
                    connections_added += 1
    conn.commit()
    print(f"[SUCCESS] Ingested {connections_added} connection entries.")
    
    conn.close()
    print("\n--- Database Initialization Complete ---")

if __name__ == "__main__":
    initialize_database()