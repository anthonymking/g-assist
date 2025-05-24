# Google Calendar and Gmail Integration

This Python application allows you to connect to your Google Calendar and Gmail account using the Google API. It provides functionality to view calendar events and send emails.

## Setup Instructions

1. First, install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up Google Cloud Project and obtain credentials:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Enable the Google Calendar API and Gmail API for your project
   - Go to "Credentials"
   - Click "Create Credentials" and select "OAuth client ID"
   - Choose "Desktop application" as the application type
   - Download the credentials and save them as `credentials.json` in this project directory

3. Run the application:
   ```bash
   python google_calendar_gmail.py
   ```

   The first time you run the application, it will open a browser window asking you to authorize the application. After authorization, it will save the credentials in a `token.pickle` file for future use.

## Features

- View upcoming calendar events
- Send emails using Gmail API

## Security Note

- Keep your `credentials.json` and `token.pickle` files secure and never share them
- These files contain sensitive information that grants access to your Google account
- If you suspect your credentials have been compromised, revoke them immediately in the Google Cloud Console

## Usage

The script includes example functions for:
- Listing calendar events
- Sending emails

You can modify the main section of the script to test different functionality or integrate these functions into your own applications.

## Running the ChatGPT Plugin API

1. Install the new dependencies (if you haven't already):
   ```bash
   pip install -r requirements.txt
   ```

2. Start the FastAPI server:
   ```bash
   uvicorn plugin_api:app --reload
   ```

3. Visit `http://localhost:8000/docs` in your browser to test the endpoints interactively.

4. For ChatGPT plugin integration, you will need to deploy this API to a public URL and add the plugin manifest files (see below). 