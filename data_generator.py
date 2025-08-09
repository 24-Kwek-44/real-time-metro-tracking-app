import sqlite3
import time
import random


conn = sqlite3.connect('db.sqlite')
cursor = conn.cursor()

def fetch_data():
    
    # Join fare_matrix and station to retrieve the exact matching route for origin-destination
    query = '''
        SELECT 
            fare_matrix.fare_id, 
            fare_matrix.station_name, 
            fare_matrix.destination_name,
            station.route,
            fare_matrix.price
        FROM fare_matrix
        JOIN station 
        ON fare_matrix.station_name = station.station_name
        AND fare_matrix.destination_name = station.destination_name
    '''
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows

def simulate_live_updates():
    try:
        print("Starting live train fare updates...\n")
        print("Live Update:")
        print("-" * 20)
        while True:
            data = fetch_data()
            sample = random.sample(data, min(1, len(data)))  # Random 1 entries 

            
            for row in sample:
                fare_id, station, destination, route, price = row
                print(f"ID: {fare_id} ")
                print(f"From: {station} -> To: {destination}")
                print(f"Route: {route}")
                print(f"Price: RM {price:.2f}")
            print("-" * 80)
            time.sleep(5) 

    except KeyboardInterrupt:
        print("\nStopped live updates.")
    finally:
        conn.close()

if __name__ == "__main__":
    simulate_live_updates()
