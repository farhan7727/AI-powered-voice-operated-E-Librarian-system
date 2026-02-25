# AI-Powered Voice-Operated E-Librarian System

🎥 **Demo Video:** [Watch on Google Drive](https://drive.google.com/file/d/1paX9TCm8gIrnN5gKq-W4xrp3SrLVyfC_/view?usp=sharing)

An end-to-end voice librarian assistant that turns spoken queries into database-backed book recommendations and conversational summaries.

This repository now supports two product paths built on the same core retrieval/summarization logic:

1. **Local transcriber pipeline (`src/demo.py`)**  
   `Speech → STT → SQL generation → DB fetch → LLM summary → TTS`
2. **VAPI web assistant (`src/index.html` + `src/app.py`)**  
   Browser/VAPI voice call → backend tool call → SQL generation → DB fetch → LLM summary

---

## Latest Project Evolution

The implementation has evolved in two steps:

- **Step 1: `demo.py` pipeline**
  - Added a Gradio experience that records local microphone audio.
  - Uses local STT + SQL + summary + TTS in one synchronous flow.
  - Useful for quick local validation of the full audio loop.

- **Step 2: VAPI assistant architecture (`index.html` + `app.py`)**
  - Introduced a browser-based VAPI assistant UI (`index.html`) for a smoother call-style UX.
  - Added FastAPI backend endpoint (`app.py`) to handle VAPI tool calls.
  - Backend calls shared modules (`llm_query.py`, `db_manager.py`) to generate SQL and return summarized results.
  - This approach optimizes the interaction model by offloading voice orchestration to VAPI while reusing existing retrieval logic.

---

## Core Modules

- `src/stt.py` — Records audio and transcribes speech using Deepgram.
- `src/llm_query.py` — Converts user intent into SQLite SQL for the `books` table.
- `src/db_manager.py` — Executes SQL against `data/library.db` and generates a librarian-style summary with OpenAI.
- `src/tts.py` — Synthesizes spoken response from summary text.
- `src/demo.py` — Gradio orchestration for local end-to-end voice demo.
- `src/app.py` — FastAPI backend endpoint for VAPI tool calls.
- `src/index.html` — Browser UI integrating the VAPI web call assistant.
- `src/main.py` — CLI orchestrator for the core pipeline.

---

## Architecture

### A) Local Demo Flow (`demo.py`)

1. Record microphone input.
2. Transcribe speech to text.
3. Convert text to SQL.
4. Query SQLite books database.
5. Summarize book results.
6. Generate voice response audio.

### B) VAPI Web Flow (`index.html` + `app.py`)

1. User starts a call in the VAPI web widget.
2. VAPI issues backend tool call (`find_books`) to FastAPI.
3. FastAPI extracts `query` from tool arguments.
4. Query text is converted to SQL via `llm_query.py`.
5. SQL is executed and summarized via `db_manager.py`.
6. Summary is returned in tool response payload to VAPI assistant.

---

## Project Structure

```text
.
├── data/
│   ├── books.json
│   └── library.db
├── ingestion/
│   └── data_ingestion.ipynb
├── src/
│   ├── app.py
│   ├── db_manager.py
│   ├── demo.py
│   ├── index.html
│   ├── llm_query.py
│   ├── main.py
│   ├── stt.py
│   └── tts.py
├── LICENSE
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Microphone access (for local STT/demo/CLI flows)
- Audio playback support (for local TTS playback)
- API keys:
  - `DEEPGRAM_API`
  - `OPENAI_API`
- VAPI credentials (for `index.html` flow):
  - `assistant` ID
  - `apiKey`

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install numpy sounddevice "deepgram-sdk<3.0" python-dotenv scipy openai pygame gradio fastapi uvicorn pydantic
```

Create `.env` in project root:

```env
DEEPGRAM_API=your_deepgram_key
OPENAI_API=your_openai_key
```

---

## Run Options

### 1) CLI Pipeline

```bash
python src/main.py
```

### 2) Gradio Demo Pipeline

```bash
python src/demo.py
```

Then open the printed Gradio URL (usually `http://127.0.0.1:7860`).

### 3) VAPI Backend + Web UI

Start backend (from `src/` directory):

```bash
cd src
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Then configure `assistant` and `apiKey` constants in `src/index.html`, and open `index.html` in a browser.

> Note: VAPI must be configured so its tool call maps to the backend endpoint `/LibrarianSearchResponse`.

---

## Example Queries

- “Recommend me 3 fiction books.”
- “Find books about machine learning.”
- “Suggest philosophy books by well-known authors.”
- “Give me nonfiction recommendations.”

---

## Troubleshooting

- **Transcription fails**
  - Check `DEEPGRAM_API`.
  - Verify microphone permissions.

- **No summary / backend errors**
  - Check `OPENAI_API`.
  - Confirm `data/library.db` exists and is readable.

- **VAPI call works but no results**
  - Verify tool name is `find_books`.
  - Verify tool argument includes `query`.
  - Verify backend endpoint path is `/LibrarianSearchResponse`.

- **No audio playback in local flow**
  - Ensure system audio output is working.
  - Ensure `pygame` installed correctly.

  ---
