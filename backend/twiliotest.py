import os
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_sms_alert(phone_number, frame_number, timestamp, image_url=None):
    try:
        message_body = (
            "🔥 URGENT: Fire Detection Alert! 🔥\n\n"
            f"Our system detected a potential fire:\n"
            f"- Frame: {frame_number}\n"
            f"- Time: {timestamp:.2f}s\n"
            f"- Detected: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\
