from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import os
import json
import logging
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize GPT-2 with proper padding
print("🔄 Loading GPT-2 model and tokenizer...")
try:
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    
    # Fix GPT-2 padding warnings
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id
    
    print("✅ GPT-2 loaded successfully")
except Exception as e:
    print(f"❌ Failed to load GPT-2: {e}")
    raise

MEMORY_FILE = "halcyon_memory.json"
MAX_MEMORY_SIZE = 1000

def load_memory():
    """Load conversation history from JSON."""
    try:
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory = json.load(f)
                if isinstance(memory, list) and len(memory) > MAX_MEMORY_SIZE:
                    memory = memory[-MAX_MEMORY_SIZE:]
                return memory
        return []
    except Exception as e:
        logger.error(f"Failed to load memory: {e}")
        return []

def save_memory(user_input, ai_response):
    """Save conversation to memory file."""
    try:
        memory = load_memory()
        timestamp = datetime.now().isoformat()
        entry = {
            "timestamp": timestamp,
            "user": user_input.strip(),
            "ai": ai_response.strip()
        }
        memory.append(entry)
        
        if len(memory) > MAX_MEMORY_SIZE:
            memory = memory[-MAX_MEMORY_SIZE:]
        
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        logger.debug(f"Saved memory entry: {entry['user'][:30]}...")
    except Exception as e:
        logger.error(f"Failed to save memory: {e}")

def generate_response(prompt, max_new_tokens=100, temperature=0.8, top_p=0.9):
    """Generate AI response using GPT-2."""
    try:
        input_text = f"Human: {prompt}\nAI:"
        inputs = tokenizer.encode(input_text, return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                attention_mask=inputs.ne(tokenizer.pad_token_id),
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                repetition_penalty=1.1,
                no_repeat_ngram_size=2,
                early_stopping=True
            )
        
        response = tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
        response = response.replace("Human:", "").replace("AI:", "").strip()
        
        if len(response) < 10:
            response = "That's interesting! Can you tell me more?"
        
        return response[:500]
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return "I'm having trouble generating a response right now. Please try again."

@app.route("/", methods=["GET"])
def status():
    """Health check endpoint."""
    return jsonify({
        "status": "🟢 Halcyon Web API v1.0.0 is online",
        "model": "GPT-2",
        "memory_entries": len(load_memory()),
        "timestamp": datetime.now().isoformat()
    })

@app.route("/interact", methods=["POST"])
def interact():
    """Main interaction endpoint with robust JSON handling."""
    try:
        # Check content type first
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        # Try multiple JSON parsing methods
        data = None
        try:
            data = request.get_json(force=True, silent=True, cache=False)
        except Exception as json_error:
            logger.warning(f"JSON parsing failed: {json_error}")
        
        if not data:
            # Fallback: try parsing raw data
            try:
                raw_data = request.get_data(as_text=True)
                if raw_data:
                    data = json.loads(raw_data)
            except json.JSONDecodeError:
                pass
        
        if not data:
            return jsonify({"error": "Invalid or missing JSON data"}), 400
        
        user_input = data.get("input", "").strip()
        if not user_input:
            return jsonify({"error": "Missing 'input' field or empty input"}), 400
        
        if len(user_input) > 1000:
            return jsonify({"error": "Input too long (max 1000 chars)"}), 400
        
        logger.info(f"📨 Received: {user_input[:50]}...")
        
        ai_response = generate_response(user_input)
        save_memory(user_input, ai_response)
        
        logger.info(f"🤖 Response: {ai_response[:50]}...")
        
        return jsonify({
            "response": ai_response,
            "timestamp": datetime.now().isoformat(),
            "input_length": len(user_input),
            "response_length": len(ai_response)
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Interact error: {traceback.format_exc()}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)[:200]
        }), 500

@app.route("/memory", methods=["GET"])
def get_memory():
    """Retrieve conversation history."""
    try:
        memory = load_memory()
        return jsonify({
            "total": len(memory),
            "entries": memory[-10:] if memory else []
        })
    except Exception as e:
        logger.error(f"Memory retrieval error: {e}")
        return jsonify({"error": "Failed to retrieve memory"}), 500

@app.route("/memory/clear", methods=["POST"])
def clear_memory():
    """Clear conversation history."""
    try:
        if os.path.exists(MEMORY_FILE):
            os.remove(MEMORY_FILE)
            logger.info("Memory cleared")
        return jsonify({"status": "Memory cleared successfully"}), 200
    except Exception as e:
        logger.error(f"Clear memory error: {e}")
        return jsonify({"error": "Failed to clear memory"}), 500

@app.route("/health", methods=["GET"])
def health():
    """Detailed health check."""
    try:
        memory_exists = os.path.exists(MEMORY_FILE)
        return jsonify({
            "status": "healthy",
            "model_loaded": True,
            "memory_file": memory_exists,
            "memory_entries": len(load_memory()) if memory_exists else 0,
            "timestamp": datetime.now().isoformat()
        })
    except:
        return jsonify({"status": "unhealthy"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Halcyon Web API v1.0.0")
    print(f"🌐 Host: {host}:{port}")
    print(f"💾 Memory: {MEMORY_FILE}")
    print(f"🧠 Model: GPT-2 (loaded)")
    print("📡 Endpoints: /, /health, /interact, /memory, /memory/clear")
    print("🔄 Press Ctrl+C to stop")
    
    app.run(host=host, port=port, debug=False)