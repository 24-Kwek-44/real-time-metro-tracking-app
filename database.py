import sqlite3

db = sqlite3.connect('db.sqlite')

db.execute('''CREATE TABLE IF NOT EXISTS station(
    station_id INTEGER PRIMARY KEY AUTOINCREMENT,
    station_name TEXT NOT NULL,
    destination_name TEXT NOT NULL,
    route TEXT NOT NULL

)''')

db.execute('''
CREATE TABLE IF NOT EXISTS fare_matrix (
    origin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    destination_id INTEGER,
    price REAL
)
''')    

cursor = db.cursor()


db.commit()
db.close()  


import sqlite3
import csv
import os

DB_NAME = 'db.sqlite'
ROUTE_CSV = 'Route.csv'
FARE_CSV = 'Fare.csv'
ROUTE_NAME = 'Kelana Jaya Line'


def create_tables():
    db = sqlite3.connect(DB_NAME)

    db.execute('''CREATE TABLE IF NOT EXISTS station (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT NOT NULL,
        destination_name TEXT NOT NULL,
        route TEXT NOT NULL
    )''')

    db.execute('''CREATE TABLE IF NOT EXISTS fare_matrix (
        origin_id INTEGER,
        destination_id INTEGER,
        price REAL,
        PRIMARY KEY (origin_id, destination_id)
    )''')

    db.commit()
    db.close()


# Utility: Build name → id mapping
def get_station_ids():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT DISTINCT station_name FROM station')
    station_names = {row[0] for row in cursor.fetchall()}

    all_names = list(station_names)
    name_to_id = {}

    for name in all_names:
        cursor.execute('''
            SELECT station_id FROM station
            WHERE station_name = ? LIMIT 1
        ''', (name,))
        result = cursor.fetchone()
        if result:
            name_to_id[name] = result[0]

    conn.close()
    return name_to_id


def ingest_route_matrix(file_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

        destinations = data[0][1:]

        for i in range(1, len(data)):
            row = data[i]
            origin_name = row[0]

            for j in range(1, len(row)):
                dest_name = destinations[j - 1]

                try:
                    cursor.execute('''
                        INSERT INTO station (station_name, destination_name, route)
                        VALUES (?, ?, ?)
                    ''', (origin_name, dest_name, ROUTE_NAME))
                except Exception as e:
                    print(f"Error inserting station {origin_name} -> {dest_name}: {e}")

    conn.commit()
    conn.close()
    print("✅ Route matrix ingested.")


def ingest_fare_matrix(file_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

        destination_names = data[0][1:]
        origin_to_row = data[1:]

        # Create temp mapping of name → new ID
        all_names = set(destination_names + [row[0] for row in origin_to_row])
        name_to_id = {name: idx + 1 for idx, name in enumerate(sorted(all_names))}

        for i, row in enumerate(origin_to_row):
            origin_name = row[0]
            for j in range(1, len(row)):
                dest_name = destination_names[j - 1]
                price = row[j].strip()

                if not price:
                    continue  # skip empty

                try:
                    origin_id = name_to_id[origin_name]
                    dest_id = name_to_id[dest_name]

                    cursor.execute('''
                        INSERT OR REPLACE INTO fare_matrix (origin_id, destination_id, price)
                        VALUES (?, ?, ?)
                    ''', (origin_id, dest_id, float(price)))
                except Exception as e:
                    print(f"Error inserting fare {origin_name} -> {dest_name}: {e}")

    conn.commit()
    conn.close()
    print("✅ Fare matrix ingested.")


def initialize_database():
    create_tables()

    if os.path.exists(ROUTE_CSV):
        ingest_route_matrix(ROUTE_CSV)
    else:
        print(f"❌ Missing {ROUTE_CSV}")

    if os.path.exists(FARE_CSV):
        ingest_fare_matrix(FARE_CSV)
    else:
        print(f"❌ Missing {FARE_CSV}")


if __name__ == "__main__":
    initialize_database()
