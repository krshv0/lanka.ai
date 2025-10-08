# backend/app.py

from flask import Flask, request, jsonify
from utils import generate_ai_response, text_to_speech
import os

app = Flask(__name__)

@app.route('/')
def home():
    return {"message": "AI Voice Backend Active ✅"}

@app.route('/alexa', methods=['POST'])
def alexa_webhook():
    try:
        data = request.get_json()
        user_text = data.get("text", "")

        if not user_text:
            return jsonify({"error": "No input text received"}), 400

        print(f"🗣️ User said: {user_text}")

        # Generate AI response
        ai_text = generate_ai_response(user_text)
        print(f"🤖 AI response: {ai_text}")

        # Convert AI text to audio
        audio_url = text_to_speech(ai_text)

        return jsonify({
            "responseText": ai_text,
            "audioUrl": audio_url
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)