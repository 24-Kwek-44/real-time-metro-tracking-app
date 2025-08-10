# realtime.py
"""
Manages all real-time WebSocket communication using Flask-SocketIO.

This module initializes the SocketIO server and defines the event handlers
for client connections, disconnections, and custom application events like
receiving and broadcasting train position updates.
"""

from flask_socketio import SocketIO, emit

# Create the SocketIO server instance.
# 'async_mode' is set for compatibility with the Flask development server.
socketio = SocketIO(async_mode='threading')

# --- Default Socket.IO Event Handlers ---

@socketio.on('connect')
def handle_connect():
    """
    Handles new client connections. This is triggered automatically when a
    client establishes a connection with the server.
    """
    print('Client connected successfully!')
    # 'emit' sends a message back only to the client that just connected.
    emit('welcome_message', {'data': 'Welcome to the real-time server!'})

@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles client disconnections. This is triggered automatically when a
    client closes their connection.
    """
    print('Client disconnected.')

# --- Custom Application Event Handlers ---

@socketio.on('train_update')
def handle_train_update(data):
    """
    Receives a 'train_update' event from the data_generator client.

    This function acts as the entry point for live data into the system.
    It then broadcasts this data to all connected frontend (browser) clients
    on the 'new_train_position' event.

    Args:
        data (dict): A dictionary containing the train update information.
                     Example: {'train_id': 'T-1234', 'current_station': 'Kajang'}
    """
    print(f"Received train update: {data}")
    # 'socketio.emit' with 'broadcast=True' sends the message to ALL connected clients.
    # This is the core of the "publish-subscribe" model for our live tracking.
    socketio.emit('new_train_position', data, broadcast=True)