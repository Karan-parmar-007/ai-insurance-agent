# agent/tts_elevenlabs.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "Rachel")  # default voice

def generate_speech(text: str) -> bytes:
    """Converts text to speech using ElevenLabs and returns raw audio bytes."""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.7,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=payload, stream=True)

    if response.status_code == 200:
        return response.content  # audio bytes (MP3)
    else:
        print(f"[ElevenLabs] Error: {response.status_code} - {response.text}")
        return b""
