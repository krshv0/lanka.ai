import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from elevenlabs.client import ElevenLabs  # Official ElevenLabs SDK

# Load environment variables from .env in project root
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")  # Default public voice

print("Loaded ElevenLabs API Key:", ELEVENLABS_API_KEY != "")
print("Loaded HuggingFace API Key:", HF_TOKEN != "")
print("Using ElevenLabs Voice ID:", ELEVENLABS_VOICE_ID)

AUDIO_DIR = "backend/audio"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Initialize ElevenLabs client
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)


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
    Convert AI text into natural speech using the official ElevenLabs SDK.
    """
    if not ELEVENLABS_API_KEY:
        return "Error: Missing ElevenLabs API Key."

    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_path = os.path.join(AUDIO_DIR, f"response_{timestamp}.mp3")

        # Generate streaming audio using ElevenLabs SDK
        audio_stream = elevenlabs.text_to_speech.convert(
            text=text,
            voice_id=ELEVENLABS_VOICE_ID,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128"
        )

        # Write the stream chunks to file
        with open(audio_path, "wb") as f:
            for chunk in audio_stream:
                if isinstance(chunk, bytes):
                    f.write(chunk)

        return f"/audio/{os.path.basename(audio_path)}"

    except Exception as e:
        return f"Error generating audio with ElevenLabs SDK: {str(e)}"