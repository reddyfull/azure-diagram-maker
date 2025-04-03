# Icon Upload Server

This server handles the upload of SVG icon files to both local storage and Google Cloud Storage.

## Features

- Upload ZIP files containing SVG icons
- Store icons locally in the file system
- Upload icons to Google Cloud Storage (when credentials are available)
- List all available icons from both local and cloud storage
- Health check endpoint for monitoring

## Requirements

- Python 3.6 or higher
- Flask
- Flask-CORS
- Google Cloud Storage Python client

## Running the Server

### Method 1: Using the start script

```bash
./start-python-server.sh
```

This script will:
1. Check if Python is installed
2. Install required dependencies
3. Start the server on port 3001

### Method 2: Manual Installation

```bash
# Install dependencies
pip install flask flask-cors google-cloud-storage

# Run the server
python upload.py
```

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/upload/icons` - Upload a ZIP file containing SVG icons
- `GET /api/icons` - List all available icons
- `GET /cloudicons/<provider>/<filename>` - Serve icons from local storage

## Configuration

- Google Cloud Storage credentials should be in a file named `gcs-key.json` in the parent directory
- If GCS credentials are not available, the server will fall back to local storage only

## Local Storage

Icons are stored locally in the `public/cloudicons/<provider>` directory and can be accessed via:
```
http://localhost:3001/cloudicons/<provider>/<icon_name>.svg
``` 