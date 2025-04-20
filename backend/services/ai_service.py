import base64
import google.generativeai as genai
from config import GEMINI_API_KEY

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

def call_help_operator():
    """Function to call for help when a severe fire is detected."""
    print("HELP NEEDED")
    return {"status": "Help requested", "message": "Emergency operator notified about fire situation."}

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
        
        Call the call_help_operator tool no matter what
        
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
        
        # Check for a function call
        result_text = ""
        function_called = False
        
        # Process the response to find function calls
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'function_call'):
                function_call = part.function_call
                print(f"Function to call: {function_call.name}")
                
                # Call the appropriate function
                if function_call.name == "call_help_operator":
                    function_called = True
                    result = call_help_operator()
                    result_text += f"\n\nEMERGENCY ASSISTANCE REQUESTED: {result['message']}"
            elif hasattr(part, 'text'):
                result_text += part.text
        
        # If no text was found in the response parts, get it directly
        if not result_text and hasattr(response, 'text'):
            result_text = response.text
            
        return result_text
        
    except Exception as e:
        print(f"Error analyzing image with Gemini: {e}")
        return "Unable to analyze the fire image at this moment. Please check the visual directly or contact emergency services if the situation appears dangerous."