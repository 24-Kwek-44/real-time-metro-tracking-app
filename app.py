from flask import Flask, render_template
from routes import api, build_network_graph
from realtime import socketio
from config import SERVER_PORT  # <-- ADD THIS IMPORT

# --- Application Setup ---

# 1. Build the in-memory station network graph upon application startup.
# This pre-computation is a key performance optimization for the routing API.
build_network_graph()

# 2. Create the main Flask application instance.
app = Flask(__name__)

# 3. Register the API blueprint. All API routes will be prefixed with /api.
app.register_blueprint(api, url_prefix='/api')

# 4. Initialize the Socket.IO server with the Flask app.
socketio.init_app(app)


# --- Route Definitions ---

@app.route('/')
def index():
    """Serves the main HTML file for the single-page application kiosk."""
    return render_template('index.html')


# --- Main Execution ---

if __name__ == '__main__':
    # Use socketio.run() to start a server that supports both standard HTTP and WebSockets.
    # The port is now managed in the central config.py file.
    print(f"--- Starting Flask-SocketIO server on http://127.0.0.1:{SERVER_PORT} ---")
    socketio.run(app, debug=True, port=SERVER_PORT)  # <-- USE THE IMPORTED VARIABLE