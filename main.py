from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
import io
import base64
import openai
from gtts import gTTS

# ------------------------
# Initialize FastAPI app
# ------------------------
app = FastAPI()

# ------------------------
# Enable CORS
# ------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# OpenAI API Key (SAFE)
# ------------------------
openai.api_key = os.getenv()

# ------------------------
# In-memory conversation storage
# ------------------------
conversations: Dict[str, List[Dict[str, str]]] = {}

# ------------------------
# Request model
# ------------------------
class ChatRequest(BaseModel):
    text: str
    session_id: Optional[str] = None

# ------------------------
# Frontend
# ------------------------
@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Mental Health Voice Chatbot</title>
</head>
<body>
  <h1>🧠 Mental Health Voice Chatbot</h1>

  <input id="userText" placeholder="Your speech will appear here" readonly />
  <button onclick="startRecognition()">🎤 Speak</button>

  <p><strong>Bot response:</strong></p>
  <div id="botText"></div>

  <p style="color: gray; font-size: 14px;">
    Disclaimer: This chatbot is not a substitute for professional mental health care.
  </p>

<script>
let sessionId = localStorage.getItem("session_id");
if (!sessionId) {
  sessionId = Math.random().toString(36).substring(2);
  localStorage.setItem("session_id", sessionId);
}

function startRecognition() {
  const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
  recognition.lang = "en-US";

  recognition.onresult = async function(event) {
    const text = event.results[0][0].transcript;
    document.getElementById("userText").value = text;

    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: text, session_id: sessionId })
    });

    const data = await res.json();
    document.getElementById("botText").innerText = data.text;

    const audio = new Audio("data:audio/mp3;base64," + data.audio);
    audio.play();
  };

  recognition.start();
}
</script>
</body>
</html>
"""
