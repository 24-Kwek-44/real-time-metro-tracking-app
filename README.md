# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking app using Flask, SQLite, and WebSockets.

## Project Setup & Running Instructions

### 1. Initial Setup

Follow these steps to get the project set up locally.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/24-Kwek-44/real-time-metro-tracking-app.git
    cd real-time-metro-tracking-app
    ```

2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    # On macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download and Place the Dataset:**
    The dataset is not tracked by Git. Please download the required CSV files from the official source:
    *   **[Kaggle: MyRapidKL Train Dataset](https://www.kaggle.com/datasets/niknmarjan/myrapidkl-train-dataset)**
    
    After downloading, place the `Fare.csv` and `Route.csv` files into the `data/` folder in the project's root directory.

5.  **Initialize the Database:**
    Run the `database.py` script once to create and populate the `db.sqlite` file.
    ```bash
    python database.py
    ```

### 2. Running the Application

The application requires two separate processes to be running concurrently.

1.  **Start the Main Flask Server:**
    This server runs the backend API and the WebSocket hub.
    ```bash
    python app.py
    ```
    The server will be running on `http://127.0.0.1:5000`.

2.  **Start the Data Generator:**
    In a **new, separate terminal window**, activate the virtual environment again and start the data generator. This will simulate and publish live train data to the main server.
    ```bash
    # (In a new terminal)
    # venv\Scripts\activate
    python data_generator.py
    ```

3.  **Access the Kiosk Interface:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## Backend API Documentation

The backend server provides a set of RESTful API endpoints to interact with the metro system data. All API routes are prefixed with `/api`.

### 1. Get All Stations

Returns a list of all unique station names in the system.

*   **URL:** `/stations`
*   **Method:** `GET`
*   **Success Response (Code 200 OK):**
    ```json
    [
        { "name": "Abdullah Hukum" },
        { "name": "Alam Megah" },
        { "name": "Ampang Park" },
        ...
    ]
    ```

### 2. Get Fare Between Two Stations

Returns the direct fare for a single travel segment between two stations.

*   **URL:** `/fare`
*   **Method:** `GET`
*   **Query Parameters:**
    *   `from` (string, required): The name of the origin station.
    *   `to` (string, required): The name of the destination station.
*   **Example URL:** `/api/fare?from=Kajang&to=Muzium Negara`
*   **Success Response (Code 200 OK):**
    ```json
    {
      "from": "Kajang",
      "price": 3.3,
      "to": "Muzium Negara"
    }
    ```
*   **Error Responses:**
    *   `404 Not Found`: If the specific fare is not in the database.
    *   `400 Bad Request`: If `from` or `to` parameters are missing.

### 3. Get Route Between Two Stations

Calculates and returns the shortest path (by number of stops) and the total fare between two stations.

*   **URL:** `/route`
*   **Method:** `GET`
*   **Query Parameters:**
    *   `from` (string, required): The name of the origin station.
    *   `to` (string, required): The name of the destination station.
*   **Example URL:** `/api/route?from=Kajang&to=Batu+11+Cheras`
*   **Success Response (Code 200 OK):**
    ```json
    {
      "from": "Kajang",
      "path": [
        "Kajang",
        "Stadium Kajang",
        "Sungai Jernih",
        "Batu 11 Cheras"
      ],
      "to": "Batu 11 Cheras",
      "total_fare": 2.5
    }
    ```
*   **Error Responses:**
    *   `404 Not Found`: If no path exists or a station is not in the network.
    *   `400 Bad Request`: If `from` or `to` parameters are missing.