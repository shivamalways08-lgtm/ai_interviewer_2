# IntervueAI — Hackathon Demo Script (3–5 Minutes)

> **Goal**: Wow the hackathon judges by demonstrating a complete, working adaptive interview in English and Hindi, showcasing real-time difficulty transitions, evidence-based scoring, and human-in-the-loop decision making.

---

## 🕒 Minute 0:00 – 0:30 | The Hook & Problem Statement

**Speaker**:
> *"Judges, traditional first-round technical interviews are broken in two huge ways:*
> *1. They rely on fixed, static questionnaires that can't adapt to a candidate's real skill level.*
> *2. They unfairly penalize non-native English speakers whose algorithmic logic is top-tier but who express technical concepts better in Hindi or regional languages.*
> *Today, we are thrilled to present **IntervueAI**: An adaptive first-round technical interview platform with multilingual parity in English and Hindi, evidence-backed scoring, and human-in-the-loop governance."*

---

## 🕒 Minute 0:30 – 1:15 | Landing Page & 1-Click Demo Showcase

**Action on Screen**:
1. Show the landing page at `http://localhost:5173`.
2. Scroll to the **"Why IntervueAI?"** section.
3. Highlight the 5 key differentiators:
   - **Adaptive Questioning**
   - **Multilingual Equality**
   - **Evidence-Backed Scoring**
   - **Fairness-by-Design**
   - **Human-in-the-Loop Hiring**
4. Click **"Try 1-Click Demo"** in the navigation bar.

**Speaker**:
> *"Right from the start, judges can inspect a completed technical dossier. Notice our first candidate, Aarav Sharma. He scored 84.4/100 for Software Developer Intern. The AI recommends 'Strong Match'—notice the system explicitly says 'AI does not make hiring decisions'."*

---

## 🕒 Minute 1:15 – 2:00 | The Star Feature: Evidence-Backed Scoring

**Action on Screen**:
1. Click on **"Programming Fundamentals"** to expand the accordion.
2. Point out the green quote box:
   `"Verbatim Candidate Evidence: '...Stack is organized as LIFO for local variables... Heap is dynamic allocation for objects...'"`
3. Show the **Recruiter Action Panel** at the bottom:
   - Click **[ Shortlist for Team Round ]**
   - Type in the recruiter note box: *"Strong system trade-offs. Proceed to live team round."*
   - Click **[ Save Recruiter Notes ]**

**Speaker**:
> *"This is our core differentiator: zero black-box ratings. Every score is directly anchored to verbatim quotes from what the candidate actually wrote or spoke. If a score cannot be proven with candidate quotes, it's rejected. And the final hiring decision belongs 100% to the human recruiter."*

---

## 🕒 Minute 2:00 – 3:15 | Multilingual Parity & Live Adaptive Interview

**Action on Screen**:
1. In the navbar, click **"Start Interview"**.
2. Show the setup screen:
   - Job Role: *Software Developer Intern*
   - Language: Click **[ हिंदी (Hindi) ]** 🇮🇳
   - Mode: Click **[ Voice Mode ]** 🎤 or **[ Text Mode ]**
   - Show the mandatory **Candidate Consent & Fairness Guarantee** box.
   - Check the box: *"I agree to the AI evaluation terms..."*
   - Click **[ I Agree & Start Interview ]**.
3. **Turn 1 (Medium Question in Hindi)**:
   - Question appears in Hindi: *"Stack और Heap मेमोरी में क्या अंतर है?..."*
   - Click the audio button: **[ 🔊 Listen to Question ]** to hear it read aloud.
   - Click demo button: **[ 💡 Strong Answer (Score >75) ]**.
   - Click **[ Submit Answer ]**.
4. **Adaptive Feedback Modal**:
   - Point to the modal: Score = **84/100**.
   - Point to the verbatim Hindi evidence quote harvested from the candidate's answer.
   - Point to the adaptive transition: **"Score > 70 → Increasing difficulty from MEDIUM to HARD for next question!"**
   - Click **[ Proceed to Next Question ]**.
5. **Turn 2 (Hard Question in Hindi)**:
   - Point out the difficulty badge is now **HARD**!
   - Click demo button: **[ ⚠️ Weak Answer (Score <40) ]**.
   - Click **[ Submit Answer ]**.
   - Point to the modal: Score = **25/100**.
   - Notice the adaptive transition: **"Supportive pacing: Next question adjusted to MEDIUM!"**

**Speaker**:
> *"Notice the magic: IntervueAI evaluated technical depth in Hindi with zero penalty. When the candidate aced the first question, the engine scaled difficulty up to HARD. When the candidate struggled, it adapted back to MEDIUM to test baseline problem solving. This is a true adaptive interview, not a rigid script."*

---

## 🕒 Minute 3:15 – 4:00 | Recruiter Dashboard & Ethics Wrap-Up

**Action on Screen**:
1. Click **"Recruiter Dashboard"** in the top navigation.
2. Show the KPI stats (Total Assessed, Avg Score, Hindi Interviews, Bias = 0%).
3. Filter by **हिंदी** to show Pooja Verma's dossier.
4. Click **"Fairness System"** tab to display the Ethics Manifesto (protected attributes like gender, caste, age, religion, accent strictly ignored).

**Speaker**:
> *"To conclude: IntervueAI is ready to run out of the box with zero external dependencies, while fully supporting live Gemini and OpenAI LLMs. It brings fairness, multilingual accessibility, and evidence-based rigor to the future of hiring.*
> *Thank you, and we welcome your questions!"*
