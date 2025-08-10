# routes.py
"""
Defines all HTTP API endpoints for the Flask application.
This version is updated to work with the new, normalized database schema.
"""
from flask import Blueprint, jsonify, request
from database import get_db_connection
from collections import deque

api = Blueprint('api', __name__)
network_graph = {}

# --- Graph Construction and Helper Functions ---
def build_network_graph():
    """
    Builds an undirected graph of the station network from the 'connections' table.
    """
    global network_graph
    print("Building station network graph from the 'connections' table...")
    conn = get_db_connection()
    # CORRECTED: Query the 'connections' table
    connections_from_db = conn.execute('SELECT origin_name, destination_name FROM connections').fetchall()
    conn.close()

    graph = {}
    for row in connections_from_db:
        origin, dest = row['origin_name'], row['destination_name']
        graph.setdefault(origin, [])
        graph.setdefault(dest, [])
        if dest not in graph[origin]:
            graph[origin].append(dest)
        if origin not in graph[dest]:
            graph[dest].append(origin)

    network_graph = graph
    print("Station network graph built successfully.")

def _calculate_path_fare(path):
    """Calculates the total fare for a given path using the 'fares' table."""
    if len(path) < 2:
        return 0.0
    total_fare = 0
    conn = get_db_connection()
    for i in range(len(path) - 1):
        # CORRECTED: Query the 'fares' table
        fare_data = conn.execute(
            'SELECT price FROM fares WHERE origin_name = ? AND destination_name = ?',
            (path[i], path[i+1])
        ).fetchone()
        if fare_data and fare_data['price']:
            total_fare += fare_data['price']
    conn.close()
    return round(total_fare, 2)

# --- API Endpoints ---

@api.route('/stations', methods=['GET'])
def get_stations():
    """Returns a JSON list of all unique station names from the 'stations' table."""
    conn = get_db_connection()
    # CORRECTED: Query the new 'stations' table
    stations_from_db = conn.execute('SELECT name FROM stations ORDER BY name').fetchall()
    conn.close()
    
    stations = [{"name": row['name']} for row in stations_from_db]
    return jsonify(stations)

@api.route('/fare', methods=['GET'])
def get_fare():
    """Returns the direct fare between two specified stations from the 'fares' table."""
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    conn = get_db_connection()
    # CORRECTED: Query the 'fares' table
    fare_data = conn.execute(
        'SELECT price FROM fares WHERE origin_name = ? AND destination_name = ?',
        (from_station, to_station)
    ).fetchone()
    conn.close()

    if fare_data is None:
        return jsonify({"error": "Fare not found for the specified route"}), 404

    return jsonify({"from": from_station, "to": to_station, "price": fare_data['price']})

@api.route('/route', methods=['GET'])
def get_route():
    """Computes the shortest path using BFS on the new graph structure."""
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    if from_station == to_station:
        return jsonify({
            "from": from_station, "to": to_station, "path": [from_station],
            "total_fare": 0.0, "message": "Origin and destination stations are the same."
        })

    if from_station not in network_graph or to_station not in network_graph:
        return jsonify({"error": "One or both stations not found in the network"}), 404

    # The BFS logic itself does not need to change, as it works with the graph
    queue = deque([(from_station, [from_station])])
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