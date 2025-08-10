import csv
import sqlite3
import os
from config import DATABASE_NAME

DB_FILE = DATABASE_NAME
# --- Create robust, absolute paths to the data files ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FARE_CSV_PATH = os.path.join(BASE_DIR, 'data', 'Fare.csv')
ROUTE_CSV_PATH = os.path.join(BASE_DIR, 'data', 'Route.csv')

def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_database_schema():
    """Creates all required database tables, dropping old ones if they exist."""
    print("[INFO] Creating database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DROP TABLE IF EXISTS fares')
    cursor.execute('DROP TABLE IF EXISTS connections')
    cursor.execute('DROP TABLE IF EXISTS stations')
    
    cursor.execute('CREATE TABLE stations (name TEXT PRIMARY KEY)')
    cursor.execute('CREATE TABLE connections (origin_name TEXT, destination_name TEXT)')
    cursor.execute('CREATE TABLE fares (origin_name TEXT, destination_name TEXT, price REAL)')

    conn.commit()
    conn.close()
    print("[INFO] Database schema created successfully.")

def initialize_database():
    """Orchestrates the entire database setup process."""
    create_database_schema()
    conn = get_db_connection()
    cursor = conn.cursor()

    # --- Step 1: Discover all unique stations from Fare.csv ---
    print("\n--- Step 1: Discovering all unique stations ---")
    if not os.path.exists(FARE_CSV_PATH):
        print(f"[FATAL ERROR] {FARE_CSV_PATH} not found. Aborting.")
        return
        
    station_names = set()
    with open(FARE_CSV_PATH, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)[1:]
        for name in headers:
            station_names.add(name.strip())
        for row in reader:
            station_names.add(row[0].strip())
            
    # Insert all discovered stations into the stations table
    for name in sorted(list(station_names)):
        cursor.execute('INSERT INTO stations (name) VALUES (?)', (name,))
    conn.commit()
    print(f"[SUCCESS] Discovered and inserted {len(station_names)} unique stations.")

    # --- Step 2: Ingest fares from Fare.csv ---
    print("\n--- Step 2: Ingesting fares ---")
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

    # --- Step 3: Ingest connections from Route.csv ---
    print("\n--- Step 3: Ingesting connections ---")
    if not os.path.exists(ROUTE_CSV_PATH):
        print(f"[ERROR] {ROUTE_CSV_PATH} not found. Skipping.")
    else:
        connections_added = 0
        with open(ROUTE_CSV_PATH, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            dest_names = next(reader)[1:]
            for row in reader:
                origin_name = row[0].strip()
                for i, cell_value in enumerate(row[1:]):
                    # We only care that a connection exists, not what the route string says.
                    if cell_value and cell_value.strip() not in ['', '-']:
                        dest_name = dest_names[i].strip()
                        cursor.execute('INSERT INTO connections (origin_name, destination_name) VALUES (?, ?)', (origin_name, dest_name))
                        connections_added += 1
        conn.commit()
        print(f"[SUCCESS] Ingested {connections_added} connection entries.")
    
    # --- FINAL VERIFICATION ---
    print("\n--- Final Verification ---")
    stations_count = cursor.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
    fares_count = cursor.execute("SELECT COUNT(*) FROM fares").fetchone()[0]
    connections_count = cursor.execute("SELECT COUNT(*) FROM connections").fetchone()[0]
    print(f"  [RESULT] Stations table has: {stations_count} rows.")
    print(f"  [RESULT] Fares table has: {fares_count} rows.")
    print(f"  [RESULT] Connections table has: {connections_count} rows.")

    conn.close()
    print("\n--- Database Initialization Complete ---")

if __name__ == "__main__":
    initialize_database()