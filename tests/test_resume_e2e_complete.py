import io
import json
import pytest
from fastapi.testclient import TestClient
from docx import Document

from backend.main import app
from backend.database.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    init_db()

def create_sample_pdf(text_lines):
    """Helper creating a valid in-memory PDF without external heavy libraries."""
    if isinstance(text_lines, str):
        text_lines = text_lines.split("\n")
    stream = "".join(f"BT /F1 12 Tf 72 {750 - i*25} Td ({line.replace('(', '').replace(')', '')}) Tj ET\n" for i, line in enumerate(text_lines))
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
0000000244 00000 n 
0000000318 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
{370 + stream_len}
%%EOF
"""
    return pdf.encode("latin1")

def create_sample_docx(content_text: str) -> bytes:
    """Helper creating a valid DOCX binary in memory."""
    doc = Document()
    for line in content_text.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.read()

def test_resume_valid_pdf_parsing_and_extraction():
    """Tests upload and text extraction from a valid PDF."""
    resume_text = (
        "ALEX RIVERA\n"
        "Full-Stack Software Engineer\n"
        "Skills: Python, React, TypeScript, Docker, PostgreSQL, Redis, FastAPI\n"
        "Projects:\n"
        "Distributed E-Commerce Gateway\n"
        "Engineered microservices using FastAPI, Redis, and PostgreSQL. Reduced latency.\n"
        "Real-time Collaborative Canvas\n"
        "Built interactive canvas using React, WebSockets, and Canvas API.\n"
        "Experience:\n"
        "Software Engineering Intern at CloudFlow Inc (2024)"
    )
    pdf_bytes = create_sample_pdf(resume_text)
    
    response = client.post(
        "/api/resume/upload",
        files={"file": ("alex_rivera_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["resume_id"].startswith("res_")
    assert data["file_type"] == "pdf"
    assert "Python" in data["languages_frameworks"] or "React" in data["languages_frameworks"]
    assert any("E-Commerce" in p["name"] or "Gateway" in p["name"] or "Canvas" in p["name"] for p in data["detected_projects"])

def test_resume_valid_docx_parsing_and_extraction():
    """Tests upload and extraction from a valid DOCX."""
    resume_text = (
        "PRIYA SHARMA\n"
        "Backend Developer\n"
        "Technical Stack: Java, Spring Boot, Go, MySQL, Kafka, AWS, Docker\n"
        "Projects:\n"
        "High-Throughput Notification Engine\n"
        "Built event-driven pipeline using Apache Kafka and Spring Boot to handle 10,000 notifications per second.\n"
        "Designed dead-letter queue recovery mechanisms."
    )
    docx_bytes = create_sample_docx(resume_text)
    
    response = client.post(
        "/api/resume/upload",
        files={"file": ("priya_sharma_resume.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_type"] == "docx"
    assert "Spring Boot" in data["languages_frameworks"] or "Java" in data["languages_frameworks"] or "Go" in data["languages_frameworks"]

def test_resume_invalid_file_type():
    """Tests rejection of unsupported file types."""
    response = client.post(
        "/api/resume/upload",
        files={"file": ("malicious.exe", b"MZ\x90\x00\x03\x00\x00\x00", "application/x-msdownload")}
    )
    assert response.status_code == 400
    assert "unsupported file format" in response.json()["detail"].lower()

def test_resume_empty_file():
    """Tests rejection of 0-byte empty files."""
    response = client.post(
        "/api/resume/upload",
        files={"file": ("empty_resume.pdf", b"", "application/pdf")}
    )
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()

def test_resume_corrupted_pdf():
    """Tests rejection of corrupted PDF files."""
    response = client.post(
        "/api/resume/upload",
        files={"file": ("corrupted.pdf", b"This is not a real PDF file contents", "application/pdf")}
    )
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "corrupt" in detail or "unreadable" in detail or "failed" in detail or "empty" in detail

def test_resume_corrupted_docx():
    """Tests rejection of corrupted DOCX files."""
    response = client.post(
        "/api/resume/upload",
        files={"file": ("corrupted.docx", b"PK\x03\x04corrupted_zip_payload", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    )
    assert response.status_code == 400
    detail = response.json()["detail"].lower()
    assert "zip" in detail or "corrupt" in detail or "failed" in detail or "unreadable" in detail

def test_resume_oversized_file():
    """Tests rejection of files exceeding the 5 MB limit."""
    huge_data = b"0" * (6 * 1024 * 1024)  # 6 MB
    response = client.post(
        "/api/resume/upload",
        files={"file": ("huge_resume.pdf", huge_data, "application/pdf")}
    )
    assert response.status_code in [400, 413]
    assert "exceeds" in response.json()["detail"].lower()

def test_personalized_turn0_question_generation():
    """Tests that Turn 0 generates a question personalized to the candidate's resume project."""
    resume_text = (
        "CANDIDATE: ROHAN MEHTA\n"
        "Skills: React, Node.js, Redux, PostgreSQL\n"
        "Projects:\n"
        "Student Management Portal\n"
        "Built responsive student portal using React and Redux with JWT authentication and state normalization."
    )
    pdf_bytes = create_sample_pdf(resume_text)
    up_res = client.post(
        "/api/resume/upload",
        files={"file": ("rohan_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert up_res.status_code == 200
    resume_id = up_res.json()["resume_id"]
    
    # Start interview with resume_id and explicit consent
    start_payload = {
        "name": "Rohan Mehta",
        "email": "rohan@example.com",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "consent": {
            "agreed": True,
            "skill_assessment_agreed": True,
            "read_understood": True,
            "policy_version": "v1.2",
            "categories_disclosed": ["ai_question_generation"]
        },
        "resume_id": resume_id
    }
    
    start_res = client.post("/api/interview/start", json=start_payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    first_q = start_data["first_question"]
    
    # Turn 0 should mention either the project or the candidate's core stack
    q_text = first_q["question_en"].lower()
    assert "student management" in q_text or "react" in q_text or "redux" in q_text or "portal" in q_text

def test_skip_resume_uses_standard_role_question():
    """Tests that skipping resume uses standard benchmark question and records no resume_id."""
    start_payload = {
        "name": "Sarah Connor",
        "email": "sarah@example.com",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "consent": {
            "agreed": True,
            "skill_assessment_agreed": True,
            "read_understood": True,
            "policy_version": "v1.2",
            "categories_disclosed": ["ai_question_generation"]
        },
        "resume_id": None
    }
    
    start_res = client.post("/api/interview/start", json=start_payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert start_data["resume_id"] is None
    first_q = start_data["first_question"]
    # First question should be standard Software Developer Intern Programming Fundamentals
    assert first_q["skill"] == "Programming Fundamentals"

def test_hindi_interview_with_resume_personalization():
    """Tests that Hindi interview personalizes questions in Hindi based on resume."""
    resume_text = (
        "VIKRAM SINGH\n"
        "Skills: Python, Django, PostgreSQL, Docker\n"
        "Projects:\n"
        "Hospital OPD Queue Manager\n"
        "Developed emergency room queue triage system using Django and Celery for real-time ticket dispatch."
    )
    pdf_bytes = create_sample_pdf(resume_text)
    up_res = client.post(
        "/api/resume/upload",
        files={"file": ("vikram_resume.pdf", pdf_bytes, "application/pdf")}
    )
    assert up_res.status_code == 200
    resume_id = up_res.json()["resume_id"]
    
    start_payload = {
        "name": "Vikram Singh",
        "email": "vikram@example.com",
        "role": "Software Developer Intern",
        "language": "hi",
        "interview_mode": "text",
        "consent_agreed": True,
        "consent": {
            "agreed": True,
            "skill_assessment_agreed": True,
            "read_understood": True,
            "policy_version": "v1.2",
            "categories_disclosed": ["ai_question_generation"]
        },
        "resume_id": resume_id
    }
    
    start_res = client.post("/api/interview/start", json=start_payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    first_q = start_data["first_question"]
    
    # Should contain Hindi text referencing the project
    q_hi = first_q.get("question_hi", "")
    assert len(q_hi) > 10
    assert ("Hospital" in q_hi or "OPD" in q_hi or "Django" in q_hi or "प्रोजेक्ट" in q_hi or "किए" in q_hi or "उपयोग" in q_hi)

def test_report_includes_resume_dossier_when_uploaded():
    """Tests that candidate report returns parsed resume dossier when resume was uploaded."""
    resume_text = (
        "ANANYA IYER\n"
        "Skills: Go, Kubernetes, Prometheus, Redis\n"
        "Projects:\n"
        "Cloud Observability Exporter\n"
        "Engineered telemetry metrics scraper with Prometheus exposition format."
    )
    pdf_bytes = create_sample_pdf(resume_text)
    up_res = client.post(
        "/api/resume/upload",
        files={"file": ("ananya_resume.pdf", pdf_bytes, "application/pdf")}
    )
    resume_id = up_res.json()["resume_id"]
    
    start_payload = {
        "name": "Ananya Iyer",
        "email": "ananya@example.com",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "consent": {
            "agreed": True,
            "skill_assessment_agreed": True,
            "read_understood": True,
            "policy_version": "v1.2",
            "categories_disclosed": ["ai_question_generation"]
        },
        "resume_id": resume_id
    }
    start_res = client.post("/api/interview/start", json=start_payload)
    intv_id = start_res.json()["interview_id"]
    
    # Answer 1 question
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": start_res.json()["first_question"]["question_id"],
        "candidate_answer": "I built the exporter in Go using the official prometheus client_golang package, registering custom Gauges and Counters.",
        "response_time_seconds": 35.0
    })
    assert ans_res.status_code == 200
    
    # Check report
    rep_res = client.get(f"/api/report/{intv_id}")
    assert rep_res.status_code == 200
    report = rep_res.json()
    assert report["resume_info"] is not None
    assert report["resume_info"]["filename"] == "ananya_resume.pdf"
    assert any("Observability" in p["name"] for p in report["resume_info"]["detected_projects"])
