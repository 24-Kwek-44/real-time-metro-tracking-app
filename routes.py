from flask import Blueprint, jsonify, request
from database import get_db_connection
from collections import deque

# Create a Blueprint which will be registered with the Flask app.
api = Blueprint('api', __name__)

# This global variable will hold the in-memory graph of the station network.
# It is populated by the build_network_graph() function upon app startup.
network_graph = {}


# --- Graph Construction and Helper Functions ---
def build_network_graph():
    global network_graph
    print("Building station network graph...")
    conn = get_db_connection()
    # The 'station' table represents all direct connections between stations.
    routes_from_db = conn.execute('SELECT station_name, destination_name FROM station').fetchall()
    conn.close()

    graph = {}
    for row in routes_from_db:
        origin, dest = row['station_name'], row['destination_name']
        
        # Ensure an entry exists for both origin and destination.
        graph.setdefault(origin, [])
        graph.setdefault(dest, [])
        
        # Add a two-way connection to represent an undirected edge.
        if dest not in graph[origin]:
            graph[origin].append(dest)
        if origin not in graph[dest]:
            graph[dest].append(origin)

    network_graph = graph
    print("Station network graph built successfully.")


def _calculate_path_fare(path):
    if len(path) < 2:
        return 0.0

    total_fare = 0
    conn = get_db_connection()
    # Iterate through each segment of the path (e.g., A->B, B->C).
    for i in range(len(path) - 1):
        fare_data = conn.execute(
            'SELECT price FROM fare_matrix WHERE station_name = ? AND destination_name = ?',
            (path[i], path[i+1])
        ).fetchone()
        if fare_data and fare_data['price']:
            total_fare += fare_data['price']
    conn.close()
    return round(total_fare, 2)


# --- API Endpoints ---
@api.route('/stations', methods=['GET'])
def get_stations():
    """Returns a JSON list of all unique station names."""
    conn = get_db_connection()
    # Use DISTINCT to ensure we only get unique station names.
    stations_from_db = conn.execute(
        'SELECT DISTINCT station_name FROM fare_matrix ORDER BY station_name'
    ).fetchall()
    conn.close()
    
    # Format the data for the JSON response.
    stations = [{"name": row['station_name']} for row in stations_from_db]
    return jsonify(stations)


@api.route('/fare', methods=['GET'])
def get_fare():
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    conn = get_db_connection()
    fare_data = conn.execute(
        'SELECT price FROM fare_matrix WHERE station_name = ? AND destination_name = ?',
        (from_station, to_station)
    ).fetchone()
    conn.close()

    if fare_data is None:
        return jsonify({"error": "Fare not found for the specified route"}), 404

    return jsonify({"from": from_station, "to": to_station, "price": fare_data['price']})


@api.route('/route', methods=['GET'])
def get_route():
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    if from_station not in network_graph or to_station not in network_graph:
        return jsonify({"error": "One or both stations not found in the network"}), 404

    # --- BFS Pathfinding Algorithm ---
    # The queue stores tuples of (current_station, path_taken_to_get_here).
    queue = deque([(from_station, [from_station])])
    # The visited set prevents processing the same station multiple times, avoiding cycles.
    visited = {from_station}

    while queue:
        current, path = queue.popleft()

        # Goal check: If the current station is our destination, we've found the shortest path.
        if current == to_station:
            # Calculate the total fare for the found path.
            total_fare = _calculate_path_fare(path)
            
            return jsonify({
                "from": from_station,
                "to": to_station,
                "path": path,
                "total_fare": total_fare
            })

        # Exploration: Add all unvisited neighbors to the queue.
        for neighbor in network_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append((neighbor, new_path))
    
    # If the queue becomes empty and we haven't found the destination, no path exists.
    return jsonify({"error": "No route found between the specified stations"}), 404