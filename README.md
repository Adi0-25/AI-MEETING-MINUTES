# AI Meeting Minutes System — Soft Copy Submission

**Mini Project | School of Computer Engineering | KIIT Deemed to be University**

---

## Folder Structure

```
Submission/
│
├── 1. Source Code/              ← Complete application source code
│   ├── app.py                   ← Flask backend server & API endpoints
│   ├── transcriber.py           ← Whisper ASR transcription module
│   ├── summarizer.py            ← Qwen LLM summarization & MarianMT translation
│   ├── requirements.txt         ← All Python dependencies
│   ├── README.md                ← Setup & run instructions
│   ├── sample_meeting.mp3       ← Sample audio file for demo
│   └── public/
│       ├── index.html           ← Frontend UI
│       ├── app.js               ← Frontend application logic
│       ├── style.css            ← Glassmorphism dark-mode styles
│       └── favicon.svg          ← App icon
│
├── 2. Project Report/           ← All documentation
│   ├── AI_Meeting_Minutes_Full_Report.docx   ← Full 8-chapter technical report
│   ├── KIIT_Format_Report.docx               ← KIIT university format report
│   ├── Technical_Research_Report.md          ← Deep technical research document
│   └── Mini_Project_Report.md                ← Concise mini project report
│
└── 3. Presentation/             ← Presentation materials
    ├── Presentation.pptx        ← PowerPoint slides (7 slides)
    ├── Presentation_3D.pdf      ← 3D glassmorphism PDF presentation
    └── Presentation_Slides.html ← Interactive HTML presentation (open in browser)
```

---

##  How to Run the Application

### Prerequisites
- Python 3.9+
- ffmpeg installed and added to PATH

### Steps
```bash
# 1. Navigate to Source Code folder
cd "1. Source Code"

# 2. Create virtual environment
python -m venv venv

# 3. Install dependencies (Windows)
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Run the app (Windows)
.\venv\Scripts\python.exe app.py
```

Open **http://localhost:5000** in your browser.

> **Note:** First run downloads AI models (~2-3 GB). Ensure internet connection for initial setup.

---

##  Tech Stack

| Component | Technology |
|---|---|
| Backend Server | Flask (Python) |
| Speech Recognition | OpenAI Whisper via Faster-Whisper + CTranslate2 |
| AI Summarization | Qwen/Qwen1.5-0.5B-Chat (HuggingFace) |
| Translation | Helsinki-NLP MarianMT |
| Frontend | Vanilla HTML5 / CSS3 / JavaScript |
| PDF Export | html2pdf.js (client-side rendering) |

---

*All AI processing runs 100% locally. No data is sent to any external cloud API.*
