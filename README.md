# Automated Building Layout Generator

This project generates strict building layouts for a 200m x 140m site using a Python backend and (optionally) a Web Interface.

## Features
*   Strict adherence to geometric rules (Setbacks, Distance, Plaza).
*   Randomized exploration algorithm.
*   **Web Interface**: Interactive visualization and statistics.
*   **CLI Mode**: Generate static images directly.

## Requirements
*   Python 3.x
*   `matplotlib`, `numpy`, `flask`

## Setup
Install dependencies:
```bash
pip install -r requirements.txt
```

## How to Run (Web Platform)
1.  Start the Flask server:
    ```bash
    python app.py
    ```
2.  Open your browser and navigate to:
    `http://127.0.0.1:5000`
3.  Click **"Generate New Layouts"** to visualize.

## How to Run (CLI Only)
To generate static images without the web server:
```bash
python layout_generator.py
```

## Rules Implemented
*   **Site**: 200m x 140m
*   **Plaza**: 40m x 40m (Reserved Center)
*   **Setback**: 10m from boundary
*   **Min Distance**: 15m between buildings
*   **Neighbour-Mix**: Every Tower A has a Tower B within 60m.
