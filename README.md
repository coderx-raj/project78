# Thief Detection Backend

This is the backend service for the Thief Detection System. It provides face detection and matching capabilities using OpenCV and face_recognition libraries.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create required directories:
```bash
mkdir uploads surveillance
```

3. Add surveillance videos:
Place your surveillance video files (*.mp4) in the `surveillance` directory.

## Running the Server

Start the FastAPI server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/upload`: Upload a photo to search for matches in surveillance videos
- `GET /api/status`: Get system status and surveillance video count

## Notes

- The system processes every 30th frame of surveillance videos for performance
- Face matching threshold is set to 0.6 (lower is more strict)
- Uploaded photos are stored in the `uploads` directory
- Surveillance videos should be in MP4 format