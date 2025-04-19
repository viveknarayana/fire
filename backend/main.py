import os
import random
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import supabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# Initialize Supabase client
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase_client = supabase.create_client(supabase_url, supabase_key)

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
    user_uuid: str = Form(...), 
    user_email: str = Form(...), 
    image_data: UploadFile = File(...)
):
    # Get file content
    file_content = await image_data.read()
    file_size = len(file_content)
    
    # Simulate fire detection with 10% probability FOR TESTINTG
    fire_detected = random.random() < 0.4  
    confidence_score = random.uniform(0.9, 0.99) if fire_detected else random.uniform(0.1, 0.89)
    
    response_data = {
        "message": "Frame received", 
        "frame": frame_number,
        "user_uuid": user_uuid,
        "user_email": user_email,
        "fire_detected": fire_detected,
        "confidence_score": confidence_score
    }
    
    # If fire detected, upload to Supabase
    if fire_detected:
        try:
            await image_data.seek(0)
            
            supabase_filename = f"{user_uuid}/{user_uuid}_fire_frame_{frame_number}.jpg"
            

            upload_result = supabase_client.storage.from_("fireimages").upload(
                supabase_filename,
                file_content,
                file_options={"content-type": "image/jpeg"}
            )
            
            # Get public URL for the uploaded file
            public_url = supabase_client.storage.from_("fireimages").get_public_url(supabase_filename)
        
            print(f"Fire detected! Uploaded to Supabase: {public_url}")
            
            response_data["supabase_url"] = public_url
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            response_data["supabase_error"] = str(e)
    
    return response_data
