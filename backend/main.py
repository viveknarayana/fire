import os
import random
import asyncio
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware

# Import services
from services.storage_service import upload_fire_image
from services.email_service import send_email_alert, notified_users, start_email_polling_thread
from models.schemas import FireDetectionResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/test")
async def receive_data(
    frame_number: int = Form(...),
    timestamp: float = Form(...),
    user_uuid: str = Form(...),
    user_email: str = Form(None),
    image_data: UploadFile = File(...)
):
    # Get file content
    file_content = await image_data.read()
    file_size = len(file_content)
    
    # Simulate fire detection with 40% probability FOR TESTING
    fire_detected = random.random() < 0.4
    confidence_score = random.uniform(0.9, 0.99) if fire_detected else random.uniform(0.1, 0.89)
    
    response_data = {
        "message": "Frame received", 
        "frame": frame_number,
        "user_uuid": user_uuid,
        "fire_detected": fire_detected,
        "confidence_score": confidence_score
    }
    
    # Add email to response if provided
    if user_email:
        response_data["user_email"] = user_email
    
    # If fire detected, upload to Supabase and send email alert
    if fire_detected:
        try:
            await image_data.seek(0)
            file_content = await image_data.read()
            
            # Upload to Supabase
            upload_result = await upload_fire_image(user_uuid, frame_number, file_content)
            
            if upload_result["success"]:
                public_url = upload_result["url"]
                response_data["supabase_url"] = public_url
                
                # Send email alert if user email is provided and they haven't been notified yet
                # Using a combination of UUID and frame/100 to limit notifications
                notification_key = f"{user_uuid}_{frame_number // 100}"
                
                if user_email and notification_key not in notified_users:
                    # Send email with the image URL
                    email_sent = send_email_alert(
                        user_email=user_email,
                        frame_number=frame_number,
                        timestamp=timestamp,
                        user_uuid=user_uuid,
                        image_url=public_url
                    )
                    
                    if email_sent:
                        notified_users.add(notification_key)
                        response_data["email_alert"] = "sent"
                    else:
                        response_data["email_alert"] = "failed"
                elif notification_key in notified_users:
                    response_data["email_alert"] = "already_notified"
            else:
                response_data["supabase_error"] = upload_result["error"]
            
        except Exception as e:
            print(f"Error processing file: {e}")
            response_data["error"] = str(e)
    
    return response_data

@app.on_event("startup")
async def startup_event():
    """Start email polling service on application startup."""
    start_email_polling_thread()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)