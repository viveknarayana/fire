import os
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a directory to store frames if it doesn't exist
UPLOAD_DIR = "uploaded_frames"
os.makedirs(UPLOAD_DIR, exist_ok=True)

seen = []

@app.post("/test")
async def receive_data(
    frame_number: int = Form(...),
    timestamp: float = Form(...),
    image_data: UploadFile = File(...)
):
    # Get file content
    file_content = await image_data.read()
    file_size = len(file_content)
    
    # Generate a unique filename using timestamp and frame number
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"frame_{frame_number}_time_{timestamp:.2f}_{timestamp_str}.jpg"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    print(f"Received frame {frame_number} at timestamp {timestamp}")
    print(f"Saved image to {file_path}, size: {file_size} bytes")
    
    # Reset file stream position for potential further operations
    await image_data.seek(0)
    
    return {
        "message": "Frame received and saved", 
        "frame": frame_number,
        "saved_path": file_path
    }