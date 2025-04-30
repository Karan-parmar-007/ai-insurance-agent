# agent/voice_agent.py

import aiohttp
import asyncio
import base64
import os
from dotenv import load_dotenv
from agent.tts_elevenlabs import generate_speech
from agent.llm import get_bot_response 
from agent.api_utils import get_user_by_email
import re
from livekit.agents.stt.deepgram import DeepgramSTT

class VoiceAgent:
    def __init__(self, user_identity, room_name):
        self.identity = user_identity
        self.room = room_name
        self.agent_active = True
        self.state = "greeting"
        self.stt = DeepgramSTT(api_key=os.getenv("DEEPGRAM_API_KEY"))
        self.context = []

    async def run(self, audio_generator):
        """Main loop: audio → Deepgram STT → LLM → ElevenLabs TTS with registration and policy flow."""
        self.state = "greeting"
        self.user_email = None
        self.user_name = None
        self.is_registered = False
        self.policy_link = None

        greeting = "Hello, welcome to Karan's test insurance project. You can ask about policies or say 'register' to create an account."
        audio_bytes = generate_speech(greeting)
        self.play_audio(audio_bytes)
        self.state = "waiting_for_input"

        async for transcript in self.transcribe_audio(audio_generator):
            print("🗣️ User said:", transcript)
            user_input = transcript.lower()

            if self.state == "waiting_for_input":
                if "register" in user_input or "purchase" in user_input or "buy" in user_input:
                    self.state = "registering_email"
                    prompt = "Please provide your email address to register."
                    audio_bytes = generate_speech(prompt)
                    self.play_audio(audio_bytes)
                    continue
                elif "buy" in user_input or "policy" in user_input:
                    if not self.is_registered:
                        prompt = "You need to register first. Please say 'register' to begin the registration process."
                        audio_bytes = generate_speech(prompt)
                        self.play_audio(audio_bytes)
                        continue
                    else:
                        # Provide policy link (simulate)
                        self.policy_link = f"http://localhost:5000/api/user/send_link?email={self.user_email}"
                        prompt = f"You can buy a policy using this link: {self.policy_link}"
                        audio_bytes = generate_speech(prompt)
                        self.play_audio(audio_bytes)
                        continue
                else:
                    # General insurance Q&A
                    bot_reply = get_bot_response(transcript)
                    self.context.append({"user": transcript, "bot": bot_reply})
                    audio_bytes = generate_speech(bot_reply)
                    self.play_audio(audio_bytes)
                    continue

            if self.state == "registering_email":
                # Simple email validation
                email_match = re.search(r"[\w\.-]+@[\w\.-]+", user_input)
                if email_match:
                    self.user_email = email_match.group(0)
                    user_info = get_user_by_email(self.user_email)
                    if user_info and not user_info.get("error"):
                        prompt = "An account with this email already exists. Please use another email or proceed to buy a policy."
                        self.is_registered = True
                        self.state = "waiting_for_input"
                    else:
                        prompt = "Thank you. Now, please say your full name."
                        self.state = "registering_name"
                    audio_bytes = generate_speech(prompt)
                    self.play_audio(audio_bytes)
                else:
                    prompt = "That doesn't seem like a valid email. Please try again."
                    audio_bytes = generate_speech(prompt)
                    self.play_audio(audio_bytes)
                continue

            if self.state == "registering_name":
                self.user_name = transcript.strip()
                # Call API to create user (simulate POST)
                import requests
                try:
                    res = requests.post("http://localhost:5000/api/user/create", json={"name": self.user_name, "email": self.user_email})
                    if res.status_code == 201:
                        prompt = f"Registration successful, {self.user_name}. You can now buy a policy."
                        self.is_registered = True
                    else:
                        prompt = "There was a problem creating your account. Please try again later."
                except Exception as e:
                    prompt = "There was a problem connecting to the registration service. Please try again later."
                self.state = "waiting_for_input"
                audio_bytes = generate_speech(prompt)
                self.play_audio(audio_bytes)
                continue

    async def transcribe_audio(self, audio_generator):
        """Yields transcripts using livekit-agents DeepgramSTT."""
        async for transcript in self.stt.transcribe(audio_generator):
            if transcript:
                yield transcript

    def play_audio(self, audio_bytes):
        # Save response for playback (replace with actual playback in production)
        with open("latest_response.mp3", "wb") as f:
            f.write(audio_bytes)