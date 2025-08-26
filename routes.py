# routes.py (FINAL - HYBRID BFS + PANDAS ARCHITECTURE)
from flask import Blueprint, jsonify, request
import pandas as pd
import sqlite3
from collections import deque
from config import DATABASE_NAME, KAJANG_LINE, KELANA_JAYA_LINE, INTERCHANGE_STATIONS

api = Blueprint('api', __name__)

# --- In-Memory Data Storage ---
stations_df = None
fare_df, time_df = None, None
network_graph = {} # For the BFS algorithm

def load_all_data():
    """
    Loads data from the clean SQLite database. It loads fares/times into
    Pandas DataFrames for fast lookups and builds an in-memory graph for BFS routing.
    """
    global stations_df, fare_df, time_df, network_graph
    
    print("--- Loading clean data from SQLite into memory ---")
    conn = sqlite3.connect(DATABASE_NAME)
    
    # Load stations, fares, and times into Pandas
    stations_df = pd.read_sql_query("SELECT * FROM stations ORDER BY name", conn, index_col='name')
    fares_raw = pd.read_sql_query("SELECT * FROM fares", conn)
    times_raw = pd.read_sql_query("SELECT * FROM times", conn)
    
    # Load connections to build the graph
    connections_raw = pd.read_sql_query("SELECT * FROM connections", conn)
    conn.close()
    
    # Pivot fares and times into matrix format for O(1) lookup
    fare_df = fares_raw.pivot(index='origin', columns='destination', values='price')
    time_df = times_raw.pivot(index='origin', columns='destination', values='minutes')
    
    # Build the network graph for BFS pathfinding
    graph = {}
    for index, row in connections_raw.iterrows():
        origin, dest = row['origin_name'], row['destination_name']
        graph.setdefault(origin, []).append(dest)
        graph.setdefault(dest, []).append(origin)
    network_graph = graph
    
    print(f"[SUCCESS] Loaded data and built graph for {len(stations_df)} stations.")

# --- API Endpoints ---

@api.route('/lines', methods=['GET'])
def get_lines():
    """Returns the line sequences and interchange data for map drawing."""
    return jsonify({
        "lines": {"Kelana Jaya Line": KELANA_JAYA_LINE, "Kajang Line": KAJANG_LINE},
        "interchanges": [[stn1, stn2] for stn1, stn2 in INTERCHANGE_STATIONS.items()]
    })

@api.route('/stations', methods=['GET'])
def get_stations():
    """Returns a list of all stations with their names and coordinates."""
    # Convert the DataFrame to the JSON format the frontend expects
    stations_for_api = stations_df.reset_index().to_dict(orient='records')
    return jsonify(stations_for_api)

@api.route('/route', methods=['GET'])
def get_route():
    """
    Calculates the true shortest path with BFS, then looks up fare/time with Pandas.
    """
    origin, destination = request.args.get('from'), request.args.get('to')
    if not origin or not destination: return jsonify({"error": "Missing parameters"}), 400
    if origin == destination:
        return jsonify({ "path": [origin], "total_fare": 0.0, "total_time_minutes": 0 })

    # --- Step 1: Find the true shortest path with BFS ---
    # This uses the accurate graph we built from the hardcoded line data
    queue = deque([(origin, [origin])])
    visited = {origin}
    path = None
    while queue:
        current, p = queue.popleft()
        if current == destination:
            path = p
            break
        for neighbor in network_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(p)
                new_path.append(neighbor)
                queue.append((neighbor, new_path))
    
    if not path:
        return jsonify({"error": "No route could be calculated between these stations."}), 404

    # --- Step 2: Calculate Fare and Time for the true path using fast Pandas lookups ---
    total_fare = 0.0
    total_time = 0
    try:
        for i in range(len(path) - 1):
            # Use .loc for fast, direct lookup in the DataFrames
            total_fare += fare_df.loc[path[i], path[i+1]]
            total_time += time_df.loc[path[i], path[i+1]]
    except KeyError:
        # This can happen if a fare/time is missing for a specific segment
        print(f"[WARNING] Missing fare/time data for a segment in path: {path}")
        # We can either return an error or proceed with the data we have.
        # For a better user experience, we'll proceed.
        pass
            
    return jsonify({
        "path": path,
        "path_description": " > ".join(path),
        "total_fare": round(total_fare, 2),
        "total_time_minutes": int(total_time)
    })

# Load all data from SQLite once when the application starts
load_all_data()