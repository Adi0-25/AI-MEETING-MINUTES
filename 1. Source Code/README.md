# AI Meeting Minutes

Convert meeting recordings into professional, structured meeting minutes — all locally on your machine, with zero cloud dependencies.

## Features

- **Audio Transcription** — Upload `.mp3`, `.wav`, `.m4a` etc. or record live; transcribed with OpenAI Whisper (via Faster-Whisper)
- **AI Summarization** — Generates structured Meeting Minutes (Executive Summary, Key Points, Decisions, Action Items) using Qwen1.5-0.5B-Chat LLM
- **Long-Meeting Support** — Map-Reduce semantic chunking handles transcripts of any length without crashing
- **Multi-language** — Translates summaries to 6+ languages via Helsinki-NLP MarianMT
- **Export** — Export finalized minutes as a formatted PDF
- **Privacy First** — 100% offline. No audio or text is ever sent to a third-party API

## Prerequisites

- **Python 3.9+** (added to PATH)
- **ffmpeg** — required by Whisper for audio decoding
  - Windows: `winget install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org/download.html)
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Setup

```bash
# 1. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Run the app
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

> **Note:** On first run, the AI models (~2-3 GB total) will be downloaded and cached automatically. Subsequent runs use cached models and start instantly.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Transcription | OpenAI Whisper via Faster-Whisper + CTranslate2 |
| Summarization | Qwen/Qwen1.5-0.5B-Chat (HuggingFace) |
| Translation | Helsinki-NLP MarianMT |
| Frontend | Vanilla HTML5 / CSS3 / JavaScript |
| PDF Export | html2pdf.js (client-side) |

## Performance Notes

- GPU acceleration is automatic if CUDA is available (uses float16)
- CPU-only mode uses int8 quantization via CTranslate2 for efficiency
- Upload limit is 100MB
- Models are cached in memory after first load for instant subsequent requests
