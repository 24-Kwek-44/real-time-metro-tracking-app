# database.py (FINAL with Real Geocoding)
import csv
import sqlite3
import os
import time
from geopy.geocoders import Nominatim  # <-- NEW IMPORT
from config import DATABASE_NAME

DB_FILE = DATABASE_NAME
FARE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Fare.csv')
ROUTE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Route.csv')

def get_db_connection():
    # ... (no change) ...
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_database_schema():
    """Creates tables, now including latitude and longitude columns."""
    print("[INFO] Creating database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS fares')
    cursor.execute('DROP TABLE IF EXISTS connections')
    cursor.execute('DROP TABLE IF EXISTS stations')
    
    # Add latitude and longitude columns to the stations table
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

    # --- Step 1: Discover all unique stations from Fare.csv ---
    print("\n--- Step 1: Discovering all unique stations ---")
    station_names = set()
    with open(FARE_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)[1:]
        station_names.update(h.strip() for h in headers)
        for row in reader:
            station_names.add(row[0].strip())
            
    print(f"[INFO] Discovered {len(station_names)} unique stations. Now fetching coordinates...")
    
    # --- NEW GEOCODING STEP ---
    # Create a geolocator instance. The user_agent is required by Nominatim's policy.
    geolocator = Nominatim(user_agent="metro_tracker_app_kwek")
    
    stations_to_insert = []
    for name in sorted(list(station_names)):
        lat, lon = None, None
        try:
            # Construct a specific query for better accuracy
            query = f"{name} Station, Kuala Lumpur, Malaysia"
            location = geolocator.geocode(query, timeout=10)
            
            if location:
                lat, lon = location.latitude, location.longitude
                print(f"  [SUCCESS] Found coordinates for {name}: ({lat}, {lon})")
            else:
                print(f"  [WARNING] Could not find coordinates for {name}. It will be NULL.")
            
            # IMPORTANT: Nominatim has a strict usage policy of 1 request per second.
            time.sleep(1) # Wait for 1 second before the next API call.

        except Exception as e:
            print(f"  [ERROR] An error occurred while geocoding {name}: {e}")

        stations_to_insert.append((name, lat, lon))

    # Insert all stations with their newly found coordinates
    cursor.executemany('INSERT INTO stations (name, latitude, longitude) VALUES (?, ?, ?)', stations_to_insert)
    conn.commit()
    print(f"[SUCCESS] Finished processing all stations.")

    # --- Steps 2 & 3: Ingest fares and connections (no changes to this logic) ---
    # ... (The rest of the script is the same as the last working version) ...
    print("\n--- Step 2: Ingesting fares ---")
    fares_added = 0
    with open(FARE_CSV_PATH, newline='', encoding='utf-8') as f:
        # ... (same fare ingestion logic) ...
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
    
    print("\n--- Step 3: Ingesting connections ---")
    connections_added = 0
    with open(ROUTE_CSV_PATH, newline='', encoding='utf-8') as f:
        # ... (same connection ingestion logic) ...
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