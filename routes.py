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
import re
from config import VERIFIED_COORDINATES, KAJANG_LINE, KELANA_JAYA_LINE, INTERCHANGE_STATIONS

api = Blueprint('api', __name__)

# --- In-Memory Data Storage ---
station_list = []
fare_df, time_df, route_df = None, None, None

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
    """Looks up fare/time and returns a drawable path + colored segments."""
    origin, destination = request.args.get('from'), request.args.get('to')
    if not origin or not destination:
        return jsonify({"error": "Missing parameters"}), 400
    try:
        fare = float(fare_df.loc[origin, destination])
        minutes = int(time_df.loc[origin, destination])
    except Exception:
        return jsonify({"error": "Route data not available for this journey."}), 404

    # Build path + segments from the official line sequences
    path, segments = _compute_path_segments(origin, destination)

    return jsonify({
        "from": origin,
        "to": destination,
        "total_fare": fare,
        "total_time_minutes": minutes,
        "path": path,                    # e.g. ["Kajang", ..., "SS 15"]
        "segments": segments             # e.g. [{line:"KGL", stations:[...]}, {line:"KJL", stations:[...]}]
    })
def _slice_line(seq, a, b):
    i, j = seq.index(a), seq.index(b)
    step = 1 if i <= j else -1
    return seq[i:j+step:step]

def _line_code_for(station):
    # 'KGL' for Kajang (SBK), 'KJL' for Kelana Jaya
    if station in KAJANG_LINE: return 'KGL'
    if station in KELANA_JAYA_LINE: return 'KJL'
    return None

def _compute_path_segments(origin, destination):
    """Return (path_list, segments[{line, stations[]}])."""
    lo = _line_code_for(origin)
    ld = _line_code_for(destination)
    lines = {'KGL': KAJANG_LINE, 'KJL': KELANA_JAYA_LINE}

    # Same line — simple slice
    if lo and ld and lo == ld:
        seq = lines[lo]
        path = _slice_line(seq, origin, destination)
        return path, [{'line': lo, 'stations': path}]

    # Cross-line via the defined interchanges
    pairs = set()
    for a, b in INTERCHANGE_STATIONS.items():
        pairs.add((a, b))
        pairs.add((b, a))  # allow both directions

    best = None
    for a, b in pairs:
        la, lb = _line_code_for(a), _line_code_for(b)
        if not (la and lb and lo and ld): 
            continue
        if lo == la and ld == lb and a in lines[lo] and b in lines[ld]:
            seg1 = _slice_line(lines[lo], origin, a)            # origin -> a
            seg2 = _slice_line(lines[ld], b, destination)       # b -> destination
            seg2_tail = seg2[1:] if seg2 and seg2[0] == b else seg2
            path = seg1 + [b] + seg2_tail                       # bridge a -> b (walkway)
            cand = (path, [{'line': lo, 'stations': seg1}, {'line': ld, 'stations': seg2}])
            if (best is None) or (len(cand[0]) < len(best[0])):
                best = cand

    return best if best else ([origin, destination], [{'line': lo or 'KGL', 'stations': [origin, destination]}])


# Load all data into memory once when the module is imported
load_all_data()