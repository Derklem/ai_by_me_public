# ---- Base ----
FROM python:3.11-slim

# Keep Python quiet & unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=web_api:app \
    TRANSFORMERS_VERBOSITY=error \
    HF_HUB_ENABLE_HF_TRANSFER=1

WORKDIR /app

# System deps (git sometimes needed by HF hubs); keep image slim
RUN apt-get update && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/requirements.txt

# Install CPU-only torch from the official PyTorch CPU index, then the rest
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu "torch==2.4.*" \
 && pip install --no-cache-dir -r /app/requirements.txt

# Bring in the app
COPY . /app

# Expose API port
EXPOSE 8000

# Run the Flask app binding to all interfaces (container)
CMD ["python","-m","flask","run","--host=0.0.0.0","--port=8000"]
