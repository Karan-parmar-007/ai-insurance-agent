from flask import request, jsonify
from app.blueprints.agent import agent_bp
from app.agent.llm import get_bot_response
from app.agent.tts_elevenlabs import generate_speech
from app.agent.deepgram_stt import DeepgramSTT
import tempfile
import os
import base64
import requests
import uuid

# In-memory conversation state
conversation_states = {}

# Helper to get state for a session_id
def get_state(session_id):
    return conversation_states.setdefault(session_id, {})

def handle_policy_intent(transcript, session_id):
    text = transcript.lower()
    import re
    state = get_state(session_id)
    # Registration flow state
    if state.get('registering') == 'awaiting_email':
        email_match = re.search(r"[\w\.-]+@[\w\.-]+", text)
        if email_match:
            email = email_match.group(0)
        else:
            email = text.strip()
        res = requests.get(f"http://localhost:5000/api/user/get_user?email={email}")
        user_data = res.json() if res.status_code == 200 else None
        if user_data and not user_data.get('error'):
            state['registering'] = None
            state['user_email'] = email
            return f"An account with this email already exists. Would you like to buy a policy? Say 'buy policy' to continue."
        else:
            state['registering'] = 'awaiting_name'
            state['user_email'] = email
            return "Please provide your full name to complete registration."
    elif state.get('registering') == 'awaiting_name':
        name = text.strip()
        email = state.get('user_email')
        if not email:
            state['registering'] = 'awaiting_email'
            return "Please provide your email address first."
        res = requests.post("http://localhost:5000/api/user/create", json={"name": name, "email": email})
        if res.status_code == 201:
            state['registering'] = None
            return f"Registration successful for {name}. You can now buy a policy. Say 'buy policy' to continue."
        else:
            return f"There was a problem registering {email}. Please try again."
    if state.get('registering'):
        if state['registering'] == 'awaiting_email':
            return "Please provide your email address to register."
        elif state['registering'] == 'awaiting_name':
            return "Please provide your full name to complete registration."
    if "register" in text:
        state['registering'] = 'awaiting_email'
        return "To register, please provide your email address."
    elif "buy" in text or "policy" in text:
        return "To buy a policy, please visit your dashboard or say 'register' if you don't have an account."
    return None

@agent_bp.route('/api/agent/audio', methods=['POST'])
def agent_audio():
    session_id = request.headers.get('X-Session-ID') or request.form.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as tmp:
        audio_path = tmp.name
        audio_file.save(audio_path)
    stt = DeepgramSTT(api_key=os.getenv("DEEPGRAM_API_KEY"))
    with open(audio_path, 'rb') as f:
        audio_data = f.read()
    transcript = stt.transcribe_bytes(audio_data) if hasattr(stt, 'transcribe_bytes') else ""
    if not transcript:
        transcript = "(STT failed or returned empty)"
    # Policy agent logic
    policy_response = handle_policy_intent(transcript, session_id)
    if policy_response is not None:
        response = policy_response
    else:
        response = get_bot_response(transcript)
    audio_bytes = generate_speech(response)
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None
    return jsonify({
        'transcript': transcript,
        'response': response,
        'tts_b64': audio_b64,
        'session_id': session_id
    })

@agent_bp.route('/api/agent/text', methods=['POST'])
def agent_text():
    data = request.get_json()
    text = data.get('text', '')
    session_id = data.get('session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    # Policy agent logic
    policy_response = handle_policy_intent(text, session_id)
    if policy_response is not None:
        response = policy_response
    else:
        response = get_bot_response(text)
    audio_bytes = generate_speech(response)
    audio_b64 = base64.b64encode(audio_bytes).decode('utf-8') if audio_bytes else None
    return jsonify({
        'response': response,
        'tts_b64': audio_b64,
        'session_id': session_id
    })
