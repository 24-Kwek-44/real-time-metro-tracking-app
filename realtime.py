from flask_socketio import SocketIO, emit

# Create the SocketIO server instance.
# We explicitly set the async_mode to 'threading' for compatibility with the
# standard Flask development server.
socketio = SocketIO(async_mode='threading')


# --- Default Event Handlers ---
@socketio.on('connect')
def handle_connect():
    print('Client connected successfully!')
    # 'emit' sends a message back to the client that just connected.
    emit('welcome_message', {'data': 'Welcome to the real-time server!'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected.')


# --- Custom Application Event Handlers ---
# This handler will be triggered by the data_generator.py script.
@socketio.on('train_update')
def handle_train_update(data):
    """
    Receives a train update from the data generator and
    broadcasts it to all connected web clients.
    """
    print(f"Received train update from generator: {data}")
    # By default, socketio.emit() from the server sends to all clients (broadcasts).
    # The 'broadcast=True' argument is used inside a request context to override
    # the default behavior of sending only to the originating client.
    # The TypeError indicates our library version prefers the simpler call.
    socketio.emit('new_train_position', data) # <-- REMOVE broadcast=True
