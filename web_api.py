from flask import Flask, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import os
import json

app = Flask(__name__)

# Initialize GPT-2
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2")

MEMORY_FILE = "halcyon_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_memory(user_input, ai_response):
    memory = load_memory()
    memory.append({"user": user_input, "ai": ai_response})
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4)

def generate_response(prompt):
    input_text = f"Human: {prompt}\nAI:"
    input_ids = tokenizer.encode(input_text, return_tensors="pt")
    output = model.generate(input_ids, max_length=100, temperature=0.75)
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response.replace("Human:", "").replace("AI:", "").strip()

@app.route("/")
def status():
    return jsonify({"status": "🟢 Halcyon Web API is online."})

@app.route("/interact", methods=["POST"])
def interact():
    data = request.json
    user_input = data.get("input", "")
    ai_response = generate_response(user_input)
    save_memory(user_input, ai_response)
    return jsonify({"response": ai_response})
