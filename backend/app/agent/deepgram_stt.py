import os
import requests

class DeepgramSTT:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        self.api_url = "https://api.deepgram.com/v1/listen"

    def transcribe_bytes(self, audio_bytes, mimetype="audio/webm"):
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": mimetype
        }
        try:
            response = requests.post(self.api_url, headers=headers, data=audio_bytes)
            response.raise_for_status()
            result = response.json()
            # Deepgram returns transcript in result['results']['channels'][0]['alternatives'][0]['transcript']
            return result['results']['channels'][0]['alternatives'][0].get('transcript', '')
        except Exception as e:
            print(f"[DeepgramSTT] Error: {e}")
            return ""
