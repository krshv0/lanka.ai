# backend/utils.py

import os
import requests
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

AUDIO_DIR = "backend/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

def generate_ai_response(prompt: str) -> str:
    """
    Generate an AI response using HuggingFace Inference API.
    """
    API_URL = "https://api-inference.huggingface.co/models/gpt2"  # Change to preferred model
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    payload = {"inputs": prompt}

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        return "Sorry, I couldn't process your request."

    result = response.json()
    if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
        return result[0]["generated_text"]
    elif isinstance(result, dict) and "generated_text" in result:
        return result["generated_text"]
    else:
        return str(result)


def text_to_speech(text: str) -> str:
    """
    Convert AI text into natural speech using ElevenLabs TTS API.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice": "alloy"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        with open(audio_path, "wb") as f:
            f.write(response.content)
        return f"/audio/{os.path.basename(audio_path)}"
    else:
        return ""