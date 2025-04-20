import base64
import google.generativeai as genai
from config import GEMINI_API_KEY

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)

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