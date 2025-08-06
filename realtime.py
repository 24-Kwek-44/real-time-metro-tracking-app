from flask_socketio import SocketIO, emit

# Create the SocketIO server instance.
# The async_mode is set to 'threading' for compatibility with the standard Flask server.
socketio = SocketIO(async_mode='threading')

# Define what happens when a client connects to the server
@socketio.on('connect')
def handle_connect():
    """Event handler for new client connections."""
    print('Client connected successfully!')
    # Send a welcome message back to the connected client
    emit('welcome_message', {'data': 'Welcome to the real-time server!'})

# You can add more event handlers here later, like for 'disconnect'.
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected.')