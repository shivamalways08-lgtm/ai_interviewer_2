# IntervueAI 🎙️

> **Adaptive AI Interviewer – Fair Interviews in More Than One Language**  
> *"Fair interviews. Smarter evaluation. Every candidate gets a voice."*

![IntervueAI](https://img.shields.io/badge/Status-Hackathon%20Ready%20MVP-success?style=for-the-badge)
![Languages](https://img.shields.io/badge/Languages-English%20%7C%20%E0%A4%B9%E0%A4%BF%E0%A4%82%E0%A4%A6%E0%A4%80-blue?style=for-the-badge)
![Stack](https://img.shields.io/badge/Stack-React%20%2B%20FastAPI%20%2B%20SQLite-indigo?style=for-the-badge)

---

## 📌 1. Problem Statement
First-round technical interviews in modern recruitment suffer from systemic flaws:
1. **Rigid, Static Questionnaires**: Interviews ask candidates a fixed, pre-determined list of questions regardless of whether a candidate is struggling or easily answering every prompt.
2. **Linguistic Penalty**: Non-native English speakers who have exceptional technical problem-solving ability are often scored poorly simply due to accent, regional phrasing, or lack of native English fluency.
3. **Black-Box AI Scoring**: Traditional automated evaluation tools assign arbitrary scores without verifiable citations or proof from what the candidate actually said.
4. **Autonomous AI Overreach**: Systems claim to decide who gets "hired", creating severe ethical and legal compliance risks.

---

## 💡 2. The IntervueAI Solution
**IntervueAI** is an adaptive, multilingual first-round interview platform designed with fairness and verifiable proof at its core:
- **Real-Time Adaptive Engine**: Dynamically shifts difficulty between **EASY**, **MEDIUM**, and **HARD** based on candidate responses.
- **Bilingual Parity (English & हिंदी)**: Evaluates technical substance equally in English and Hindi without accent or language penalties.
- **Verbatim Evidence Citations**: Every single score extracts and cites direct quotes from the candidate's transcript as verifiable proof.
- **Fairness-by-Design**: Explicitly filters and ignores demographic attributes (gender, age, appearance, religion, caste, nationality, accent).
- **Human-in-the-Loop Governance**: AI only generates structured insights and recommendations ("Strong Match", "Potential Match"). The final shortlisting and hiring decision rests entirely with the human recruiter.
- **Zero-Config Demo Mode**: 100% runnable offline out of the box with intelligent rubric evaluation, with seamless support for live Gemini and OpenAI LLM APIs.
- **Google Gemini 2.5 Flash Integration**: Real-time LLM-powered evaluation, dynamic contextual follow-up question generation, and evidence harvesting via official `google-genai` SDK.

---

## ⚡ 2.1 Enabling Live Google Gemini AI (Optional but Recommended)

IntervueAI features native integration with Google's latest **Gemini 2.5 Flash** model via the official `google-genai` SDK.

### Method A: In-App UI (Easiest)
1. Open the web app at `http://localhost:5173`.
2. Click the **"AI: Offline Rubric"** badge in the top navigation bar.
3. Paste your key from [Google AI Studio](https://aistudio.google.com/app/apikey) (Free).
4. Click **"Test Connection"** → **"Save & Activate"**.
5. The badge will glow **"⚡ Gemini Active"**, and all subsequent answers will be evaluated with live Gemini AI!

### Method B: Environment Variable (`.env`)
1. Open `.env` in the root folder.
2. Add your key:
   ```env
   GEMINI_API_KEY=AIzaSy...your_key_here
   ```
3. Restart the backend or let uvicorn reload automatically.

*Note: If no key is provided, IntervueAI automatically falls back to its deterministic rubric evaluator so your hackathon demo never fails or crashes.*

---

## 🚀 3. Quick Start (Beginner-Friendly Setup)

Running IntervueAI locally requires two terminal windows in VS Code.

### Prerequisites
- **Python 3.10+** (Python 3.12 is bundled in `.venv`)
- **Node.js 18+** & npm

---

### Step 1: Start the Backend (Terminal 1)

1. Open your terminal in the project root:
   ```powershell
   cd c:\Users\Vansh\Documents\ai_interviewer_2
   ```

2. Activate the virtual environment:
   - On Windows (PowerShell):
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - On Windows (Command Prompt):
     ```cmd
     .\.venv\Scripts\activate.bat
     ```

3. Run the FastAPI server:
   ```powershell
   python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

4. The backend is live at: `http://127.0.0.1:8000` (API Docs at `/docs`).

---

### Step 2: Start the Frontend (Terminal 2)

1. Open a **second** terminal window:
   ```powershell
   cd c:\Users\Vansh\Documents\ai_interviewer_2\frontend
   ```

2. Start the Vite dev server:
   ```powershell
   npm run dev
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 🎯 4. 1-Click Interactive Demo (For Hackathon Judges)

Judges can explore the complete platform in **under 60 seconds** without typing long answers:
1. Open `http://localhost:5173`.
2. Click **"Try 1-Click Demo"** in the top navigation bar.
3. This opens a pre-evaluated dossier for **Aarav Sharma (English)** or **Pooja Verma (हिंदी)**.
4. Expand any competency (e.g. *Programming Fundamentals*) to see the **Verbatim Evidence Quote**.
5. Test the **Human Recruiter Action Panel**: Click **[ Shortlist for Team Round ]**, add a note, and save!
6. Click **"Start Interview"** → Select **हिंदी** → Use the **💡 Strong Answer** and **⚠️ Weak Answer** quick-fill buttons to watch the question difficulty scale up and down in real time!

---

## 🧠 5. How the Adaptive Engine Works

The interview progresses through 5 job-related competencies for **Software Developer Intern**:
1. Programming Fundamentals
2. Problem Solving
3. Data Structures & Algorithms
4. Technical Understanding
5. Communication

At each turn, the candidate's answer is evaluated (0–100):

| Candidate Score | Difficulty Action | Pedagogical Rationale |
| :--- | :--- | :--- |
| **Score < 40** | **Decrease (to EASY)** | Adjusts to a concept-check question to assess foundational baseline |
| **Score 40 – 70** | **Maintain (MEDIUM)** | Consolidates competency before advancing |
| **Score > 70** | **Increase (to HARD)** | Probes deeper architectural understanding and edge cases |

---

## 🌐 6. How Multilingual Support Works

- The candidate chooses their preferred language before starting: **English** or **हिंदी**.
- Questions are rendered natively in the selected language.
- Audio text-to-speech reads the question aloud in either English (`en-US`) or Hindi (`hi-IN`).
- Answers can be spoken via Web Speech API or typed in English, Hindi, or conversational Hinglish.
- Evaluation focuses strictly on **technical concepts** (e.g. Stack LIFO, Hash collision, O(N) complexity) rather than accent or language syntax.

---

## 🔍 7. Evidence-Based Scoring Mechanics

IntervueAI rejects unsupported ratings. For every competency score:
$$\text{Score} \longrightarrow \text{Rationale} \longrightarrow \mathbf{Verbatim\ Evidence\ Excerpt}$$

**Example:**
- **Skill**: Data Structures & Algorithms
- **Score**: 85/100
- **Verbatim Evidence**: `"...To achieve O(1) for both get and put in an LRU cache, combine a Hash Map and a Doubly Linked List. Map gives O(1) lookup, list maintains recency with head and tail..."`
- **Rationale**: *"Candidate correctly explained dual data structure mechanics for constant time cache lookups and tail eviction."*

If an answer is too brief or evasive, the system states:
> *"Insufficient evidence from this answer."*

---

## ⚖️ 8. Fairness & Privacy Architecture

- **Protected Attributes Disregarded**: The system explicitly scans and strips demographic mentions (gender, age, appearance, religion, caste, nationality, regional accent).
- **No Autonomous Hiring**: AI output is labeled `Assistive Recommendation` ("Strong Match", "Potential Match", "Needs Further Review").
- **Human Decision Buttons**: Recruiter explicitly selects `[ Shortlist ]`, `[ Review Later ]`, or `[ Decline ]`.
- **Privacy By Design**: Candidates are evaluated under anonymous identifiers (e.g. `Anonymous Candidate #042`).

---

## 🛠️ 9. Technology Stack

- **Frontend**: React 18, Vite, Lucide Icons, Canvas Confetti, Vanilla CSS Design System.
- **Backend**: FastAPI, Python 3.12, Uvicorn, Pydantic v2.
- **Database**: SQLite3 with thread-safe persistence.
- **Speech**: Browser Web Speech API (`SpeechRecognition` & `SpeechSynthesis`).
- **AI Engine**: Live Google Gemini 1.5 Flash / OpenAI GPT-4o-mini with seamless Fallback Semantic Rubric Evaluator.
- **Testing**: Pytest with automated unit and end-to-end integration test suites.

---

## 🧪 10. Running Automated Tests

Run the test suite from the project root:
```powershell
.\.venv\Scripts\python.exe -m pytest tests/
```
All 6 tests verify:
- Adaptive difficulty transitions (<40, 40-70, >70)
- Bilingual concept matching (English & Hindi)
- Verbatim evidence extraction
- Protected attribute exclusion
- Full 5-turn interview session lifecycle

---

## 🔮 11. Future Roadmap
- Additional roles: Data Analyst, Hardware Engineer, Marketing Specialist.
- Additional languages: Tamil, Telugu, Bengali, Spanish, French.
- Live video posture / eye-contact assessment toggle (with explicit opt-in).
- ATS integrations: Greenhouse, Lever, Workday webhooks.

---

## 📄 License
MIT License. Built for hackathon demonstration and ethical recruitment research.
