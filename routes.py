# routes.py

from flask import Blueprint, jsonify, request

# Create a Blueprint named 'api'
api = Blueprint('api', __name__)

# Stub for /stations endpoint
@api.route('/stations', methods=['GET'])
def get_stations():
    """Returns a list of all station metadata."""
    # This is fake data for now.
    # Later, this will come from the database.
    fake_stations = [
        {"station_id": "ST1", "name": "Central Station", "latitude": 3.1390, "longitude": 101.6869},
        {"station_id": "ST2", "name": "North Hub", "latitude": 3.1587, "longitude": 101.7118}
    ]
    return jsonify(fake_stations)

# Stub for /fare endpoint
@api.route('/fare', methods=['GET'])
def get_fare():
    """Returns the fare between two stations."""
    # Get 'from' and 'to' station IDs from the query parameters
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    # This is a fake fare for now.
    fake_fare = {"from": from_station, "to": to_station, "price": 5.50}
    return jsonify(fake_fare)


# Stub for /route endpoint
@api.route('/route', methods=['GET'])
def get_route():
    """Computes and returns the shortest path (by hops or price)."""
    from_station = request.args.get('from')
    to_station = request.args.get('to')

    if not from_station or not to_station:
        return jsonify({"error": "Missing 'from' or 'to' station parameters"}), 400

    # This is a fake route for now.
    fake_route = {
        "from": from_station,
        "to": to_station,
        "path": ["ST1", "ST3", "ST5", "ST2"],
        "total_fare": 12.00
    }
    return jsonify(fake_route)