# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking and routing application using Flask, SQLite, Pandas, and WebSockets.

**Note:** The most up-to-date and complete version of this project is on the **`develop`** branch.

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

2.  **Set up a Virtual Environment (Recommended):**

    ```bash
    # On Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install Dependencies:**
    This will install Flask, Pandas, and all other required libraries.

    ```bash
    pip install -r requirements.txt
    ```

4.  **Download the Required CSV Files:**
    The project uses external CSV files as the raw data source.

    - Download the dataset from: **[Kaggle: MyRapidKL Train Dataset](https://www.kaggle.com/datasets/niknmarjan/myrapidkl-train-dataset)**
    - From the downloaded files, place `Fare.csv`, `Route.csv`, and `Time.csv` into the `data/` folder in your project's root directory.

5.  **Initialize the Database (Critical One-Time Step):**
    Run the `database.py` script once. This script performs an **ETL (Extract, Transform, Load)** process: it reads the raw CSVs, cleans and filters the data, enriches it with verified coordinates, and loads the final, clean dataset into a `db.sqlite` file.
    ```bash
    python database.py
    ```
    After this step, your `db.sqlite` database is complete and ready for the application to use.

### 2. Running the Application

The application requires two separate processes to be running concurrently.

1.  **Start the Main Flask Server (in Terminal 1):**
    This server reads the clean data from `db.sqlite` into an in-memory model for high performance.

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
