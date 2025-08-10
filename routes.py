# routes.py
"""
Defines all HTTP API endpoints for the Flask application.

This module uses a Flask Blueprint to organize routes, handling all request-response
logic for the application, including station data retrieval, fare lookups, and
dynamic route computation using a pre-built in-memory graph.
"""
from flask import Blueprint, jsonify, request
from database import get_db_connection
from collections import deque

# Create a Blueprint which will be registered with the Flask app in app.py.
api = Blueprint('api', __name__)

# This global variable will hold the in-memory graph of the station network.
# It is populated by the build_network_graph() function upon app startup.
network_graph = {}

# --- Graph Construction and Helper Functions ---

def build_network_graph():
    """
    Builds an undirected graph representation of the station network.
    This function reads from the 'connections' table and populates the global
    'network_graph' variable. It is called once at application startup for performance.
    """
    global network_graph
    print("Building station network graph from the 'connections' table...")
    conn = get_db_connection()
    connections_from_db = conn.execute('SELECT origin_name, destination_name FROM connections').fetchall()
    conn.close()

    graph = {}
    for row in connections_from_db:
        origin, dest = row['origin_name'], row['destination_name']
        # Ensure that connections are two-way to represent an undirected graph.
        graph.setdefault(origin, []).append(dest)
        graph.setdefault(dest, []).append(origin)

    network_graph = graph
    print(f"Station network graph built successfully with {len(graph)} nodes.")

def _calculate_path_fare(path):
    """
    Helper function to calculate the total fare for a given path.
    It iterates through each segment of the path and sums the individual fares.
    """
    if len(path) < 2:
        return 0.0
    total_fare = 0
    conn = get_db_connection()
    for i in range(len(path) - 1):
        # Note: Fares are directional, A->B might be different from B->A.
        # For this dataset they are the same, but this query handles both.
        fare_data = conn.execute(
            'SELECT price FROM fares WHERE (origin_name = ? AND destination_name = ?) OR (origin_name = ? AND destination_name = ?)',
            (path[i], path[i+1], path[i+1], path[i])
        ).fetchone()
        if fare_data and fare_data['price']:
            total_fare += fare_data['price']
    conn.close()
    return round(total_fare, 2)

# --- API Endpoints ---

@api.route('/stations', methods=['GET'])
def get_stations():
    """
    Returns a JSON list of all stations with their name and coordinates.
    This data is used by the frontend to populate station selectors and map markers.
    """
    conn = get_db_connection()
    stations_from_db = conn.execute('SELECT name, latitude, longitude FROM stations ORDER BY name').fetchall()
    conn.close()
    # Convert the list of database row objects into a list of dictionaries.
    stations = [dict(row) for row in stations_from_db]
    return jsonify(stations)

@api.route('/fare', methods=['GET'])
def get_fare():
    """
    Returns the direct fare between two specified stations.
    Query Params: from (str), to (str).
    """
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    conn = get_db_connection()
    fare_data = conn.execute('SELECT price FROM fares WHERE origin_name = ? AND destination_name = ?', (from_station, to_station)).fetchone()
    conn.close()

    if fare_data is None:
        return jsonify({"error": "Fare not found for the specified route"}), 404

    return jsonify({"from": from_station, "to": to_station, "price": fare_data['price']})

@api.route('/route', methods=['GET'])
def get_route():
    """
    Computes and returns the shortest path (by stops) and total fare
    between two stations using the Breadth-First Search (BFS) algorithm.
    Query Params: from (str), to (str).
    """
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' parameters"}), 400

    if from_station == to_station:
        return jsonify({"from": from_station, "to": to_station, "path": [from_station], "total_fare": 0.0, "message": "Origin and destination are the same."})

    if from_station not in network_graph or to_station not in network_graph:
        return jsonify({"error": "One or both stations not found in the network"}), 404

    # --- BFS Pathfinding Algorithm ---
    queue = deque([(from_station, [from_station])]) # Each item is (current_node, path_to_this_node)
    visited = {from_station}

    while queue:
        current, path = queue.popleft()
        if current == to_station:
            total_fare = _calculate_path_fare(path)
            return jsonify({"from": from_station, "to": to_station, "path": path, "total_fare": total_fare})

        for neighbor in network_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append((neighbor, new_path))
    
    return jsonify({"error": "No route found between the specified stations"}), 404