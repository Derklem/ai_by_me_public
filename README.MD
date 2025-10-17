@"
# 🛡️ Halcyon v3.1 - Privacy Resistance Hub
- Rule-based privacy tools
- GPT-2 fallback for general queries
- PIN security (1234)
- Waitress production server

## Quick Start
```bash
pip install -r requirements.txt
export HALCYON_PIN=1234
python web_api.py ## Quick Start

**Requirements:** Python 3.11+, Windows/macOS/Linux

```powershell
# create & activate venv (Windows)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# deps
pip install -r requirements.txt

# secure write endpoints
$env:HALCYON_PIN = "1234"

# run (Waitress production server)
python web_api.py
# UI (desktop): http://localhost:8000/ui
# UI (phone on LAN): http://<your-LAN-IP>:8000/ui
