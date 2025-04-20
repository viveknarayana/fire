import imaplib
import email
import email.header
import time
import os
import threading
from datetime import datetime
from email.utils import parseaddr
from mailjet_rest import Client
import asyncio

from config import (MAILJET_API_KEY, MAILJET_SECRET_KEY, EMAIL_FROM, 
                    EMAIL_FROM_NAME, EMAIL_IMAP_SERVER, EMAIL_IMAP_PORT, 
                    EMAIL_USERNAME, EMAIL_PASSWORD)
from services.storage_service import get_latest_fire_image
from services.ai_service import analyze_fire_image_with_gemini

# Initialize Mailjet client
mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_SECRET_KEY), version='v3.1')

# Keep track of users who have already been notified (to avoid spam)
notified_users = set()

# Dictionary to keep track of user UUIDs by email (to retrieve their images later)
user_email_to_uuid = {}

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

class EmailPoller:
    """Class to handle checking for email responses via IMAP."""
    
    def __init__(self):
        self.imap_server = EMAIL_IMAP_SERVER
        self.imap_port = EMAIL_IMAP_PORT
        self.username = EMAIL_USERNAME
        self.password = EMAIL_PASSWORD
        self.processed_ids = set()  # Track processed message IDs
        
    def connect(self):
        """Establish connection to the IMAP server."""
        try:
            # Connect to the IMAP server
            self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            
            # Login
            self.mail.login(self.username, self.password)
            print(f"Connected to {self.imap_server} as {self.username}")
            return True
        except Exception as e:
            print(f"Error connecting to email server: {e}")
            return False
            
    def disconnect(self):
        """Close the connection to the IMAP server."""
        try:
            self.mail.close()
            self.mail.logout()
            print("Disconnected from email server")
        except Exception as e:
            print(f"Error disconnecting from email server: {e}")
            
    def check_for_replies(self):
        """Check for new reply emails and process them."""
        try:
            # Select the inbox
            self.mail.select('INBOX')
            print(self.username, "TEMP MAIL USERNAME")
            
            status, data = self.mail.search(None, 'UNSEEN')
            
            # Process each unread email
            for num in data[0].split():
                status, data = self.mail.fetch(num, '(RFC822)')
                
                if status != 'OK':
                    print(f"Error fetching email {num}: {status}")
                    continue
                    
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Get email ID to avoid processing duplicates
                email_id = email_message.get('Message-ID', '')
                
                if email_id in self.processed_ids:
                    print(f"Already processed email ID: {email_id}")
                    continue
                    
                self.processed_ids.add(email_id)
                
                # Extract sender email
                sender_email = parseaddr(email_message['From'])[1]
                print(f"Sender email: {sender_email}")
                
                # Only process emails from users who have received fire alerts
                if sender_email not in user_email_to_uuid:
                    # Mark as read but don't process further
                    self.mail.store(num, '+FLAGS', '\\Seen')
                    continue
                
                # Print email details for debugging (only for relevant users)
                print("\n=== NEW EMAIL RECEIVED FROM MONITORED USER ===")
                print(f"From: {email_message['From']}")
                print(f"To: {email_message['To']}")
                print(f"Subject: {email_message['Subject']}")
                print(f"Date: {email_message['Date']}")
                print(f"Sender email: {sender_email}")
                
                # Process email body
                body = ""
                
                # Extract body content based on message type
                if email_message.is_multipart():
                    for part in email_message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        
                        # Skip attachments
                        if "attachment" in content_disposition:
                            continue
                            
                        # Get text content
                        if content_type in ["text/plain", "text/html"]:
                            try:
                                body_part = part.get_payload(decode=True).decode()
                                body += body_part
                                break  # We only need one text part
                            except Exception as e:
                                print(f"Error decoding email body: {e}")
                else:
                    # Get body for non-multipart messages
                    try:
                        body = email_message.get_payload(decode=True).decode()
                    except Exception as e:
                        print(f"Error decoding email body: {e}")
                
                # Process commands in email body
                self.process_email_command(sender_email, body)
                
                # Mark as read
                self.mail.store(num, '+FLAGS', '\\Seen')
                
        except Exception as e:
            print(f"Error checking for replies: {e}")

    async def handle_status_command(self, sender_email):
        """Handle STATUS command from a user."""
        try:
            user_uuid = user_email_to_uuid.get(sender_email)
            if not user_uuid:
                print(f"No UUID found for email {sender_email}")
                return
                
            # Get the latest fire image
            latest_image = await get_latest_fire_image(user_uuid)
            
            if not latest_image or not latest_image.get("content"):
                print(f"No images found for user {user_uuid}")
                return
                
            # Analyze the image with AI
            analysis = await analyze_fire_image_with_gemini(latest_image["content"])
            
            # Send the analysis back to the user
            send_status_response_email(
                to_email=sender_email,
                analysis_text=analysis,
                image_url=latest_image["url"]
            )
            
        except Exception as e:
            print(f"Error handling STATUS command: {e}")
            
    def process_email_command(self, sender_email, body):
        """Process commands found in email body."""
        print(f"\nProcessing email body from {sender_email}: {body[:100]}...")  # Print first 100 chars for debugging
        
        body_upper = body.upper()
        
        # Check for known commands
        if "STATUS" in body_upper:
            print(f"STATUS command received from {sender_email}")
            asyncio.run(self.handle_status_command(sender_email))
        elif "CALL" in body_upper:
            print(f"CALL command received from {sender_email}")
            # TODO: Implement call functionality
        else:
            print(f"No recognized command in email from {sender_email}")

def start_email_polling():
    """Start polling for email responses."""
    poller = EmailPoller()
    
    try:
        print("Starting email polling service...")
        
        while True:
            # Connect to email server
            if poller.connect():
                # Check for new emails
                print("POLLER CONNECTED")
                poller.check_for_replies()
                
                # Disconnect
                poller.disconnect()
            
            # Wait before checking again
            print(f"Waiting 2 seconds before checking again...")
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("Email polling service stopped by user")
    except Exception as e:
        print(f"Error in email polling service: {e}")

def start_email_polling_thread():
    """Start a separate thread to poll for email responses."""
    polling_thread = threading.Thread(target=start_email_polling)
    polling_thread.daemon = True  
    polling_thread.start()
    print("Email polling thread started")