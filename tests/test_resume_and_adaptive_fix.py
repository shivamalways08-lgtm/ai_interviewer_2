"""
Comprehensive Test Suite for Resume Upload, Parsing, Personalization, and Adaptive Engine Bugfix.
Validates:
1. Resume upload validation (valid PDF, valid DOCX, empty file rejection, unsupported file rejection).
2. Resume personalization (React vs Python resume content influences Turn 0 questions).
3. Adaptive Engine Branching: Weak (0-4 / <40) -> EASY, Moderate (5-7 / 40-70) -> MEDIUM, Strong (8-10 / >70) -> HARD.
4. Same-Question Bug Prevention: Verifies distinct next questions across score bands and no repeated questions.
5. Report and History API endpoints verify resume_info and per-question response times.
"""

import io
import pytest
from fastapi.testclient import TestClient
from docx import Document

from backend.main import app
from backend.services.resume_parser import (
    validate_resume_file,
    deterministic_parse_resume,
    parse_and_analyze_resume
)

@pytest.fixture
def client():
    return TestClient(app)

def create_sample_docx(text_blocks):
    """Helper to create an in-memory DOCX file."""
    doc = Document()
    for block in text_blocks:
        doc.add_paragraph(block)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

def create_sample_pdf(text_lines):
    """Helper to create a valid in-memory PDF file without third-party PDF generators."""
    stream = "".join(f"BT /F1 12 Tf 72 {750 - i*25} Td ({line}) Tj ET\n" for i, line in enumerate(text_lines))
    stream_len = len(stream)
    pdf = f"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj
