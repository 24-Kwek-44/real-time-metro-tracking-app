# app.py

from flask import Flask
from routes import api  # Import the 'api' blueprint from routes.py

# Create an instance of the Flask application
app = Flask(__name__)

# Register the blueprint with the app
# We're adding a prefix, so all routes in routes.py will start with /api
# For example: /api/stations
app.register_blueprint(api, url_prefix='/api')

# This block ensures the server runs only when the script is executed directly
if __name__ == '__main__':
    # Run the app in debug mode on port 5000
    app.run(debug=True, port=5000)