import base64
import google.generativeai as genai
from twilio.rest import Client
from config import GEMINI_API_KEY
from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER
from config import WEBHOOK_BASE_URL
from config import conversation_history
from config import CEREBRAS_API_KEY

from twilio.twiml.voice_response import VoiceResponse, Gather
from fastapi.responses import PlainTextResponse
from fastapi import Form, Request

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# System prompt for the AI assistant
SYSTEM_PROMPT = """
You are an emergency fire detection AI assistant. 
You've detected a potential fire and are calling to provide assistance.
Speak clearly and calmly. Ask if they can dispatch emergency services.
Provide details about the detected fire based on the analysis.
Listen to their questions and instructions, and respond appropriately.
Your goal is to provide the required information and obtain help from the fire department.
"""

def call_help_operator(fire_analysis):
    """
    Function to call for help when a severe fire is detected.
    Makes an outgoing call to the emergency contact number, configured for interactive conversation.
    
    Args:
        fire_analysis: The fire analysis text to include in the conversation
    """
    EMERGENCY_PHONE_NUMBER = "5107366089"  # The specific phone number to call
    
    try:
        # Create a call that will connect to our webhook for conversation
        # The webhook URL must be publicly accessible for Twilio to reach it
        call = twilio_client.calls.create(
            url=f"{WEBHOOK_BASE_URL}/fire-conversation",  
            to=f"+1{EMERGENCY_PHONE_NUMBER}",  
            from_=TWILIO_PHONE_NUMBER
        )
        
        # Format a brief introduction based on the fire analysis
        initial_message = "Hello, this is Firewatch. We have detected a potential fire and are calling to provide information and request assistance."
        
        # Initialize the conversation history for this call
        conversation_history[call.sid] = {
            "messages": [
                {"role": "system", "content": f"{SYSTEM_PROMPT}\n\nFire Analysis: {fire_analysis}"},
                {"role": "assistant", "content": initial_message}
            ],
            "fire_analysis": fire_analysis  # Store the analysis for reference during conversation
        }
        
        print(f"HELP NEEDED - Interactive call initiated to {EMERGENCY_PHONE_NUMBER} - SID: {call.sid}")
        return {
            "status": "Help requested", 
            "message": f"Emergency interactive call placed to +1{EMERGENCY_PHONE_NUMBER}",
            "call_sid": call.sid
        }
    except Exception as e:
        print(f"Error making emergency call: {e}")
        return {
            "status": "Error", 
            "message": f"Failed to place emergency call: {str(e)}"
        }

from cerebras.cloud.sdk import Cerebras

async def generate_conversation_response(call_sid, user_input):
    """
    Generate a response to the user using Cerebras SDK based on conversation history
    """
    try:
        # Add user's input to conversation history
        conversation_history[call_sid]["messages"].append({"role": "user", "content": user_input})
        
        # Get fire analysis from conversation history if available
        fire_analysis = conversation_history[call_sid].get("fire_analysis", "")
        
        # Prepare messages for Cerebras API
        messages = conversation_history[call_sid]["messages"].copy()
        
        
        # Initialize Cerebras client
        client = Cerebras(
            api_key=CEREBRAS_API_KEY,
        )
        
        # Call Cerebras API for response generation
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-4-scout-17b-16e-instruct",
            max_tokens=100  # Keep responses concise for voice conversation
        )
        
        # Extract response text
        response_text = chat_completion.choices[0].message.content
        
        # Add assistant's response to conversation history
        conversation_history[call_sid]["messages"].append({"role": "assistant", "content": response_text})
        
        return response_text
        
    except Exception as e:
        print(f"Error generating response: {e}")
        return "I'm sorry, I'm having trouble processing that. Is everyone safe? If you're in immediate danger, please hang up and call emergency services directly."


async def analyze_fire_image_with_gemini(image_data):
    """Use Gemini to analyze a fire image and provide insights with function calling capability."""
    try:
        # Convert image data to base64 for Gemini
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Define the function declaration for the model
        help_operator_function = {
            "name": "call_help_operator",
            "description": "Calls for emergency help when a severe fire is detected.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        }
        
        # Initialize Gemini model for multimodal inputs with tool configuration
        model = genai.GenerativeModel(
            'gemini-1.5-pro',
            tools=[{"function_declarations": [help_operator_function]}]
        )
        
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
        
        If you determine the fire to be any risk at all, please call for emergency assistance using call_help_operator. If the fire is EXTREMELY small, please just provide the analysis. 
        The email notification will suffice in this case.
        
        Format your response in an easy-to-read manner suitable for someone checking on a fire alert.
        """
        
        # Create the multimodal inputs
        image_part = {
            "mime_type": "image/jpeg", 
            "data": image_base64
        }
        
        contents = [prompt, image_part]
        
        # Generate the response from Gemini with function calling capability
        response = model.generate_content(contents)
        
        # First extract the full text analysis
        full_analysis = ""
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text'):
                full_analysis += part.text
        
        if not full_analysis and hasattr(response, 'text'):
            full_analysis = response.text
            
        # Process the response to find function calls
        function_called = False
        result_text = full_analysis
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                print(f"Function to call: {function_call.name}")
                
                # Call the appropriate function with the full analysis text
                if function_call.name == "call_help_operator":
                    function_called = True
                    result = call_help_operator(full_analysis)
                    result_text += f"\n\nEMERGENCY ASSISTANCE REQUESTED: {result['message']}"
        
        # If no function was called but we have an analysis, call help anyway
        if not function_called and full_analysis:
            result = call_help_operator(full_analysis)
            result_text += f"\n\nEMERGENCY ASSISTANCE REQUESTED: {result['message']}"
            
        return result_text
        
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return "Unable to analyze the fire image at this moment. Please check the visual directly or contact emergency services if the situation appears dangerous."