# data_generator.py

import time
import random
import socketio
import sqlite3
from config import SIMULATION_INTERVAL_SECONDS, DATABASE_NAME

# --- 1. Client Setup ---
sio = socketio.Client()
try:
    sio.connect('http://localhost:5000')
except socketio.exceptions.ConnectionError:
    print("Connection failed: Please ensure the main Flask server (app.py) is running.")
    exit()

# --- 2. Realistic Route Generation ---
def build_network_graph_for_generator():
    """Builds a simplified station graph from the 'connections' table."""
    try:
        # Connect to the correct database file from config
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row
        # CORRECTED: Query the 'connections' table
        connections_from_db = conn.execute('SELECT origin_name, destination_name FROM connections').fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"Database error while building graph: {e}")
        return {} # Return an empty graph on error

    graph = {}
    for row in connections_from_db:
        origin, dest = row['origin_name'], row['destination_name']
        graph.setdefault(origin, [])
        graph.setdefault(dest, [])
        if dest not in graph[origin]:
            graph[origin].append(dest)
        if origin not in graph[dest]:
            graph[dest].append(origin)
    return graph

def generate_random_route(graph, length=10):
    """
    Generates a realistic, longer route by performing a random walk
    on the station network graph.
    """
    if not graph:
        return []
        
    start_station = random.choice(list(graph.keys()))
    route = [start_station]
    current_station = start_station
    
    for _ in range(length - 1):
        neighbors = graph.get(current_station, [])
        if not neighbors:
            break
        
        # Move to a random neighbor
        next_station = random.choice(neighbors)
        route.append(next_station)
        current_station = next_station
        
    return route

# --- 3. Simulation Logic ---
def simulate_train_movement():
    """Simulates a train moving along a randomly generated route."""
    train_id = f"Train-{random.randint(1000, 9999)}"
    
    # --- BUILD GRAPH AND GENERATE A REALISTIC ROUTE ---
    print("Building local network graph for simulation...")
    station_graph = build_network_graph_for_generator()
    route = generate_random_route(station_graph)
    
    if not route:
        print("Could not generate a route from DB. Using fallback.")
        route = ["Kajang", "Stadium Kajang", "Sungai Jernih", "Batu 11 Cheras"]
    
    print(f"--- Starting Live Data Simulation for {train_id} using route: {route} ---")

    while True:
        for station in route:
            update_data = {'train_id': train_id, 'current_station': station, 'timestamp': time.time()}
            sio.emit('train_update', update_data)
            print(f"Sent update: {train_id} is now at {station}")
            time.sleep(SIMULATION_INTERVAL_SECONDS)

# --- 4. Main Execution Block ---
if __name__ == "__main__":
    try:
        simulate_train_movement()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        if sio.connected:
            sio.disconnect()
        print("Disconnected from server.")