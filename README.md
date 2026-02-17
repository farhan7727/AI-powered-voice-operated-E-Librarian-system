# AI-Powered Voice-Operated E-Librarian System

A voice-first librarian assistant that listens to a user query, converts speech to text, translates the request into SQL, fetches books from a local SQLite library database, summarizes the results with an LLM, and reads the answer aloud.

The project currently supports two ways to run:
- **CLI pipeline** (`src/main.py`)
- **Gradio web demo** (`src/demo.py`)

## Project Workflow (Step-by-Step)
This is the exact runtime flow used in the code:
This is the runtime flow used in the app logic:

1. **Capture microphone audio** (`src/stt.py`)
   - Records audio from the default microphone for a fixed duration.
   - Saves the recording as a WAV file.

2. **Speech-to-text transcription** (`src/stt.py`)
   - Sends the recorded audio to Deepgram.
   - Returns the transcribed user request as plain text.

3. **Convert natural language to SQL** (`src/llm_query.py`)
   - Sends user text and DB schema to OpenAI.
   - Generates a SQLite query targeting the `books` table.

4. **Execute SQL query on local database** (`src/db_manager.py`)
   - Runs the generated query on `data/library.db`.
   - Collects matching rows and column information.

5. **Generate librarian-style summary** (`src/db_manager.py`)
   - Sends query results to OpenAI chat completion.
   - Produces a short conversational book summary.

6. **Text-to-speech output** (`src/tts.py`)
   - Converts summary text into speech audio (MP3) with OpenAI TTS.
   - Plays the generated audio locally using `pygame`.
   - Cleans up temporary input audio file.
   - In CLI mode, plays the generated audio locally using `pygame`.
   - In Gradio mode, returns the generated audio file to the UI player.

7. **Orchestration entrypoint** (`src/main.py`)
   - Calls all above modules in sequence from one `main()` function.
7. **Orchestration entrypoints**
   - `src/main.py`: runs the full flow in terminal.
   - `src/demo.py`: runs the full flow behind a Gradio interface.

---

## Repository Structure

```text
.
├── data/
│   ├── books.json              # Raw/seed book records
│   ├── library.db              # SQLite database queried by the assistant
│   └── output.mp3              # Generated speech output (runtime artifact)
├── ingestion/
│   └── data_ingestion.ipynb    # Notebook used for data ingestion/preparation
├── src/
│   ├── main.py                 # Application entrypoint
│   ├── main.py                 # CLI application entrypoint
│   ├── demo.py                 # Gradio web demo entrypoint
│   ├── stt.py                  # Speech-to-text (record + transcribe)
│   ├── llm_query.py            # Natural language -> SQL conversion
│   ├── db_manager.py           # SQL execution + summary generation
│   └── tts.py                  # Text-to-speech generation + playback
└── README.md
```

---

## Prerequisites

- Python 3.10+
- Microphone input enabled
- Audio playback support on your machine
- API keys:
  - Deepgram API key (for STT)
  - OpenAI API key (for SQL generation, summarization, and TTS)

---

## Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-powered-voice-operated-E-Librarian-system
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install numpy sounddevice "deepgram-sdk<3.0" python-dotenv scipy openai pygame
   pip install numpy sounddevice "deepgram-sdk<3.0" python-dotenv scipy openai pygame gradio
   ```

4. **Create environment file**
   ```bash
   cp .env.example .env  # if example file exists
   ```
   If `.env.example` is not present, create `.env` manually.

5. **Add required environment variables in `.env`**
   ```env
   DEEPGRAM_API=your_deepgram_api_key
   OPENAI_API=your_openai_api_key
   ```

---

## How to Run

### Option 1: CLI pipeline
From the project root:

```bash
python src/main.py
```

When you run it:
- The app records your voice.
- It transcribes your question.
- It builds and executes a SQL query.
- It summarizes matching books.
- It speaks the answer aloud.
### Option 2: Gradio web demo
From the project root:

```bash
python src/demo.py
```

Then open the local URL printed by Gradio (commonly `http://127.0.0.1:7860`).

---

## Example Voice Queries

- “Recommend me 3 fiction books.”
- “Find books about machine learning.”
- “Suggest some philosophy titles by famous authors.”
- “Give me nonfiction recommendations.”

---

## Notes & Tips

- Ensure your microphone is available before starting.
- Keep your spoken request short and clear for better transcription quality.
- The SQL generation logic is tuned around the `books` table schema in `src/llm_query.py`.
- The local SQLite DB path is configured in `src/db_manager.py`.

---

## Troubleshooting

- **No transcription output**
  - Verify `DEEPGRAM_API` in `.env`.
  - Check microphone permissions/device availability.

- **No spoken output**
  - Verify `OPENAI_API` in `.env`.
  - Ensure audio playback works and `pygame` is installed.

- **Gradio UI not launching**
  - Ensure `gradio` is installed in the active environment.
  - Check the terminal for local URL/port binding errors.

- **SQL/query issues**
  - Validate that `data/library.db` exists.
  - Check that the `books` table/schema matches the prompt assumptions.

---
