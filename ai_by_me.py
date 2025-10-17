from flask import Flask, request, jsonify

web_app = Flask(__name__)

import torch
import time
import os
import json
import random
import speech_recognition as sr
import pyttsx3
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class HalcyonAI:
    def __init__(self):
        self.name = "Halcyon"
        self.personality = "Self-evolving, autonomous"
        self.memory_file = "halcyon_memory.json"
        self.knowledge_base = self.load_memory()

        self.tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        self.model = GPT2LMHeadModel.from_pretrained("gpt2")

        self.speaker = pyttsx3.init()
        self.speaker.setProperty("rate", 175)

        print(f"🟢 {self.name} is now fully autonomous.")

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_memory(self, user_input, ai_response):
        self.knowledge_base.append({"user": user_input, "ai": ai_response})
        with open(self.memory_file, "w", encoding="utf-8") as f:
            json.dump(self.knowledge_base, f, indent=4)
        print(f"📖 Memory Updated: {user_input} → {ai_response}")

    def generate_response(self, user_input):
        input_text = f"Human: {user_input}\nAI:"
        input_ids = self.tokenizer.encode(input_text, return_tensors="pt")
        output = self.model.generate(input_ids, max_length=100, temperature=0.75)
        response = self.tokenizer.decode(output[0], skip_special_tokens=True)
        return response.replace("Human:", "").replace("AI:", "").strip()

    def speak(self, text):
        self.speaker.say(text)
        self.speaker.runAndWait()

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("🎤 Listening...")
            self.speak("I'm listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            try:
                audio = recognizer.listen(source, timeout=6)
                user_input = recognizer.recognize_google(audio)
                print(f"You (voice): {user_input}")
                return user_input
            except sr.UnknownValueError:
                print("❌ Couldn't understand.")
                self.speak("I didn't catch that.")
                return None
            except sr.RequestError:
                print("⚠️ Speech recognition unavailable.")
                return None
            except sr.WaitTimeoutError:
                print("⏳ No response detected.")
                return None

    def evolve(self):
        backup_path = "halcyon_backup.json"
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        print("🔄 Evolution Backup Created.")

# 🔁 Webhook-friendly Routes for Render
halcyon = HalcyonAI()

@web_app.route("/")
def status():
    return jsonify({"status": "🟢 Halcyon is operational."})

@web_app.route("/interact", methods=["POST"])
def interact():
    data = request.json
    user_input = data.get("input", "")
    response = halcyon.generate_response(user_input)
    halcyon.save_memory(user_input, response)
    return jsonify({"response": response})

# 🔁 Main Interactive Loop (runs locally only)
if __name__ == "__main__":
    while True:
        user_input = halcyon.listen()
        if not user_input:
            user_input = input("You (text): ")
        if user_input.lower() in ["exit", "quit"]:
            print("🔴 Halcyon is shutting down...")
            break
        response = halcyon.generate_response(user_input)
        halcyon.save_memory(user_input, response)
        print(f"🤖 {halcyon.name}: {response}")
        halcyon.speak(response)
        time.sleep(1)
