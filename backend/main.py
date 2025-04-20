import os
import random
import smtplib
import re
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, File, Form, UploadFile, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime
import supabase
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from typing import Optional

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

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Security for webhook endpoint
API_KEY_NAME = "X-API-KEY"
API_KEY = os.getenv("WEBHOOK_API_KEY")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

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

# Dictionary to keep track of user UUIDs by email (to retrieve their images later)
user_email_to_uuid = {}

async def get_api_key(api_key_header: str = Depends(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(status_code=403, detail="Could not validate API key")

def send_email_alert(user_email, frame_number, timestamp, user_uuid, image_url=None):
    """Send an email alert to the user when a fire is detected."""
    try:
        # Store the email-to-uuid mapping for later use
        user_email_to_uuid[user_email] = user_uuid
        
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = user_email
        msg['Subject'] = "🔥 URGENT: Fire Detection Alert! 🔥"
        
        # Email body with reply instructions
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
            <hr>
            <p><strong>Need an update?</strong> You can reply to this email with:</p>
            <ul>
                <li><strong>STATUS</strong> - To get an AI analysis of the current fire situation</li>
                <li><strong>CALL</strong> - To request emergency services (coming soon)</li>
            </ul>
            <p><em>This is an automated message from your fire monitoring system.</em></p>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            print("SENDING EMAIL")
            server.send_message(msg)
        
        print(f"Email alert sent to {user_email}")
        return True
    except Exception as e:
        print(f"Error sending email alert: {e}")
        return False

async def get_latest_fire_image(user_uuid):
    """Get the most recent fire image for a specific user from Supabase storage."""
    try:
        # List all objects in the user's directory
        list_result = supabase_client.storage.from_("fireimages").list(user_uuid)
        
        sorted_files = sorted(list_result, key=lambda x: x['name'], reverse=True)
        
        if not sorted_files:
            return None
        
        # Get the latest file
        latest_file = sorted_files[0]
        file_path = f"{user_uuid}/{latest_file['name']}"
        
        # Download the file content
        response = supabase_client.storage.from_("fireimages").download(file_path)
        
        # Get the public URL for reference
        public_url = supabase_client.storage.from_("fireimages").get_public_url(file_path)
        
        return {
            "content": response,
            "name": latest_file['name'],
            "url": public_url
        }
    except Exception as e:
        print(f"Error retrieving latest fire image: {e}")
        return None

async def analyze_fire_image_with_gemini(image_data):
    """Use Gemini to analyze a fire image and provide insights."""
    try:
        # Convert image data to base64 for Gemini
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Initialize Gemini model for multimodal inputs
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Create a prompt for fire analysis
        prompt = """
        Analyze this fire image and provide a detailed assessment. Include:
        1. Severity level (low, medium, high, extreme)
        2. Visible flame characteristics
        3. Smoke density and color
        4. Probable fire type (electrical, chemical, natural material, etc.)
        5. Potential spread risk
        6. Any visible hazards or concerns
        7. Brief recommendations for immediate action

        Format your response in an easy-to-read manner suitable for someone checking on a fire alert.
        """
        
        # Create the multimodal inputs
        image_part = {
            "mime_type": "image/jpeg", 
            "data": image_base64
        }
        
        contents = [prompt, image_part]
        
        # Generate the response from Gemini
        response = model.generate_content(contents)
        
        return response.text
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return "Unable to analyze the fire image at this moment. Please check the visual directly or contact emergency services if the situation appears dangerous."

def send_status_response_email(to_email, analysis_text, image_url):
    """Send a response email with fire status analysis."""
    try:
        # Create the email message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        msg['Subject'] = "Fire Status Analysis - Automated Response"
        
        # Current time for the report
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Email body with the analysis
        body = f"""
        <html>
        <body>
            <h2>🔍 Fire Status Analysis Report</h2>
            <p>Time of Report: {current_time}</p>
            <p>Below is an AI-powered analysis of the most recent fire image:</p>
            
            <div style="background-color: #f8f9fa; border-left: 4px solid #ff6b6b; padding: 15px; margin: 15px 0;">
                {analysis_text.replace('\n', '<br>')}
            </div>
            
            <p>Reference Image: <a href="{image_url}">View Image</a></p>
            
            <p><strong>Important:</strong> This is an automated analysis. In case of an actual emergency, please contact emergency services immediately.</p>
            
            <p>You can continue to reply with:</p>
            <ul>
                <li><strong>STATUS</strong> - For an updated analysis</li>
                <li><strong>CALL</strong> - To request emergency services (coming soon)</li>
            </ul>
            
            <p><em>This is an automated message from your fire monitoring system.</em></p>
        </body>
        </html>
        """
        
        # Attach HTML content
        msg.attach(MIMEText(body, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"Status analysis email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending status response email: {e}")
        return False

@app.post("/email-webhook", dependencies=[Depends(get_api_key)])
async def email_webhook(request: Request):
    """Handle incoming email webhook requests (for replies to alert emails)."""
    try:
        data = await request.json()
        
        # Extract the sender email and the message body
        # The exact structure will depend on your email webhook provider
        sender_email = data.get("from", "").lower()
        subject = data.get("subject", "")
        body_text = data.get("text", "").strip().upper()
        
        # Check if this is a reply to our alert (may need customization based on your webhook provider)
        is_reply = "URGENT: Fire Detection Alert" in subject
        
        if not is_reply:
            return {"status": "ignored", "reason": "Not a reply to alert email"}
        
        # Check for STATUS command
        if "STATUS" in body_text:
            # Look up the user UUID based on their email
            user_uuid = user_email_to_uuid.get(sender_email)
            
            if not user_uuid:
                return {"status": "error", "reason": "User UUID not found for this email"}
            
            # Get the latest fire image for this user
            latest_image = await get_latest_fire_image(user_uuid)
            
            if not latest_image:
                return {"status": "error", "reason": "No fire images found for this user"}
            
            # Analyze the image with Gemini
            analysis = await analyze_fire_image_with_gemini(latest_image["content"])
            
            # Send the analysis back to the user
            email_sent = send_status_response_email(
                to_email=sender_email,
                analysis_text=analysis,
                image_url=latest_image["url"]
            )
            
            return {
                "status": "success" if email_sent else "error",
                "command": "STATUS",
                "action": "Analysis sent" if email_sent else "Failed to send analysis"
            }
        
        # Handle CALL command (placeholder for now)
        elif "CALL" in body_text:
            return {
                "status": "received",
                "command": "CALL",
                "action": "Feature coming soon"
            }
        
        # Unknown command
        else:
            return {
                "status": "ignored",
                "reason": "No recognized command in email"
            }
            
    except Exception as e:
        print(f"Error processing email webhook: {e}")
        return {"status": "error", "error": str(e)}

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
                    user_uuid=user_uuid,  # Pass user_uuid to store the mapping
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