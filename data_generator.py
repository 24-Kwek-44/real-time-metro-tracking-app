# data_generator.py (FINAL PANDAS-ERA VERSION)
"""
A standalone client script that simulates and publishes live train position data.
It uses the hardcoded line sequences from the config file to generate realistic routes.
"""
import time
import random
import socketio
from config import SIMULATION_INTERVAL_SECONDS, KAJANG_LINE, KELANA_JAYA_LINE

sio = socketio.Client()
try:
    sio.connect('http://localhost:5000')
except socketio.exceptions.ConnectionError:
    print(f"[FATAL ERROR] Connection failed. Is the main Flask server (app.py) running?")
    exit()

def generate_random_route(length=12):
    """
    Generates a realistic route by picking a line and a random segment from it.
    
    Args:
        length (int): The desired number of stops in the simulated route.
    
    Returns:
        list: A list of station names for the simulation.
    """

    # Choose one of the major lines to simulate a train on
    line_to_simulate = random.choice([KAJANG_LINE, KELANA_JAYA_LINE])
    
    if len(line_to_simulate) <= length:
        return line_to_simulate # Return the whole line if it's short
        
    # Pick a random starting point for the segment
    start_index = random.randint(0, len(line_to_simulate) - length)
    return line_to_simulate[start_index : start_index + length]

def simulate_train_movement():
    """
    The main simulation loop. Generates a random train and route, then
    periodically emits position updates to the server.
    """
    train_id = f"Train-{random.randint(1000, 9999)}"
    route = generate_random_route()
    
    if not route:
        print("[ERROR] Could not generate a route. Exiting.")
        return
    
    print(f"\n--- Starting simulation for {train_id} on route: {route} ---")
    while True:
        # Loop through the route to simulate the train's journey
        for station in route:
            update_data = {'train_id': train_id, 'current_station': station}
            sio.emit('train_update', update_data)
            print(f"Sent update: {train_id} is now at {station}")
            time.sleep(SIMULATION_INTERVAL_SECONDS)
            
        # When the train reaches the end, it reverses for the return journey
        route.reverse()
        print(f"--- Train {train_id} reversing direction ---")


if __name__ == "__main__":
    try:
        simulate_train_movement()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        if sio.connected:
            sio.disconnect()
        print("Disconnected from server.")