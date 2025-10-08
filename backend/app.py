from flask import Flask, request, jsonify
from utils import generate_ai_response, text_to_speech

app = Flask(__name__)


@app.route('/')
def home():
    return {"message": "AI Voice Backend Active ✅"}


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        data = request.get_json()
        text = data.get("text")
        user_id = data.get("user_id", "default_user")

        if not text:
            return jsonify({"error": "No text provided"}), 400

        # Step 1 — Generate AI response
        ai_response = generate_ai_response(text)

        # Step 2 — Convert AI response to speech
        audio_path = text_to_speech(ai_response)

        return jsonify({
            "response_text": ai_response,
            "audio_url": audio_path
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)