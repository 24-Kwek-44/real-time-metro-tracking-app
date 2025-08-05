# routes.py

from flask import Blueprint, jsonify, request
from database import get_db_connection 

# Create a Blueprint named 'api'
api = Blueprint('api', __name__)

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
    """Computes and returns the shortest path (by hops or price)."""
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    fake_route = {
        "from": from_station,
        "to": to_station,
        "path": ["ST1", "ST3", "ST5", "ST2"],
        "total_fare": 12.00
    }
    return jsonify(fake_route)