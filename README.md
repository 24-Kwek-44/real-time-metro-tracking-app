# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking and routing application using Flask, SQLite, and WebSockets.

**Note:** The most up-to-date code is on the **`develop`** branch. Please ensure you are using this branch for your work.

---

## Project Setup & Running Instructions

### 1. Initial Setup

Follow these steps to get the project fully configured and running locally.

1.  **Clone the Repository and Switch to the `develop` Branch:**
    ```bash
    git clone https://github.com/24-Kwek-44/real-time-metro-tracking-app.git
    cd real-time-metro-tracking-app
    git checkout develop
    ```

2.  **Obtain and Place the Database File:**
    This project requires a specific, pre-populated `db.sqlite` file which contains manually added station coordinates.
    *   **Action Required:** This file has been shared separately in our group's **WhatsApp chat**.
    *   Please download `db.sqlite` from the chat and place it in the main root directory of your project folder (the same folder that contains `app.py`).
    *   **(Optional) Verify:** You can open this `db.sqlite` file with "DB Browser for SQLite" to confirm that the `stations` table contains the `latitude` and `longitude` data.

3.  **Set up a Virtual Environment (Recommended):**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
5.  **IMPORTANT:** Do **NOT** run the `python database.py` script. This will overwrite the complete database with a blank one. The database is ready to use once you place the file.

### 2. Running the Application

The application requires two separate processes to be running concurrently.

1.  **Start the Main Flask Server (in Terminal 1):**
    ```bash
    python app.py
    ```
    The server will run on `http://127.0.0.1:5000`.

2.  **Start the Data Generator (in Terminal 2):**
    ```bash
    # (Activate venv first)
    python data_generator.py
    ```

3.  **Access the Kiosk Interface:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## Backend API Documentation (`develop` branch version)

The backend provides RESTful API endpoints for request-response data and WebSocket events for real-time data.

### REST API Endpoints (prefixed with `/api`)

#### **1. GET /stations**
Returns a complete list of all stations, including their names and geographic coordinates.

*   **URL:** `/stations`
*   **Method:** `GET`
*   **Success Response (200 OK):**
    ```json
    [
      {
        "name": "Abdullah Hukum",
        "latitude": 3.1188,
        "longitude": 101.6732
      },
      {
        "name": "Alam Megah",
        "latitude": 3.0009,
        "longitude": 101.5645
      },
      ...
    ]
    ```

#### **2. GET /fare**
Returns the direct fare between two specified stations.

*   **URL:** `/fare`
*   **Method:** `GET`
*   **Query Parameters:**
    *   `from` (string, required): The name of the origin station.
    *   `to` (string, required): The name of the destination station.
*   **Example URL:** `/api/fare?from=Kajang&to=Gombak`
*   **Success Response (200 OK):**
    ```json
    {
      "from": "Kajang",
      "price": 6.8,
      "to": "Gombak"
    }
    ```

#### **3. GET /route**
Calculates the shortest path (by number of stops) and total fare between two stations.

*   **URL:** `/route`
*   **Method:** `GET`
*   **Query Parameters:**
    *   `from` (string, required): The name of the origin station.
    *   `to` (string, required): The name of the destination station.
*   **Example URL:** `/api/route?from=Kajang&to=Gombak`
*   **Success Response (200 OK):**
    ```json
    {
      "from": "Kajang",
      "path": [ "Kajang", "Stadium Kajang", ... , "Gombak" ],
      "to": "Gombak",
      "total_fare": 6.8
    }
    ```

### Real-Time WebSocket Events

The server pushes live updates to clients. The frontend should use `socket.on()` to listen for these events.

#### **Event: `new_train_position`**
Broadcast by the server every few seconds with an updated train position.

*   **Direction:** Server → Client
*   **Purpose:** To provide the live location of a train for map animation.
*   **Data Payload:**
    ```json
    {
      "train_id": "Train-1234",
      "current_station": "Kajang"
    }
    ```
*   **Client-Side Usage Example:**
    ```javascript
    socket.on('new_train_position', (data) => {
        console.log(`Train ${data.train_id} is at station ${data.current_station}`);
        // Frontend logic to find and update a marker on the Leaflet map goes here.
    });
    ```