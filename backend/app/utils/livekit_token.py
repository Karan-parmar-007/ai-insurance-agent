import os
from dotenv import load_dotenv
from livekit import api

load_dotenv()

LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

def create_token(identity: str, room: str) -> str:
    """Generate a JWT token for LiveKit access."""
    token = api.AccessToken(api_key=LIVEKIT_API_KEY, api_secret=LIVEKIT_API_SECRET) \
        .with_identity(identity) \
        .with_name(identity) \
        .with_grants(api.VideoGrants(room_join=True, room=room))
    
    return token.to_jwt()
