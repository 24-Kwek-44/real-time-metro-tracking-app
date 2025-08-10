# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking and routing application using Flask, SQLite, and WebSockets.

**Note:** The most up-to-date and complete version of this project is on the **`develop`** branch. Please ensure you are using this branch for your work.

---

## Project Setup & Running Instructions

### 1. Initial Setup

Follow these steps to get the project fully configured and running locally. This entire process is automated by the provided scripts.

1.  **Clone the Repository and Switch to the `develop` Branch:**
    ```bash
    git clone https://github.com/24-Kwek-44/real-time-metro-tracking-app.git
    cd real-time-metro-tracking-app
    git checkout develop
    ```

2.  **Set up a Virtual Environment (Recommended):**
    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Required CSV Files:**
    The project uses two external CSV files for data, which are not tracked by Git.
    *   Download the dataset from: **[Kaggle: MyRapidKL Train Dataset](https://www.kaggle.com/datasets/niknmarjan/myrapidkl-train-dataset)**
    *   From the downloaded files, place `Fare.csv` and `Route.csv` into the `data/` folder in your project's root directory.

5.  **Initialize the Database (One-Time Step):**
    Run the `database.py` script once. This script will automatically:
    *   Create the `db.sqlite` file and the required table schema.
    *   Read the CSVs to ingest fare and connection data.
    *   Enrich the station data with a built-in dictionary of verified coordinates.
    ```bash
    python database.py
    ```
    After this step, your database will be complete and ready to use.

### 2. Running the Application

The application requires two separate processes to be running concurrently.

1.  **Start the Main Flask Server (in Terminal 1):**
    ```bash
    # Make sure your venv is active
    python app.py
    ```
    The server will run on `http://127.0.0.1:5000`.

2.  **Start the Data Generator (in Terminal 2):**
    ```bash
    # Make sure your venv is active
    python data_generator.py
    ```

3.  **Access the Kiosk Interface:**
    Open your web browser and navigate to `http://127.0.0.1:5000`.

---

## Backend API Documentation

The backend provides RESTful API endpoints and WebSocket events.

### REST API Endpoints (prefixed with `/api`)

#### **GET /stations**
Returns a complete list of all stations, including their names and geographic coordinates.

*   **Success Response (200 OK):**
    ```json
    [
      {
        "name": "Abdullah Hukum",
        "latitude": 3.1188319,
        "longitude": 101.6732377
      },
      ...
    ]
    ```

#### **GET /route**
Calculates the shortest path (by number of stops) and total fare between two stations.

*   **Query Params:** `from` (string), `to` (string)
*   **Example URL:** `http://127.0.0.1:5000/api/route?from=Kajang&to=Gombak`
*   **Success Response (200 OK):**
    ```json
    {
      "from": "Kajang",
      "path": ["Kajang", "Stadium Kajang", ..., "Gombak"],
      "to": "Gombak",
      "total_fare": 37.2
    }
    ```

### Real-Time WebSocket Events

The server pushes live updates to clients. The frontend should use `socket.on()` to listen for these events.

#### **Event: `new_train_position`**
Broadcast by the server every few seconds with an updated train position.

*   **Data Payload:**
    ```json
    {
      "train_id": "Train-1234",
      "current_station": "Kajang"
    }
    ```
*(The rest of your WebSocket and `/fare` documentation is perfect and can be copied in as is.)*