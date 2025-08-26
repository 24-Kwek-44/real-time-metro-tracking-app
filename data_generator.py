# data_generator.py (FINAL - USER-DRIVEN SIMULATION)
"""
A standalone client script that simulates train movement based on instructions
received from the main server.

This script:
1. Connects to the Flask-SocketIO server.
2. Enters a passive state, waiting for a 'new_route_to_simulate' event.
3. When it receives a route, it simulates a train moving along that specific path.
4. After the simulation is complete, it returns to the waiting state.
"""
import time
import random
import socketio
from config import SIMULATION_INTERVAL_SECONDS

# This global variable will be updated by the WebSocket event handler
# It holds the specific path that the server has instructed us to simulate.
current_simulation_path = None

# --- 1. WebSocket Client Setup ---
sio = socketio.Client()

# --- 2. Define Event Handlers for This Client ---
@sio.event
def connect():
    """Handler for a successful connection to the server."""
    print("Connection to server established. Waiting for a route to simulate...")

@sio.event
def disconnect():
    """Handler for disconnection from the server."""
    print("Disconnected from server.")

@sio.on('new_route_to_simulate')
def on_new_route(data):
    """
    Receives a new route from the server to start simulating.
    This is the most important handler in this script.
    """
    global current_simulation_path
    path = data.get('path')
    if path and isinstance(path, list):
        print(f"\n[RECEIVED INSTRUCTION] New route to simulate: {path}")
        current_simulation_path = path
    else:
        print(f"[WARNING] Received invalid route data: {data}")

# --- 3. Main Simulation Logic ---
def run_simulation():
    """
    The main simulation loop. It continuously checks if there is a route
    to simulate and executes the simulation when one is received.
    """
    global current_simulation_path
    train_id_counter = 1000

    while True:
        if current_simulation_path:
            # A new route has been received, start the simulation
            train_id = f"Train-{train_id_counter}"
            train_id_counter += 1
            
            print(f"--- Starting simulation for {train_id} on route: {current_simulation_path} ---")
            
            # Loop through the assigned route
            for station in current_simulation_path:
                update_data = {'train_id': train_id, 'current_station': station}
                sio.emit('train_update', update_data)
                print(f"  Sent update: {train_id} is now at {station}")
                time.sleep(SIMULATION_INTERVAL_SECONDS)
            
            print(f"--- Simulation for {train_id} complete. Train has arrived. ---")
            
            # Reset the path to None and return to the waiting state
            current_simulation_path = None
            print("\nWaiting for a new route to simulate...")
        else:
            # If there's no route, just wait quietly for instructions.
            time.sleep(1)

# --- 4. Main Execution Block ---
if __name__ == "__main__":
    try:
        # Attempt to establish the connection. The event handlers are already set up.
        sio.connect('http://localhost:5000')
        # Start the main loop
        run_simulation()
    except socketio.exceptions.ConnectionError:
        print(f"[FATAL ERROR] Connection failed. Is the main Flask server (app.py) running?")
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        if sio.connected:
            sio.disconnect()