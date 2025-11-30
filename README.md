# My Diary App

A simple, elegant diary application that saves your entries directly to a Google Doc.

## Features

-   **Clean Interface**: A distraction-free writing environment with a soothing design.
-   **Google Docs Integration**: Automatically appends your entries to a "My New Diary" Google Doc.
-   **Smart Formatting**:
    -   Entries are dated automatically.
    -   Dates are bolded and formatted (e.g., "Sunday, Nov 30, 2025").
    -   Entry text uses **Times New Roman, size 11**.

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/offtrail/my_diary.git
    cd my_diary
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Google Cloud Setup**:
    -   Create a project in [Google Cloud Console](https://console.cloud.google.com/).
    -   Enable **Google Docs API** and **Google Drive API**.
    -   Configure OAuth consent screen (add yourself as a test user).
    -   Create OAuth 2.0 Client ID (Desktop app).
    -   Download the JSON file, rename it to `credentials.json`, and place it in the project root.

4.  **Run the application**:
    ```bash
    python server.py
    ```

5.  **Open in Browser**:
    Visit `http://localhost:5000` to start writing.

## Note on Deployment

This application uses a Python Flask backend to communicate with Google APIs. It **cannot** be hosted on static site hosting services like GitHub Pages. It requires a server environment (e.g., Heroku, Render, or a local machine).
