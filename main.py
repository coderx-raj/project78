from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import face_recognition
from typing import List
import os
from datetime import datetime
import json
from pathlib import Path

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create directories for storing uploads and surveillance videos
UPLOAD_DIR = Path("uploads")
SURVEILLANCE_DIR = Path("surveillance")
UPLOAD_DIR.mkdir(exist_ok=True)
SURVEILLANCE_DIR.mkdir(exist_ok=True)

class FaceDetector:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_metadata = []
    
    def encode_face(self, image_path: str):
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        if not face_locations:
            return None
        return face_recognition.face_encodings(image, face_locations)[0]
    
    def search_in_video(self, video_path: str, target_encoding) -> List[dict]:
        matches = []
        video = cv2.VideoCapture(str(video_path))
        frame_count = 0
        
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
                
            # Process every 30th frame for performance
            if frame_count % 30 == 0:
                # Convert BGR to RGB
                rgb_frame = frame[:, :, ::-1]
                
                # Find faces in frame
                face_locations = face_recognition.face_locations(rgb_frame)
                if face_locations:
                    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
                    
                    for face_encoding in face_encodings:
                        # Compare faces
                        distance = face_recognition.face_distance([target_encoding], face_encoding)[0]
                        if distance < 0.6:  # Threshold for face matching
                            confidence = round((1 - distance) * 100)
                            timestamp = video.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
                            matches.append({
                                "video_path": str(video_path),
                                "timestamp": timestamp,
                                "confidence": confidence,
                                "frame_number": frame_count
                            })
            
            frame_count += 1
            
        video.release()
        return matches

face_detector = FaceDetector()

@app.post("/api/upload")
async def upload_photo(file: UploadFile = File(...)):
    # Save uploaded file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # Encode the target face
    target_encoding = face_detector.encode_face(str(file_path))
    if target_encoding is None:
        return {"error": "No face detected in the uploaded image"}
    
    # Search in all surveillance videos
    all_matches = []
    for video_file in SURVEILLANCE_DIR.glob("*.mp4"):
        matches = face_detector.search_in_video(video_file, target_encoding)
        all_matches.extend(matches)
    
    # Sort matches by confidence
    all_matches.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {"matches": all_matches}

@app.get("/api/status")
async def get_status():
    surveillance_count = len(list(SURVEILLANCE_DIR.glob("*.mp4")))
    return {
        "status": "operational",
        "surveillance_videos": surveillance_count,
        "last_updated": datetime.now().isoformat()
    }