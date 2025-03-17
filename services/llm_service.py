import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL

class LLMService:
    """Service for interacting with Google's Gemini LLM."""
    
    def __init__(self):
        # Configure the Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel(GEMINI_MODEL)
    
    def generate_response(self, prompt, safety_settings=None):
        """
        Generate a response from the LLM.
        
        Args:
            prompt (str): User prompt
            safety_settings (dict, optional): Custom safety settings
            
        Returns:
            tuple: (success, response_text or error_message)
        """
        try:
            # Apply default safety settings if none provided
            if safety_settings is None:
                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                    }
                ]
            
            # Generate content
            response = self.model.generate_content(
                prompt,
                safety_settings=safety_settings
            )
            
            # Extract and return the text response
            if response.text:
                return True, response.text
            else:
                return False, "The AI generated an empty response"
                
        except Exception as e:
            return False, f"Error generating LLM response: {str(e)}"
    
    def is_available(self):
        """
        Check if the LLM service is available.
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            # Simple test generation
            response = self.model.generate_content("Hello")
            return True
        except Exception:
            return False