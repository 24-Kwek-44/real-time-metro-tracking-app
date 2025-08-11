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
    Receives updates from the data generator and broadcasts to all clients.
    """
    print(f"Received train update: {data}")
    # For some library versions, broadcast=True is implicit when emitting
    # from the main socketio object. Removing the argument fixes the TypeError.
    socketio.emit('new_train_position', data)