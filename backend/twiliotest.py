import base64
import google.generativeai as genai
from twilio.rest import Client
from config import GEMINI_API_KEY
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def call_help_operator():
    """
    Function to call for help when a severe fire is detected.
    Makes an outgoing call to the emergency contact number.
    """
    EMERGENCY_PHONE_NUMBER = "5107366089"  # The specific phone number to call
    
    try:
        # Create a TwiML response for the outgoing call
        twiml = """
        <Response>
            <Say>Alert from your fire detection system. A potential fire has been detected. 
            Please check your email for the fire analysis report and images.
            This is an automated emergency notification.</Say>
            <Pause length="1"/>
            <Say>If you need immediate assistance, please call emergency services after this call.</Say>
        </Response>
        """
        
        # Make the outgoing call using Twilio
        call = twilio_client.calls.create(
            twiml=twiml,
            to=f"+1{EMERGENCY_PHONE_NUMBER}",  # Add +1 for US numbers
            from_=TWILIO_PHONE_NUMBER
        )
        
        print(f"HELP NEEDED - Call initiated to {EMERGENCY_PHONE_NUMBER} - SID: {call.sid}")
        return {
            "status": "Help requested", 
            "message": f"Emergency call placed to +1{EMERGENCY_PHONE_NUMBER}",
            "call_sid": call.sid
        }
    except Exception as e:
        print(f"Error making emergency call: {e}")
        return {
            "status": "Error", 
            "message": f"Failed to place emergency call: {str(e)}"
        }
    
call_help_operator()