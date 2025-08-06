import csv
import sqlite3
import os

# --- Constants ---
DB_NAME = 'db.sqlite'


# --- Core Database Functions ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_database_schema():
    print("Creating database schema...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # The 'station' table stores direct station-to-station connections and the route description.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS station (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            route TEXT NOT NULL
        )
    ''')

    # The 'fare_matrix' table stores the fare for a trip between an origin and a destination.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fare_matrix (
            station_name TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            price REAL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database schema is ready.")


# --- Data Ingestion and Parsing ---
def _extract_station_name(cell_text):
    cell_text = cell_text.strip()
    if "[" in cell_text and "]" in cell_text:
        # Extracts 'Kajang' from 'SBK[Kajang]'
        return cell_text.split("[")[1].replace("]", "").strip()
    return cell_text


def ingest_data_from_csv(file_path, table_name):
    print(f"Ingesting data from {os.path.basename(file_path)} into '{table_name}'...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            # The first row contains the destination station names.
            destinations = next(reader)[1:]
            
            for row in reader:
                origin_cell = row[0]
                
                # Iterate through each cell in the row, pairing it with a destination.
                for i, cell_value in enumerate(row[1:]):
                    # Skip empty cells or cells with placeholder values.
                    if not cell_value or cell_value.strip() == '-':
                        continue  

                    dest_cell = destinations[i]

                    if table_name == 'station':
                        cursor.execute(
                            'INSERT INTO station (station_name, destination_name, route) VALUES (?, ?, ?)',
                            (origin_cell, dest_cell, cell_value)
                        )
                    elif table_name == 'fare_matrix':
                        origin_name = _extract_station_name(origin_cell)
                        dest_name = _extract_station_name(dest_cell)
                        price = float(cell_value)
                        cursor.execute(
                            'INSERT INTO fare_matrix (station_name, destination_name, price) VALUES (?, ?, ?)',
                            (origin_name, dest_name, price)
                        )
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}. Skipping ingestion.")
        return 
    except Exception as e:
        print(f"An unexpected error occurred during ingestion from {file_path}: {e}")
        return

    conn.commit()
    conn.close()
    print(f"Successfully ingested data into '{table_name}'.")


def initialize_database():
    print("--- Starting Database Initialization ---")
    create_database_schema()
    ingest_data_from_csv("data/Route.csv", "station")
    ingest_data_from_csv("data/Fare.csv", "fare_matrix")
    print("--- Database Initialization Complete ---")


# This block allows the script to be run directly from the command line
# to set up the database.
if __name__ == "__main__":
    initialize_database()