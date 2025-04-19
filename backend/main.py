import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Email configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")  
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))  
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME") 
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")  
EMAIL_FROM = os.getenv("EMAIL_FROM", EMAIL_USERNAME)  

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

# Keep track of users who have already been notified (to avoid spam)
notified_users = set()

def send_email_alert(user_email, frame_number, timestamp, image_url=None):
    """Send an email alert to the user when a fire is detected."""
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = user_email
        msg['Subject'] = "🔥 URGENT: Fire Detection Alert! 🔥"
        
        # Email body
        body = f"""
        <html>
        <body>
            <h2>⚠️ Fire Detection Alert ⚠️</h2>
            <p>Our system has detected a potential fire in your video processing.</p>
            <p><strong>Details:</strong></p>
            <ul>
                <li>Frame Number: {frame_number}</li>
                <li>Timestamp: {timestamp:.2f} seconds</li>
                <li>Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
            </ul>
            {"<p>You can view the detected frame here: <a href='" + image_url + "'>View Image</a></p>" if image_url else ""}
            <p>Please check your monitoring system immediately and take appropriate action.</p>
            <p><em>This is an automated message. Please do not reply to this email.</em></p>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            print("SENFDING EMAIL")
            server.send_message(msg)
        
        print(f"Email alert sent to {user_email}")
        return True
    except Exception as e:
        print(f"Error sending email alert: {e}")
        return False

@app.post("/test")
async def receive_data(
    frame_number: int = Form(...),
    timestamp: float = Form(...),
    user_uuid: str = Form(...),
    user_email: str = Form(None),  # Make email optional
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
            
            # Send email alert if user email is provided and they haven't been notified yet
            # Using a combination of UUID and frame/100 to limit notifications
            notification_key = f"{user_uuid}_{frame_number // 100}"
            
            if user_email and notification_key not in notified_users:
                # Send email with the image URL
                email_sent = send_email_alert(
                    user_email=user_email,
                    frame_number=frame_number,
                    timestamp=timestamp,
                    image_url=public_url
                )
                
                if email_sent:
                    notified_users.add(notification_key)
                    response_data["email_alert"] = "sent"
                else:
                    response_data["email_alert"] = "failed"
            elif notification_key in notified_users:
                response_data["email_alert"] = "already_notified"
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            response_data["supabase_error"] = str(e)
    
    return response_data

# Optional: Periodically clear the notification tracking set (e.g., every 30 minutes)
@app.on_event("startup")
async def startup_event():
    # You could implement a background task here to clear notified_users
    # periodically to allow new notifications after some time has passed
    pass