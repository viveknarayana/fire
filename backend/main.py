import os
import random
import re
import base64
from fastapi import FastAPI, File, Form, UploadFile, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader, APIKey
from datetime import datetime
import supabase
from dotenv import load_dotenv
import google.generativeai as genai
import requests
from typing import Optional
from pyngrok import ngrok
from mailjet_rest import Client  # Import for Mailjet

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# Setup ngrok tunnel
public_url = ngrok.connect(8000)
print(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:8000\"")

# Initialize Supabase client
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase_client = supabase.create_client(supabase_url, supabase_key)

# Mailjet configuration
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Fire Detection System")
print(f"EMAIL_FROM: {EMAIL_FROM}")
print(f"EMAIL_FROM_NAME: {EMAIL_FROM_NAME}")
# Initialize Mailjet client
mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3.1')

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
    """Send an email alert to the user when a fire is detected using Mailjet API."""
    try:
        # Store the email-to-uuid mapping for later use
        user_email_to_uuid[user_email] = user_uuid
        print(f"User email {user_email} mapped to UUID {user_uuid}")
        
        # Email body with reply instructions
        html_body = f"""
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
        
        # Text version for clients that don't support HTML
        text_body = f"""
        ⚠️ Fire Detection Alert ⚠️
        
        Our system has detected a potential fire in your video processing.
        
        Details:
        - Frame Number: {frame_number}
        - Timestamp: {timestamp:.2f} seconds
        - Detection Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        {"You can view the detected frame here: " + image_url if image_url else ""}
        
        Please check your monitoring system immediately and take appropriate action.
        
        Need an update? You can reply to this email with:
        - STATUS - To get an AI analysis of the current fire situation
        - CALL - To request emergency services (coming soon)
        
        This is an automated message from your fire monitoring system.
        """
        
        # Create Mailjet email data structure
        data = {
            'Messages': [
                {
                    'From': {
                        'Email': EMAIL_FROM,
                        'Name': EMAIL_FROM_NAME
                    },
                    'To': [
                        {
                            'Email': user_email
                        }
                    ],
                    'Subject': "🔥 URGENT: Fire Detection Alert! 🔥",
                    'TextPart': text_body,
                    'HTMLPart': html_body,
                    'CustomID': f"fire_alert_{user_uuid}_{frame_number}"
                }
            ]
        }
        
        # Send the email using Mailjet API
        print("SENDING EMAIL VIA MAILJET")
        result = mailjet.send.create(data=data)
        
        # Check if the email was sent successfully
        if result.status_code == 200:
            print(f"Email alert sent to {user_email}")
            return True
        else:
            print(f"Failed to send email: {result.status_code}, {result.json()}")
            return False
            
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
    """Send a response email with fire status analysis using Mailjet API."""
    try:
        # Current time for the report
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # HTML body with the analysis
        html_body = f"""
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
        
        # Text version
        text_body = f"""
        🔍 Fire Status Analysis Report
        
        Time of Report: {current_time}
        
        Below is an AI-powered analysis of the most recent fire image:
        
        {analysis_text}
        
        Reference Image: {image_url}
        
        Important: This is an automated analysis. In case of an actual emergency, please contact emergency services immediately.
        
        You can continue to reply with:
        - STATUS - For an updated analysis
        - CALL - To request emergency services (coming soon)
        
        This is an automated message from your fire monitoring system.
        """
        
        # Create Mailjet email data structure
        data = {
            'Messages': [
                {
                    'From': {
                        'Email': EMAIL_FROM,
                        'Name': EMAIL_FROM_NAME
                    },
                    'To': [
                        {
                            'Email': to_email
                        }
                    ],
                    'Subject': "Fire Status Analysis - Automated Response",
                    'TextPart': text_body,
                    'HTMLPart': html_body,
                    'CustomID': f"fire_status_{datetime.now().timestamp()}"
                }
            ]
        }
        
        # Send the email using Mailjet API
        result = mailjet.send.create(data=data)
        
        # Check if the email was sent successfully
        if result.status_code == 200:
            print(f"Status analysis email sent to {to_email}")
            return True
        else:
            print(f"Failed to send status email: {result.status_code}, {result.json()}")
            return False
            
    except Exception as e:
        print(f"Error sending status response email: {e}")
        return False

@app.post("/email-webhook")
async def email_webhook(request: Request):
    """Handle incoming email webhook requests from Mailjet."""
    try:
        # Get the raw request body
        body = await request.body()
        
        # Print the raw payload for debugging
        print("=== INCOMING EMAIL WEBHOOK PAYLOAD ===")
        print(f"Raw payload: {body.decode()}")
        
        # Try to parse as JSON
        try:
            data = await request.json()
            print(f"JSON payload: {data}")
        except:
            print("Payload is not valid JSON")
        
        return {"status": "received", "message": "Email webhook received and printed"}
            
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
            
        except Exception as e:
            print(f"Error uploading to Supabase: {e}")
            response_data["supabase_error"] = str(e)
    
    return response_data

@app.on_event("startup")
async def startup_event():
    """Configure Mailjet Parse Route with current ngrok URL on startup."""
    try:
        # Get the current ngrok URL
        tunnels = ngrok.get_tunnels()
        if tunnels:
            ngrok_url = tunnels[0].public_url
            webhook_url = f"{ngrok_url}/email-webhook"
            print(f"Setting up Mailjet Parse Route to: {webhook_url}")
            
            # Use v3 API version for Parse Route (not v3.1)
            mailjet_v3 = Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3')
            
            # First, check if a Parse Route exists
            try:
                get_result = mailjet_v3.parseroute.get()
                current_routes = get_result.json()
                print(f"Current Parse Routes: {current_routes}")
                
                # If routes exist, delete them
                if 'Data' in current_routes and current_routes['Data']:
                    for route in current_routes['Data']:
                        try:
                            # Extract the ID from the route data and use it for deletion
                            route_id = route['ID']
                            delete_result = mailjet_v3.parseroute.delete(id=route_id)
                            print(f"Deleted existing Parse Route ID {route_id}: {delete_result.status_code}")
                        except Exception as delete_error:
                            print(f"Error deleting Parse Route: {delete_error}")
            except Exception as get_error:
                print(f"Error checking existing Parse Routes: {get_error}")
            
            # Now create the new Parse Route
            data = {
                'Url': webhook_url
            }
            
            try:
                result = mailjet_v3.parseroute.create(data=data)
                print(f"Status code: {result.status_code}")
                print(f"Response: {result.json()}")
                
                if result.status_code in (200, 201):
                    print(f"✅ Mailjet Parse Route successfully configured")
                else:
                    print(f"❌ Failed to configure Mailjet Parse Route: {result.status_code}")
            except Exception as api_error:
                print(f"API Error: {api_error}")
                
        else:
            print("❌ No ngrok tunnels found")
    except Exception as e:
        print(f"❌ Error configuring Mailjet Parse Route: {e}")