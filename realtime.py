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
    print(f"Received train update from generator: {data}")
    # 'emit' with 'broadcast=True' sends the message to ALL connected clients.
    # We use a different event name ('new_train_position') to distinguish
    # it from the incoming event.
    socketio.emit('new_train_position', data, broadcast=True)