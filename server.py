"""
Study Helper — FastAPI backend.

Calls Ollama (qwen3:4b) to extract study topics from pasted syllabus text.
Serves the static frontend from ./static/.

Usage:
    python server.py
"""

import json
import os
import time
import logging

import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from prompts import EXTRACT_SYSTEM, EXTRACT_JSON_SCHEMA, GUIDE_SYSTEM, GUIDE_JSON_SCHEMA

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL = "qwen3:4b"
OLLAMA_BASE = os.getenv("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "120"))  # seconds

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------

app = FastAPI(title="Study Helper", version="0.1.0")

# Allow the local frontend to call the API (belt-and-suspenders; same-origin
# when served from StaticFiles, but handy during development).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------

class ExtractRequest(BaseModel):
    text: str


class Topic(BaseModel):
    title: str
    difficulty: int
    hours: float


class ExtractResponse(BaseModel):
    topics: list[Topic]
    elapsed_seconds: float


class GuideRequest(BaseModel):
    topic: str
    context: str = ""


class GuideConcept(BaseModel):
    name: str
    explanation: str


class GuideResponse(BaseModel):
    concepts: list[GuideConcept]
    tips: str
    elapsed_seconds: float


# ---------------------------------------------------------------------------
# Ollama helper
# ---------------------------------------------------------------------------

def call_ollama(user_text: str, system_prompt: str = EXTRACT_SYSTEM, json_schema: dict = EXTRACT_JSON_SCHEMA) -> dict:
    """Send a chat completion to Ollama (qwen3:4b) and return parsed JSON."""

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "stream": False,
        "format": json_schema,  # forces valid JSON output
        "think": False,                 # disable extended thinking (spirals on small inputs)
        "options": {
            "temperature": 0.3,         # low creativity for extraction
            "num_predict": 2048,        # enough tokens for a big syllabus
        },
    }

    url = f"{OLLAMA_BASE}/api/chat"
    log.info("→ Ollama  input_chars=%d", len(user_text))

    try:
        resp = requests.post(url, json=payload, timeout=OLLAMA_TIMEOUT)
        resp.raise_for_status()
    except requests.ConnectionError:
        raise HTTPException(
            status_code=503,
            detail="Cannot reach Ollama. Is it running?  Try: systemctl start ollama",
        )
    except requests.Timeout:
        raise HTTPException(
            status_code=504,
            detail=f"Ollama did not respond within {OLLAMA_TIMEOUT}s. "
                   "Try shorter input.",
        )
    except requests.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Ollama error: {exc}")

    body = resp.json()
    content = body.get("message", {}).get("content", "")

    # Parse the JSON content from Ollama's response.
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        log.error("Ollama returned invalid JSON: %s", content[:500])
        raise HTTPException(
            status_code=502,
            detail="Model returned invalid JSON. Try again.",
        )

    return data


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    """Quick check that the server and Ollama are reachable."""
    try:
        r = requests.get(f"{OLLAMA_BASE}/api/tags", timeout=5)
        r.raise_for_status()
        models = [m["name"] for m in r.json().get("models", [])]
    except Exception:
        models = []
    return {
        "status": "ok",
        "model": MODEL,
        "ollama_reachable": len(models) > 0,
    }


@app.post("/api/extract", response_model=ExtractResponse)
def extract_topics(req: ExtractRequest):
    """Extract study topics from pasted syllabus text."""

    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    if len(text) > 50_000:
        raise HTTPException(status_code=400, detail="Text too long (max 50 000 chars).")

    start = time.perf_counter()
    data = call_ollama(text)
    elapsed = round(time.perf_counter() - start, 2)

    topics = data.get("topics", [])
    if not topics:
        raise HTTPException(
            status_code=422,
            detail="Model returned zero topics. Paste more detailed syllabus text.",
        )

    log.info("← Ollama  topics=%d  elapsed=%.2fs", len(topics), elapsed)

    return ExtractResponse(topics=topics, elapsed_seconds=elapsed)


@app.post("/api/guide", response_model=GuideResponse)
def generate_guide(req: GuideRequest):
    """Generate a study guide for a given topic — key concepts and tips."""

    topic = req.topic.strip()
    if not topic:
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")

    user_text = f"Topic: {topic}"
    if req.context:
        user_text += f"\nContext: {req.context}"

    start = time.perf_counter()
    data = call_ollama(user_text, system_prompt=GUIDE_SYSTEM, json_schema=GUIDE_JSON_SCHEMA)
    elapsed = round(time.perf_counter() - start, 2)

    concepts = data.get("concepts", [])
    tips = data.get("tips", "")
    if not concepts:
        raise HTTPException(
            status_code=422,
            detail="Model returned no concepts.",
        )

    log.info("← Ollama guide  concepts=%d  elapsed=%.2fs", len(concepts), elapsed)

    return GuideResponse(concepts=concepts, tips=tips, elapsed_seconds=elapsed)


# ---------------------------------------------------------------------------
# Serve frontend
# ---------------------------------------------------------------------------

# Create the static directory if it doesn't exist yet.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def root():
    index = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "Study Helper API is running. Frontend not built yet."}


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    log.info("Starting Study Helper  model=%s  ollama=%s", MODEL, OLLAMA_BASE)
    uvicorn.run(app, host="0.0.0.0", port=8000)
