# Round Table 🧠

A multi-agent AI brainstorming app. Up to 5 AI agents with distinct personalities
debate your ideas in a Messenger-style chat — each one thinks, speaks, and remembers.

---

## Quick start

```
# 1. Clone and create venv
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start Ollama (downloads model automatically on first run)
python scripts/start_ollama.py

# 4. Launch the app
python src/main.py
```

Double-click **run.bat** (Windows) or **run.ps1** (PowerShell) to skip steps 3–4 for subsequent runs.

---

## AI backends

### Ollama (local — no API key needed)

| | |
|---|---|
| Server | `http://localhost:11434` |
| Model | `zephyr:7b-alpha-q4_K_M` |
| Start | `python scripts/start_ollama.py` |
| Test | `python scripts/test_ollama.py` |

`start_ollama.py` will:
1. Check if the server is already up — exit immediately if so
2. Find and launch `ollama serve` as a background process
3. Pull `zephyr:7b-alpha-q4_K_M` if it hasn't been downloaded yet
4. Wait up to 30 s for the server to respond

**Install Ollama:** https://ollama.com/download

**API format used:**
```json
POST http://localhost:11434/api/chat
{
  "model": "zephyr:7b-alpha-q4_K_M",
  "stream": true,
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user",   "content": "..."}
  ]
}
```

### Claude (subscription)

1. Get your API key from https://console.anthropic.com
2. Open Settings → Global → paste key into **Claude API key**
3. Set any agent's source to **Claude API** in Settings → Agents

---

## Settings

Open with the ⚙ icon (top right) or `Ctrl+,`.

| Section | What you can configure |
|---|---|
| Chat Appearance | Font family, font size, zoom |
| Global | Claude API key, Ollama URL & model, agent/round delays |
| Agents | Name, color, source (Ollama / Claude), persona, temperature, response length |

Changes are held in a draft — **Save** commits them, **Cancel** / closing reverts everything.
Each agent also has **Reset to default** and **Erase memory** buttons.

---

## Project structure

```
src/
  main.py              — app entry point
  ui/
    chat_window.py     — root layout, message log, agent response loop
    bubble.py          — user / agent / system message widgets
    input_bar.py       — growing text input
    settings_panel.py  — slide-in settings overlay
    title_bar.py       — drag area, action buttons
    theme.py           — all colors, sizes, spacing tokens
  agents/
    runner.py          — orchestrates one agent turn
    ollama_client.py   — async streaming client for Ollama
    claude_client.py   — async streaming client for Claude
    history.py         — converts message log to API messages
  data/
    settings_store.py  — singleton JSON persistence

scripts/
  start_ollama.py      — start Ollama server + pull model
  test_ollama.py       — smoke-test the model (non-streaming)

tests/                 — pytest suite (59 tests)
assets/icon.png        — taskbar / window icon
```

---

## Development

```bash
# Run tests
python -m pytest tests/ -q

# Run app from src/
python src/main.py
```

Python 3.11+ required. Dependencies: `flet`, `anthropic`, `httpx`, `python-dotenv`.
