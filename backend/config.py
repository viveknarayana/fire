import os
from dotenv import load_dotenv
from pyngrok import ngrok

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env.local'))

# Cerebras configuration
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

# convo history
conversation_history = {}

#ngrok configuration
public_url = ngrok.connect(8000)
print("Public URL:", public_url.public_url)

# Make the URL available to other modules
WEBHOOK_BASE_URL = public_url.public_url

# Supabase configuration
SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

#Twilio configuration
TWILIO_ACCOUNT_SID=os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN=os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER=os.getenv("TWILIO_PHONE_NUMBER")

# Mailjet configuration
MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
MAILJET_SECRET_KEY = os.getenv("MAILJET_SECRET_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "Fire Detection System")

# Email IMAP settings
EMAIL_IMAP_SERVER = os.getenv("EMAIL_IMAP_SERVER", "imap.gmail.com")
EMAIL_IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))
EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", EMAIL_FROM)
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Storage settings
UPLOAD_DIR = "uploaded_frames"
os.makedirs(UPLOAD_DIR, exist_ok=True)