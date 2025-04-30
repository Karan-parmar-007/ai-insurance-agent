import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

gemini_client = genai.Client(api_key=gemini_api_key)

def get_bot_response(prompt):
    try:
        response = gemini_client.models.generate_content(model="gemini-2.0-flash-001", contents=prompt)
        response_text = response.text.strip()
        # Remove markdown wrappers if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            response_text = response_text.strip()
        return response_text
    except Exception as e:
        print(f"[Gemini] Error: {e}")
        return "Sorry, I couldn't process your request right now."
