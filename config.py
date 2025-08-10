"""
Central configuration file for the Flask application.

This file contains all the settings and constants used across the application,
making it easy to manage and modify configurations from a single location.
"""

# --- Database Configuration ---
DATABASE_NAME = 'db.sqlite'

# --- Server Configuration ---
SERVER_PORT = 5000

# --- Real-Time Simulation Configuration ---
# The time in seconds that the data generator waits before sending a new update.
SIMULATION_INTERVAL_SECONDS = 4