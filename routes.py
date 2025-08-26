# routes.py (FINAL PANDAS-BASED VERSION)
"""
Defines all HTTP API endpoints for the Flask application.

This module implements a high-performance, in-memory data architecture.
On startup, it loads all CSV data into Pandas DataFrames. API calls then
perform fast lookups on these in-memory structures instead of querying a database.
"""
from flask import Blueprint, jsonify, request
import pandas as pd
import os
from config import VERIFIED_COORDINATES, KAJANG_LINE, KELANA_JAYA_LINE, INTERCHANGE_STATIONS

api = Blueprint('api', __name__)

# --- In-Memory Data Storage ---
station_list = []
fare_df, time_df, route_df = None, None, None

# In routes.py

# In routes.py

def load_all_data():
    """Loads all CSV data into global Pandas DataFrames upon application startup."""
    global station_list, fare_df, time_df, route_df
    
    # --- FINAL, SIMPLE, CORRECT PATH ---
    # The 'data' folder is in the same root directory as app.py
    data_dir = 'data'
    
    try:
        print("--- Loading CSV data into memory ---")
        fare_df = pd.read_csv(os.path.join(data_dir, 'Fare.csv'), index_col=0)
        time_df = pd.read_csv(os.path.join(data_dir, 'Time.csv'), index_col=0)
        route_df = pd.read_csv(os.path.join(data_dir, 'Route.csv'), index_col=0)
        
        for df in [fare_df, time_df, route_df]:
            df.columns = df.columns.str.strip()
            df.index = df.index.str.strip()
            
        station_list = sorted(list(fare_df.index))
        print(f"[SUCCESS] Loaded and processed data for {len(station_list)} stations.")
    except FileNotFoundError as e:
        print(f"[FATAL ERROR] Data file not found: {e.filename}. Please check the 'data' folder.")
        exit()

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
    """Returns a list of all stations with their names and verified coordinates."""
    return jsonify([{
        "name": name,
        "latitude": VERIFIED_COORDINATES.get(name, {}).get("lat"),
        "longitude": VERIFIED_COORDINATES.get(name, {}).get("lon")
    } for name in station_list])

@api.route('/route', methods=['GET'])
def get_route():
    """Looks up the pre-calculated route, fare, and time from the in-memory DataFrames."""
    origin, destination = request.args.get('from'), request.args.get('to')
    if not origin or not destination: return jsonify({"error": "Missing parameters"}), 400
    try:
        # Perform a direct, high-speed lookup in the Pandas DataFrames
        fare = fare_df.loc[origin, destination]
        time = time_df.loc[origin, destination]
        path = route_df.loc[origin, destination]
        
        if pd.isna(fare) or pd.isna(time) or pd.isna(path):
             return jsonify({"error": "Route data not available for this journey."}), 404
        
        return jsonify({
            "total_fare": float(fare),
            "total_time_minutes": int(time),
            "path_description": str(path)
        })
    except KeyError:
        return jsonify({"error": "Invalid station name provided"}), 404

# Load all data into memory once when the module is imported
load_all_data()