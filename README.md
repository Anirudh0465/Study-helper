# Study Helper

A local-first, AI-powered study planner. Paste your syllabus, let a local LLM extract topics, and get a weighted day-by-day study schedule — all running on your machine with zero cloud dependencies.

Built for [Hacktoberfest 2026](https://hacktoberfest.com) — "Pick one real person and build something for them."

## Features

- **AI Syllabus Import** — Paste raw syllabus text and the LLM extracts structured topics with difficulty ratings and hour estimates
- **Manual Topic Entry** — Add topics by hand with optional hour estimates (`Topic Name — 2h`)
- **Weighted Scheduling** — Automatically distributes topics across available days proportional to their estimated hours, with a revision day before the exam
- **Progress Tracking** — Check off topics as you complete them, see completion percentage per exam and overall
- **Study Guide** — Click "Guide" on any topic and the LLM generates key concepts and study tips so you know exactly what to focus on
- **Re-plan** — Fallen behind? Hit Re-plan to redistribute remaining topics across the days you have left
- **Export** — Copy your schedule as formatted plain text to share or print
- **Light / Dark Mode** — Minimalist black-and-white design with a toggle switch
- **Local Storage** — All your data persists in the browser, no account needed

## Stack

| Layer | Tech |
|-------|------|
| Frontend | Vanilla HTML/CSS/JS (single file, no build step) |
| Backend | Python, FastAPI, Uvicorn |
| AI | Ollama + Qwen3:4b (runs locally on GPU) |
| Storage | Browser localStorage (no database) |

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- A GPU with at least 4GB VRAM (tested on NVIDIA RTX 3050)
- The `qwen3:4b` model pulled in Ollama

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/Study-helper.git
cd Study-helper

# 2. Create a virtual environment and install dependencies
python -m venv .venv
.venv/bin/pip install -r requirements.txt

# 3. Make sure Ollama is running and pull the model
ollama pull qwen3:4b

# 4. Start the server
.venv/bin/python server.py
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Sharing with a Friend (ngrok)

If you want someone else to try it without any setup on their end:

```bash
# Install ngrok (no sudo needed)
curl -sSL -o /tmp/ngrok.zip https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.zip
unzip -o /tmp/ngrok.zip -d ~/.local/bin

# Authenticate (get your token from https://dashboard.ngrok.com)
~/.local/bin/ngrok config add-authtoken YOUR_TOKEN

# Start the server and expose it
.venv/bin/python server.py &
~/.local/bin/ngrok http 8000
```

Send the ngrok URL to your friend. They just open it in a browser — your machine does all the AI work.

## Project Structure

```
Study-helper/
  server.py          # FastAPI backend (extract + guide endpoints)
  prompts.py         # LLM system prompts and JSON schemas
  requirements.txt   # Python dependencies
  static/
    index.html       # Entire frontend (HTML + CSS + JS in one file)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Check server + Ollama status |
| `POST` | `/api/extract` | Extract topics from syllabus text |
| `POST` | `/api/guide` | Generate study guide for a topic |
| `GET` | `/` | Serve the frontend |

## License

MIT
