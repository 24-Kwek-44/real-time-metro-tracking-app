# routes.py

from flask import Blueprint, jsonify, request
from database import get_db_connection
from collections import deque 

# Create a Blueprint named 'api'
api = Blueprint('api', __name__)

# Global variable to hold our station network graph
network_graph = {}

def build_network_graph():
    """
    Builds a graph of the station network from the database.
    This should be called once when the application starts.
    """
    global network_graph
    # The 'station' table is perfect for this, as it represents connections
    conn = get_db_connection()
    # We need to get all connections in both directions
    routes_from_db = conn.execute('SELECT station_name, destination_name FROM station').fetchall()
    conn.close()

    graph = {}
    for row in routes_from_db:
        origin = row['station_name']
        dest = row['destination_name']

        # Add connection from origin to destination
        if origin not in graph:
            graph[origin] = []
        if dest not in graph[origin]:
            graph[origin].append(dest)

        # Add the reverse connection from destination to origin
        if dest not in graph:
            graph[dest] = []
        if origin not in graph[dest]:
            graph[dest].append(origin)

    network_graph = graph
    print("Station network graph built successfully.")

@api.route('/stations', methods=['GET'])
def get_stations():
    """Returns a list of all unique station names from the database."""
    conn = get_db_connection()
    stations_from_db = conn.execute(
        'SELECT DISTINCT station_name FROM fare_matrix ORDER BY station_name'
    ).fetchall()
    conn.close()

    stations = []
    for row in stations_from_db:
        stations.append({"name": row['station_name']})

    return jsonify(stations)

@api.route('/fare', methods=['GET'])
def get_fare():
    """Returns the fare between two stations from the database."""
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

    real_fare = {
        "from": from_station,
        "to": to_station,
        "price": fare_data['price']
    }
    return jsonify(real_fare)

@api.route('/route', methods=['GET'])
def get_route():
    """Computes and returns the shortest path using Breadth-First Search (BFS)."""
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    # --- BFS Pathfinding Logic ---
    if from_station not in network_graph or to_station not in network_graph:
        return jsonify({"error": "One or both stations not found in the network"}), 404

    queue = deque([(from_station, [from_station])]) # Queue of (current_station, path_so_far)
    visited = {from_station}

    while queue:
        current, path = queue.popleft()

        if current == to_station:
            # We found the shortest path!
            # Now, let's calculate the total fare for this path.
            total_fare = 0
            conn = get_db_connection()
            for i in range(len(path) - 1):
                fare_data = conn.execute(
                    'SELECT price FROM fare_matrix WHERE station_name = ? AND destination_name = ?',
                    (path[i], path[i+1])
                ).fetchone()
                if fare_data and fare_data['price']:
                    total_fare += fare_data['price']
            conn.close()

            return jsonify({
                "from": from_station,
                "to": to_station,
                "path": path, # The calculated path
                "total_fare": round(total_fare, 2) # The calculated fare
            })

        for neighbor in network_graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append((neighbor, new_path))
    
    # If the loop finishes, no path was found
    return jsonify({"error": "No route found between the specified stations"}), 404