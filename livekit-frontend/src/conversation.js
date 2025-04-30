import { recordAudio, playAudio } from "./audio.js";

const BACKEND_API = "http://localhost:5000";
const conversationDiv = document.getElementById("conversation");
const textInput = document.getElementById("textInput");
const sendTextBtn = document.getElementById("sendTextBtn");
const recordBtn = document.getElementById("recordBtn");
const audioPlayback = document.getElementById("audioPlayback");
const backBtn = document.getElementById("backBtn");

function appendMessage(sender, text) {
  const msg = document.createElement("div");
  msg.textContent = `${sender}: ${text}`;
  conversationDiv.appendChild(msg);
}

// Generate or load session_id
function getSessionId() {
  let sessionId = localStorage.getItem('session_id');
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('session_id', sessionId);
  }
  return sessionId;
}

function playBase64Audio(b64, audioElement) {
  if (!b64) {
    alert("No audio data received from backend (TTS failed or not configured).");
    return;
  }
  const byteCharacters = atob(b64);
  const byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  const byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'audio/mp3' });
  playAudio(blob, audioElement);
}

sendTextBtn.onclick = async () => {
  const text = textInput.value.trim();
  if (!text) return;
  appendMessage("You", text);
  textInput.value = "";
  const sessionId = getSessionId();
  const res = await fetch(`${BACKEND_API}/api/agent/text`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, session_id: sessionId })
  });
  const data = await res.json();
  appendMessage("Bot", data.response);
  if (data.session_id) {
    localStorage.setItem('session_id', data.session_id);
  }
  if (data.tts_b64) {
    playBase64Audio(data.tts_b64, audioPlayback);
  } else {
    console.warn("No tts_b64 in response", data);
    alert("No audio response from backend. Check TTS configuration.");
  }
};

recordBtn.onclick = async () => {
  recordBtn.disabled = true;
  appendMessage("System", "Recording...");
  try {
    const audioBlob = await recordAudio();
    appendMessage("System", "Processing audio...");
    const formData = new FormData();
    formData.append("audio", audioBlob, "audio.webm");
    const sessionId = getSessionId();
    formData.append("session_id", sessionId);
    const res = await fetch(`${BACKEND_API}/api/agent/audio`, {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    appendMessage("You (voice)", data.transcript || "[voice message]");
    appendMessage("Bot", data.response);
    if (data.session_id) {
      localStorage.setItem('session_id', data.session_id);
    }
    if (data.tts_b64) {
      playBase64Audio(data.tts_b64, audioPlayback);
    } else {
      console.warn("No tts_b64 in response", data);
      alert("No audio response from backend. Check TTS configuration.");
    }
  } catch (e) {
    appendMessage("System", "Audio recording failed.");
  }
  recordBtn.disabled = false;
};

backBtn.onclick = () => {
  window.location.href = "/index.html";
};
