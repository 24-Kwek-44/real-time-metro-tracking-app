# Real-Time Metro Tracking Application

This is the group project for UEEN3123/UEEN3433, building a real-time metro tracking app using Flask, SQLite, and WebSockets/MQTT.

## Initial Project Setup

Follow these steps to get the project running locally.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/24-Kwek-44/real-time-metro-tracking-app.git
    cd real-time-metro-tracking-app
    ```

2.  **Download the Dataset:**
    The dataset is not tracked by Git. Please download the required CSV files from the official source:
    *   **[Kaggle: MyRapidKL Train Dataset](https://www.kaggle.com/datasets/niknmarjan/myrapidkl-train-dataset)**

3.  **Place the Dataset:**
    After downloading, place the CSV files into the `data/` folder in the project's root directory. The `database.py` script will expect to find them there.

4.  **Set up a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

5.  **Install Dependencies:**
    (This file will be updated as we add libraries)
    ```bash
    pip install -r requirements.txt
    ```