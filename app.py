from flask import Flask, render_template
from routes import api  # CHANGE: We no longer need build_network_graph
from realtime import socketio
from config import SERVER_PORT

# --- Application Setup ---

# The data loading is now handled automatically when routes.py is imported.
# We no longer need to call build_network_graph() here.

# 1. Create the main Flask application instance.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'e75893054b24a8027e6c37e689e23fede6da697c6b1713331f6e72b06582689d' # Good practice for Flask

# 2. Register the API blueprint. All API routes from routes.py will be prefixed with /api.
app.register_blueprint(api, url_prefix='/api')

# 3. Initialize the Socket.IO server with the Flask app.
socketio.init_app(app)


# --- Route Definitions ---

@app.route('/')
def index():
    """Serves the main HTML file for the single-page application kiosk."""
    return render_template('index.html')


# --- Main Execution ---

if __name__ == '__main__':
    # Use socketio.run() to start a server that supports both standard HTTP and WebSockets.
    # The port is managed in the central config.py file.
    print(f"--- Starting Flask-SocketIO server on http://127.0.0.1:{SERVER_PORT} ---")
    socketio.run(app, host="0.0.0.0", port=SERVER_PORT, debug=True, allow_unsafe_werkzeug=True)