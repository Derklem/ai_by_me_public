import openai
import torch
import numpy as np
import faiss
import pyttsx3
import sounddevice as sd
import queue
import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Set OpenAI API Key (use environment variable for security)
openai.api_key = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")  # Replace with your key

# Memory system (conversation history)
memory = []

# Text-to-Speech (AI replies in voice)
engine = pyttsx3.init()

# Speech-to-Text setup
q = queue.Queue()

def audio_callback(indata, frames, time, status):
    """Records audio input for STT"""
    if status:
        print(status)
    q.put(bytes(indata))

@app.route("/chat", methods=["POST"])
def chat():
    """Handles AI conversations with memory and voice output"""
    data = request.get_json()
    message = data.get("message", "")

    if not message:
        return jsonify({"response": "Please say something."}), 400

    # Store conversation history
    memory.append({"role": "user", "content": message})

    try:
        # Generate AI response
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",  # Update to "gpt-4" if available
            messages=memory
        )
        
        ai_reply = response.choices[0].message.content.strip()
        memory.append({"role": "assistant", "content": ai_reply})

        # Speak the response (Text-to-Speech)
        engine.say(ai_reply)
        engine.runAndWait()

        return jsonify({"response": ai_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
