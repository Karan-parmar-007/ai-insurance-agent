import { Room } from "livekit-client";

const LIVEKIT_URL = "wss://exploring-wjsmcnlg.livekit.cloud";
const BACKEND_API = "http://localhost:5000";

document.getElementById("joinBtn").onclick = async () => {
  const identity = document.getElementById("identity").value.trim();
  if (!identity) {
    alert("Please enter your name.");
    return;
  }

  try {
    const res = await fetch(`${BACKEND_API}/api/livekit/token?identity=${identity}&room=insurance-room`);
    const data = await res.json();
    const token = data.token;

    const room = new Room();
    await room.connect(LIVEKIT_URL, token);

    console.log("Connected to room:", room.name);
    // Redirect to conversation page after joining
    window.location.href = "/conversation.html";
  } catch (err) {
    console.error("Error connecting to LiveKit:", err);
    alert("Connection failed.");
  }
};
