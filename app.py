from flask import Flask, render_template
from routes import api, build_network_graph
from realtime import socketio

# --- Application Setup ---

# Build the in-memory station network graph upon application startup.
build_network_graph()

# Create the main Flask application instance.
app = Flask(__name__)

# Register the API blueprint. All API routes will be prefixed with /api.
app.register_blueprint(api, url_prefix='/api')

# Initialize the Socket.IO server with the Flask app.
socketio.init_app(app)


# --- Route Definitions ---
@app.route('/')
def index():
    """Serves the main HTML file for the single-page application kiosk."""
    return render_template('index.html')


# --- Main Execution ---
if __name__ == '__main__':
    # Use socketio.run() to start a server that supports both standard HTTP and WebSockets.
    socketio.run(app, debug=True, port=5000)