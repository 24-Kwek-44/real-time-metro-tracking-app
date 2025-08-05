import csv
import sqlite3
import os

DB_NAME = 'db.sqlite'
def get_db_connection():
    """Establish a connection to the database and set row factory."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Create the database and both tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS station (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_name TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            route TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fare_matrix (
            fare_id INTEGER,
            station_name TEXT NOT NULL,
            destination_name TEXT NOT NULL,
            price REAL
        )
    ''')

    conn.commit()
    conn.close()
    print("Database and both tables are ready.")

def extract_line_and_name(cell):
    """Extract line prefix and station name from 'SBK[Kajang]' or just 'Kajang'."""
    cell = cell.strip()
    if "[" in cell and "]" in cell:
        prefix = cell.split("[")[0].strip()
        name = cell.split("[")[1].replace("]", "").strip()
    else:
        prefix = ""
        name = cell
    return prefix, name

def ingest_route(file_path):
    """Read route CSV and insert data into the database."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

        destinations = data[0][1:]  # First row, skipping the top-left cell

        for i in range(1, len(data)):
            row = data[i]
            origin_name = row[0].strip()

            for j in range(1, len(row)):
                dest_name = destinations[j - 1].strip()
                route_str = row[j].strip()

                if not route_str:
                    continue  # skip empty cells

                try:
                    cursor.execute('''
                        INSERT INTO station (station_name, destination_name, route)
                        VALUES (?, ?, ?)
                    ''', (origin_name, dest_name, route_str))
                except Exception as e:
                    print(f"Error inserting route {origin_name} -> {dest_name}: {e}")

    conn.commit()
    conn.close()
    print("Route matrix ingested successfully.")

def ingest_fares(file_path):
    """Read fare CSV and insert data into the fare_matrix table."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

        destinations = data[0][1:]

        fare_id = 1

        for i in range(1, len(data)):
            row = data[i]
            origin_cell = row[0].strip()
            _, origin_name = extract_line_and_name(origin_cell)

            for j in range(1, len(row)):
                dest_cell = destinations[j - 1].strip()
                _, dest_name = extract_line_and_name(dest_cell)

                try:
                    price = float(row[j].strip())
                except:
                    price = None

                if origin_name and dest_name and price is not None:
                    cursor.execute('''
                        INSERT INTO fare_matrix (fare_id, station_name, destination_name, price)
                        VALUES (?, ?, ?, ?)
                    ''', (fare_id, origin_name, dest_name, price))
                    fare_id += 1

    conn.commit()
    conn.close()
    print("Fare data ingested.")

if __name__ == "__main__":
    create_database()

    if not os.path.exists("data/Route.csv"):
        print("route.csv not found.")
    else:
        ingest_route("data/Route.csv")

    if not os.path.exists("data/Fare.csv"):
        print("Fare.csv not found.")
    else:
        ingest_fares("data/Fare.csv")