4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
5 0 obj << /Length {stream_len} >>
stream
{stream}endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000224 00000 n 
0000000297 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
400
%%EOF"""
    return pdf.encode('latin1')


# ============================================================================
# 1. RESUME FILE VALIDATION TESTS
# ============================================================================

def test_resume_validation_empty_file():
    """Empty files (0 bytes) must be rejected with ValueError / 400."""
    with pytest.raises(ValueError, match="empty"):
        validate_resume_file("empty.pdf", b"")

def test_resume_validation_unsupported_extension():
    """Unsupported extensions (.txt, .exe, .png) must be rejected."""
    with pytest.raises(ValueError, match="Unsupported file format"):
        validate_resume_file("notes.txt", b"Some random text")

def test_resume_validation_oversized_file():
    """Files exceeding 5MB must be rejected."""
    oversized = b"0" * (5 * 1024 * 1024 + 100)
    with pytest.raises(ValueError, match="exceeds maximum allowed size"):
        validate_resume_file("large.pdf", oversized)

def test_resume_upload_endpoint_valid_docx(client):
    """Uploading a valid DOCX returns parsed skills and projects."""
    docx_bytes = create_sample_docx([
        "TECHNICAL SKILLS",
        "React, JavaScript, HTML, CSS, REST APIs, Git",
        "PROJECTS",
        "Student Management System: Built a responsive web app using React and REST APIs for student registration.",
        "E-Commerce Portal: Developed shopping cart using React, Redux, and Node.js."
    ])
    
    files = {"file": ("resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    res = client.post("/api/resume/upload", files=files)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert data["filename"] == "resume.docx"
    assert "React" in data["detected_skills"]
    assert "JavaScript" in data["detected_skills"]
    assert len(data["detected_projects"]) >= 1

def test_resume_upload_endpoint_valid_pdf(client):
    """Uploading a valid PDF returns parsed skills and projects."""
    pdf_bytes = create_sample_pdf([
        "SKILLS",
        "Python, FastAPI, Docker, PostgreSQL, Machine Learning",
        "PROJECTS",
        "Predictive Sales Pipeline: Built end-to-end ML pipeline with Python and FastAPI."
    ])
    files = {"file": ("resume.pdf", pdf_bytes, "application/pdf")}
    res = client.post("/api/resume/upload", files=files)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["success"] is True
    assert "Python" in data["detected_skills"]
    assert len(data["detected_projects"]) >= 1

def test_resume_upload_endpoint_empty_and_invalid(client):
    """API endpoint rejects empty files and unsupported formats with 400."""
    files_empty = {"file": ("empty.pdf", b"", "application/pdf")}
    res_empty = client.post("/api/resume/upload", files=files_empty)
    assert res_empty.status_code == 400

    files_txt = {"file": ("resume.txt", b"Just some text", "text/plain")}
    res_txt = client.post("/api/resume/upload", files=files_txt)
    assert res_txt.status_code == 400


# ============================================================================
# 2. PERSONALIZATION: RESUME INFLUENCES TURN 0 QUESTIONS
# ============================================================================

def test_resume_personalization_react_vs_python(client):
    """
    Candidate with React resume gets a question about React or their React project.
    Candidate with Python resume gets a question about Python or their Python project.
    """
    # 1. Upload React Resume
    react_docx = create_sample_docx([
        "SKILLS: React, JavaScript, HTML, CSS",
        "PROJECTS",
        "Student Management System: Developed React frontend with state management."
    ])
    react_upload = client.post("/api/resume/upload", files={"file": ("react.docx", react_docx, "application/octet-stream")}).json()
    
    # Start interview with React resume
    react_intv = client.post("/api/interview/start", json={
        "name": "React Developer",
        "role": "Frontend Developer",
        "language": "en",
        "consent_agreed": True,
        "resume_id": react_upload["resume_id"],
        "total_questions": 5
    }).json()

    react_q = react_intv["first_question"]["question_text"].lower()
    assert ("react" in react_q or "student management" in react_q or "javascript" in react_q or "frontend" in react_q)

    # 2. Upload Python Resume
    py_docx = create_sample_docx([
        "SKILLS: Python, FastAPI, PostgreSQL, Pandas",
        "PROJECTS",
        "Predictive Sales Pipeline: Data science backend in Python."
    ])
    py_upload = client.post("/api/resume/upload", files={"file": ("python.docx", py_docx, "application/octet-stream")}).json()
    
    # Start interview with Python resume
    py_intv = client.post("/api/interview/start", json={
        "name": "Python Developer",
        "role": "Backend Developer",
        "language": "en",
        "consent_agreed": True,
        "resume_id": py_upload["resume_id"],
        "total_questions": 5
    }).json()

    py_q = py_intv["first_question"]["question_text"].lower()
    assert ("python" in py_q or "fastapi" in py_q or "predictive sales" in py_q or "backend" in py_q)


# ============================================================================
# 3. ADAPTIVE ENGINE BRANCHING & SAME-QUESTION BUG ELIMINATION
# ============================================================================

def test_adaptive_branching_weak_vs_moderate_vs_strong(client):
    """
    Given an identical initial interview and question, verify:
    - Weak answer (<40) branches to EASY difficulty with foundational diagnostic.
    - Moderate answer (40-70) branches to MEDIUM difficulty with practical application.
    - Strong answer (>70) branches to HARD difficulty with architectural scaling.
    - All three generated next questions are DISTINCT (solving the same-question bug!).
    """
    # Create a base resume
    resume_docx = create_sample_docx([
        "SKILLS: React, JavaScript, REST APIs",
        "PROJECTS",
        "Student Management System: Interactive dashboard for student grades using React."
    ])
    upload_res = client.post("/api/resume/upload", files={"file": ("resume.docx", resume_docx, "application/octet-stream")}).json()
    resume_id = upload_res["resume_id"]

    # Session 1: Weak answer
    s1 = client.post("/api/interview/start", json={
        "name": "Weak Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "consent_agreed": True,
        "resume_id": resume_id,
        "total_questions": 5
    }).json()
    q1 = s1["first_question"]

    res_weak = client.post("/api/interview/answer", json={
        "interview_id": s1["interview_id"],
        "question_id": q1["question_id"],
        "candidate_answer": "I don't know much about this, I just followed a tutorial online.",
        "response_time_seconds": 15
    }).json()
    assert res_weak["score"] < 40
    assert res_weak["next_difficulty"] == "EASY"
    q_next_weak = res_weak["next_question"]
    assert q_next_weak["difficulty"] == "EASY"

    # Session 2: Moderate answer
    s2 = client.post("/api/interview/start", json={
        "name": "Moderate Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "consent_agreed": True,
        "resume_id": resume_id,
        "total_questions": 5
    }).json()

    res_mod = client.post("/api/interview/answer", json={
        "interview_id": s2["interview_id"],
        "question_id": q1["question_id"],
        "candidate_answer": "In our Student Management System, we used React for building the UI and components. We selected React because it has good state management and is popular for frontend applications.",
        "response_time_seconds": 45
    }).json()
    assert 40 <= res_mod["score"] <= 75
    assert res_mod["next_difficulty"] == "MEDIUM"
    q_next_mod = res_mod["next_question"]
    assert q_next_mod["difficulty"] == "MEDIUM"

    # Session 3: Strong answer
    s3 = client.post("/api/interview/start", json={
        "name": "Strong Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "consent_agreed": True,
        "resume_id": resume_id,
        "total_questions": 5
    }).json()

    res_strong = client.post("/api/interview/answer", json={
        "interview_id": s3["interview_id"],
        "question_id": q1["question_id"],
        "candidate_answer": "In our Student Management System, the architecture followed a 3-tier client-server design where React handled the presentation layer with component-based state, and Node.js REST APIs served PostgreSQL data. We selected React because its component reusability and Virtual DOM enabled fast rendering of student grade dashboards. A major challenge was optimizing frequent re-renders in large student tables, which we solved by implementing pagination and React.memo trade-offs.",
        "response_time_seconds": 60
    }).json()
    assert res_strong["score"] > 70
    assert res_strong["next_difficulty"] == "HARD"
    q_next_strong = res_strong["next_question"]
    assert q_next_strong["difficulty"] == "HARD"

    # Crucial Verification: Verify all 3 questions are distinct!
    weak_text = q_next_weak["question_text"]
    mod_text = q_next_mod["question_text"]
    strong_text = q_next_strong["question_text"]

    assert weak_text != mod_text, "Weak and Moderate answers must NOT produce the same next question!"
    assert mod_text != strong_text, "Moderate and Strong answers must NOT produce the same next question!"
    assert weak_text != strong_text, "Weak and Strong answers must NOT produce the same next question!"
    assert weak_text != q1["question_text"], "Next question must not repeat the previous question!"


# ============================================================================
# 4. REPORT & INTERVIEW HISTORY VERIFICATION
# ============================================================================

def test_report_and_history_api(client):
    """
    Verify /api/interview/{id}/history and /api/interview/{id}/report
    contain resume_info, turns, response_time_seconds, and verbatim evidence quotes.
    """
    resume_docx = create_sample_docx([
        "SKILLS: JavaScript, React",
        "PROJECTS",
        "Portfolio App: Interactive web app built with React."
    ])
    upload_res = client.post("/api/resume/upload", files={"file": ("portfolio.docx", resume_docx, "application/octet-stream")}).json()
    resume_id = upload_res["resume_id"]

    start_res = client.post("/api/interview/start", json={
        "name": "Audit Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "consent_agreed": True,
        "resume_id": resume_id,
        "total_questions": 2
    }).json()
    interview_id = start_res["interview_id"]
    q1 = start_res["first_question"]

    # Submit Turn 1 with response time
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": q1["question_id"],
        "candidate_answer": "JavaScript uses an event loop and microtask queue for asynchronous operations like Promises.",
        "response_time_seconds": 32
    }).json()

    # Query history
    hist_res = client.get(f"/api/interview/{interview_id}/history")
    assert hist_res.status_code == 200
    hist = hist_res.json()
    assert hist["total_turns"] >= 1
    t1 = hist["turns"][0]
    assert t1["response_time_seconds"] == 32
    assert "event loop" in t1["answer"]

    # Query report
    rep_res = client.get(f"/api/interview/{interview_id}/report")
    assert rep_res.status_code == 200
    rep = rep_res.json()
    assert rep["resume_info"] is not None
    assert rep["resume_info"]["filename"] == "portfolio.docx"
    assert "JavaScript" in rep["resume_info"]["detected_skills"]
    assert len(rep["turns"]) >= 1
    assert rep["turns"][0]["response_time_seconds"] == 32
