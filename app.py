from flask import Flask, render_template
from routes import api  
from realtime import socketio 


# Create an instance of the Flask application
app = Flask(__name__)

# Register the blueprint with the app
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def index():
    """Serve the main HTML file for the kiosk."""
    return render_template('index.html')

# Initialize the SocketIO server with our Flask app
socketio.init_app(app)

# This block ensures the server runs only when the script is executed directly
if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    socketio.run(app, debug=True, port=5000)
