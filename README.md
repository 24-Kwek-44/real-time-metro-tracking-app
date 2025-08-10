# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking and routing application using Flask, SQLite, and WebSockets.

## Project Setup & Running Instructions

### 1. Initial Setup

Follow these steps to get the project set up locally.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/24-Kwek-44/real-time-metro-tracking-app.git
    cd real-time-metro-tracking-app
    ```

2.  **Set up a Virtual Environment (Recommended):**
    This creates an isolated environment for the project's dependencies.
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate
    
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install all required Python libraries from the requirements file.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download and Place the Dataset:**
    The project's dataset is not tracked by Git.
    *   Download the required CSV files from: **[Kaggle: MyRapidKL Train Dataset](https://www.kaggle.com/datasets/niknmarjan/myrapidkl-train-dataset)**
    *   After downloading, place the `Fare.csv` and `Route.csv` files into the `data/` folder in the project's root directory.

5.  **Initialize the Database:**
    Run the `database.py` script once to create the `db.sqlite` file and populate it with data from the CSVs.
    ```bash
    python database.py
    ```

### 2. Running the Application

The application requires two separate processes to be running concurrently in two different terminal windows.

1.  **Start the Main Flask Server:**
    This server runs the backend API and the WebSocket hub.
    ```bash
    # In Terminal 1
    python app.py
    ```
    The server will be running on `http://127.0.0.1:5000`.

2.  **Start the Data Generator:**
    This script simulates and publishes live train data to the main server.
    ```bash
    # In Terminal 2 (make sure venv is active)
    python data_generator.py
    ```

3.  **Access the Kiosk Interface:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## Backend API Documentation

The backend provides RESTful API endpoints for request-response interactions. All routes are prefixed with `/api`.

### 1. GET /stations
Returns a list of all unique station names.
*   **Success Response (200 OK):**
    ```json
    [{"name": "Abdullah Hukum"}, {"name": "Alam Megah"}, ...]
    ```

### 2. GET /fare
Returns the direct fare between two stations.
*   **Query Params:** `from` (string), `to` (string)
*   **Example:** `/api/fare?from=Kajang&to=Muzium Negara`
*   **Success Response (200 OK):**
    ```json
    {"from": "Kajang", "price": 3.3, "to": "Muzium Negara"}
    ```

### 3. GET /route
Calculates the shortest path (by number of stops) and total fare between two stations.
*   **Query Params:** `from` (string), `to` (string)
*   **Example:** `/api/route?from=Kajang&to=Batu+11+Cheras`
*   **Success Response (200 OK):**
    ```json
    {
      "from": "Kajang",
      "path": ["Kajang", "Stadium Kajang", "Sungai Jernih", "Batu 11 Cheras"],
      "to": "Batu 11 Cheras",
      "total_fare": 2.5
    }
    ```
---

## Real-Time WebSocket Events

The server uses WebSockets to push live updates to all connected clients. The frontend client should listen for the following events using `socket.on()`.

### Event: `new_train_position`

This is the primary event for live data. It is broadcast by the server every few seconds with the updated position of a simulated train.

*   **Direction:** Server → Client
*   **Purpose:** To provide the live location of a train for map animation.
*   **Data Payload:** A JSON object with the following structure:
    ```json
    {
      "train_id": "Train-1234",
      "current_station": "Kajang",
      "timestamp": 1662783451.123
    }
    ```
*   **Client-Side Usage Example:**
    ```javascript
    socket.on('new_train_position', (data) => {
        console.log(`Train ${data.train_id} is at station ${data.current_station}`);
        // Logic to find and update a marker on the Leaflet map would go here.
    });
    ```

### Event: `welcome_message`

A message sent once to a client immediately after it successfully connects.

*   **Direction:** Server → Client
*   **Purpose:** To confirm that the WebSocket connection has been established successfully.
*   **Data Payload:**
    ```json
    {
        "data": "Welcome to the real-time server!"
    }
    ```