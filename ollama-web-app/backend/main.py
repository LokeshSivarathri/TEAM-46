from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import time
from google import genai
from google.genai import types
from google.genai.errors import APIError

# --- Configuration ---
# ACTION REQUIRED: Replace 'YOUR_API_KEY' with your actual key or set the GEMINI_API_KEY environment variable.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyC2qea4Cj_qGR1mnWGqsAhg2D4Ax_O4tt8") 
MODEL_NAME = "gemini-2.5-flash"
MAX_RETRIES = 5

# --- FastAPI Setup ---
app = FastAPI(title="Voice-to-Voice Gemini Assistant API")

# Configure CORS to allow the HTML frontend to access the API.
# The '*' allows access from any origin (required when running HTML locally).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Data Model ---
class ChatPrompt(BaseModel):
    """Data model for the incoming JSON payload from the frontend."""
    prompt: str

# --- Gemini API Client Initialization ---
client = None
try:
    # Initialize the client. The SDK will automatically use the environment variable GEMINI_API_KEY.
    client = genai.Client()
except Exception as e:
    print(f"Error initializing Gemini client: {e}")

# --- API Endpoint ---

@app.post("/chat")
async def chat_with_gemini(data: ChatPrompt):
    """
    Endpoint to receive transcribed user text and return an AI response.
    Implements Step 4: Gemini AI thinks.
    """
    if not client:
        return {"response": "Backend server error: Gemini client failed to initialize. Check API key."}
        
    user_query = data.prompt
    
    for attempt in range(MAX_RETRIES):
        try:
            # 4. Gemini AI thinks
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[user_query],
                config=types.GenerateContentConfig(
                    # Instruct the model to use a sweet, helpful persona
                    system_instruction="You are a friendly, helpful, and sweet voice assistant. Keep your responses concise and conversational, as they will be spoken aloud."
                )
            )
            
            ai_response = response.text.strip()
            return {"response": ai_response}

        except APIError as e:
            print(f"Gemini API Error (Attempt {attempt + 1}): {e}")
            if attempt < MAX_RETRIES - 1:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                return {"response": "I'm sorry, I cannot connect to the service right now. Please try again."}
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            return {"response": "An unexpected server error occurred."}

# --- Health Check Endpoint ---
@app.get("/")
def read_root():
    return {"status": "FastAPI is running", "model": MODEL_NAME}
