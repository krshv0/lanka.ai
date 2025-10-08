import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

# Load environment variables from .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")

print("Loaded ElevenLabs API Key:", ELEVENLABS_API_KEY != "")
print("Loaded HuggingFace API Key:", HF_TOKEN != "")
print("Using ElevenLabs Voice ID:", ELEVENLABS_VOICE_ID)

AUDIO_DIR = "backend/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)


def generate_ai_response(prompt: str) -> str:
    """
    Generate an AI response using HuggingFace DeepSeek conversational model.
    """
    if not HF_TOKEN:
        return "Error: Missing HuggingFace API Key."

    API_URL = "https://router.huggingface.co/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-ai/DeepSeek-V3.2-Exp:novita",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except requests.RequestException as e:
        return f"Error contacting HuggingFace API: {str(e)}"
    except (KeyError, IndexError):
        return "Error: Unexpected response format from HuggingFace API."

def text_to_speech(text: str) -> str:
    """
    Convert AI text into natural speech using ElevenLabs TTS API.
    """
    if not ELEVENLABS_API_KEY:
        return "Error: Missing ElevenLabs API Key."

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}/stream"
    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
        "Accept": "audio/mpeg"
    }
    payload = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True)
        response.raise_for_status()

        with open(audio_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return f"/audio/{os.path.basename(audio_path)}"

    except requests.RequestException as e:
        return f"Error contacting ElevenLabs API: {str(e)}"