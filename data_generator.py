# data_generator.py (The final version you are implementing)

import time
import random
import socketio

# --- 1. Client Setup ---
# Create a new Socket.IO client instance. This client will connect to our main Flask server.
sio = socketio.Client()

try:
    # Attempt to establish a connection to the server.
    sio.connect('http://localhost:5000')
except socketio.exceptions.ConnectionError:
    print("Connection failed: Please ensure the main Flask server (app.py) is running.")
    exit()


# --- 2. Simulation Logic ---
def simulate_train_movement():
    """Simulates a train moving along a predefined route and emits its position."""
    train_id = f"Train-{random.randint(1000, 9999)}"
    # This route simulates a train moving sequentially through stations.
    route = ["Kajang", "Stadium Kajang", "Sungai Jernih", "Batu 11 Cheras", "Bukit Dukung", "Taman Connaught", "Taman Mutiara", "Taman Midah"]
    
    print(f"--- Starting Live Data Simulation for {train_id} ---")
    
    while True:
        # Loop through the route to simulate movement.
        for station in route:
            # This is the correct data structure the project requires.
            update_data = {
                'train_id': train_id,
                'current_station': station,
                'timestamp': time.time()
            }

            # Publish the update to the server via the 'train_update' event.
            sio.emit('train_update', update_data)
            print(f"Sent update: {train_id} is now at {station}")
            time.sleep(4) # Wait 4 seconds before the "train" moves to the next station


# --- 3. Main Execution Block ---
if __name__ == "__main__":
    try:
        simulate_train_movement()
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")
    finally:
        # Cleanly disconnect from the server when the script is stopped.
        if sio.connected:
            sio.disconnect()
        print("Disconnected from server.")