# database.py (DEFINITIVE FINAL - This is the one-time setup script)
import csv
import sqlite3
import os
import pandas as pd
from config import DATABASE_NAME, VERIFIED_COORDINATES, STATIONS_TO_EXCLUDE, KAJANG_LINE, KELANA_JAYA_LINE, INTERCHANGE_STATIONS

DB_FILE = DATABASE_NAME
FARE_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Fare.csv')
TIME_CSV_PATH = os.path.join(os.path.dirname(__file__), 'data', 'Time.csv')

def initialize_database():
    """Performs a one-time ETL process to create a clean SQLite database."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("[INFO] Creating database schema...")
    cursor.execute('DROP TABLE IF EXISTS fares')
    cursor.execute('DROP TABLE IF EXISTS times')
    cursor.execute('DROP TABLE IF EXISTS connections') # Added routes table drop for older versions
    cursor.execute('DROP TABLE IF EXISTS stations')
    cursor.execute('CREATE TABLE stations (name TEXT PRIMARY KEY, latitude REAL, longitude REAL)')
    cursor.execute('CREATE TABLE fares (origin TEXT, destination TEXT, price REAL)')
    cursor.execute('CREATE TABLE times (origin TEXT, destination TEXT, minutes INT)')
    cursor.execute('CREATE TABLE connections (origin_name TEXT, destination_name TEXT)')

    print("\n--- Step 1: Transforming and Loading Data ---")
    
    fare_df = pd.read_csv(FARE_CSV_PATH, index_col=0)
    time_df = pd.read_csv(TIME_CSV_PATH, index_col=0)

    for df in [fare_df, time_df]:
        df.columns = df.columns.str.strip()
        df.index = df.index.str.strip()
        df.drop(index=STATIONS_TO_EXCLUDE, errors='ignore', inplace=True)
        df.drop(columns=STATIONS_TO_EXCLUDE, errors='ignore', inplace=True)
    
    station_names = sorted(list(fare_df.index))
    
    stations_to_insert = []
    for name in station_names:
        coords = VERIFIED_COORDINATES.get(name, {"lat": None, "lon": None})
        stations_to_insert.append((name, coords["lat"], coords["lon"]))
    cursor.executemany('INSERT INTO stations (name, latitude, longitude) VALUES (?, ?, ?)', stations_to_insert)
    print(f"[SUCCESS] Loaded {len(stations_to_insert)} stations into database.")
    
    fares_to_load = fare_df.stack().reset_index()
    fares_to_load.columns = ['origin', 'destination', 'price']
    fares_to_load.to_sql('fares', conn, if_exists='append', index=False)
    
    times_to_load = time_df.stack().reset_index()
    times_to_load.columns = ['origin', 'destination', 'minutes']
    times_to_load.to_sql('times', conn, if_exists='append', index=False)
    
    # --- THIS IS THE MISSING LOGIC ---
    print("\n--- Step 2: Ingesting direct connections ---")
    connections_to_add = set()
    all_lines = [KELANA_JAYA_LINE, KAJANG_LINE]
    for line in all_lines:
        for i in range(len(line) - 1):
            connections_to_add.add(tuple(sorted((line[i], line[i+1]))))
    for station1, station2 in INTERCHANGE_STATIONS.items():
        connections_to_add.add(tuple(sorted((station1, station2))))
    cursor.executemany('INSERT INTO connections (origin_name, destination_name) VALUES (?, ?)', list(connections_to_add))
    print(f"[SUCCESS] Ingested {cursor.rowcount} unique direct connection entries.")

    conn.commit()
    conn.close()
    print("\n--- Database Initialization Complete ---")

if __name__ == "__main__":
    initialize_database()