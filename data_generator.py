# data_generator.py
"""
A standalone client script that simulates and publishes live train position data.

This script performs the following functions:
1. Connects to the main Flask-SocketIO server as a network client.
2. Reads the station connection data from the database to build a local network map.
3. Generates a realistic, multi-stop route by performing a random walk on the map.
4. Continuously emits 'train_update' events to the server, simulating a train's
   movement along the generated route.
"""

import time
import random
import socketio
import sqlite3
from config import SIMULATION_INTERVAL_SECONDS, DATABASE_NAME

# --- 1. WebSocket Client Setup ---

sio = socketio.Client()

try:
    # Attempt to establish a connection with the main Flask server.
    sio.connect('http://localhost:5000')
except socketio.exceptions.ConnectionError:
    print(f"[FATAL ERROR] Connection failed. Is the main Flask server (app.py) running?")
    exit()

# --- 2. Helper Functions for Route Generation ---

def get_db_connection():
    """Establishes a read-only connection to the database."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def build_network_graph_for_generator():
    """Builds a local copy of the station graph for realistic route simulation."""
    conn = get_db_connection()
    connections = conn.execute('SELECT origin_name, destination_name FROM connections').fetchall()
    conn.close()
    graph = {}
    for row in connections:
        origin, dest = row['origin_name'], row['destination_name']
        graph.setdefault(origin, []).append(dest)
        graph.setdefault(dest, []).append(origin)
    return graph

def generate_random_route(graph, length=12):
    """
    Generates a more realistic route by performing a random walk on the graph,
    avoiding immediate reversals.
    """
    if not graph: return []
    start_station = random.choice(list(graph.keys()))
    route = [start_station]
    current_station = start_station
    
    for _ in range(length - 1):
        neighbors = graph.get(current_station, [])
        # Create a list of possible next stations, excluding the one we just came from.
        possible_next = [n for n in neighbors if n != (route[-2] if len(route) > 1 else None)]
        
        if not possible_next:
            # If we hit a dead end (or can only go back), we'll just go back.
            possible_next = neighbors

        if not possible_next:
            break # Truly a dead end, stop generating.

        next_station = random.choice(possible_next)
        route.append(next_station)
        current_station = next_station
        
    return route

# --- 3. Main Simulation Logic ---

def simulate_train_movement():
    """
    The main simulation loop. Generates a random train and route, then
    periodically emits position updates to the server.
    """
    train_id = f"Train-{random.randint(1000, 9999)}"
    
    print("Building local network graph for simulation...")
    station_graph = build_network_graph_for_generator()
    route = generate_random_route(station_graph)
    
    if not route:
        print("[ERROR] Could not generate a route. Exiting.")
        return
    
    print(f"\n--- Starting simulation for {train_id} on route: {route} ---")
    while True:
        # Loop through the generated route to simulate the train's journey.
        for station in route:
            update_data = {'train_id': train_id, 'current_station': station}
            # Emit the 'train_update' event to the server.
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
        # Ensure a clean disconnection from the server when the script is stopped.
        if sio.connected:
            sio.disconnect()
        print("Disconnected from server.")