"""
Unit and Integration Tests for IntervueAI Candidate Consent System.
Verifies:
1. Rejection of unconsented session initialization (403 Forbidden).
2. Rejection of partial consent (only 1 checkbox accepted).
3. Acceptance and accurate storage of full explicit consent (policy version, categories, timestamp, session ID).
4. Prevention of answer submission without valid session consent (403 Forbidden).
5. Explicit consent decline endpoint (/api/consent/decline) recording refusal without creating interview.
6. Consent verification endpoint (/api/interview/{id}/consent) returning complete audit record.
7. Language parity for both English and Hindi candidate consent.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_start_interview_rejected_without_consent():
    """Verify that starting an interview with no consent or consent=False is rejected with 403."""
    payload = {
        "name": "Unconsenting Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": False
    }
    res = client.post("/api/interview/start", json=payload)
    assert res.status_code == 403
    assert "consent is mandatory" in res.json()["detail"].lower()

def test_start_interview_rejected_with_partial_checkboxes():
    """Verify that accepting only one of the two mandatory checkboxes is rejected with 403."""
    # Only read_understood = True, skill_assessment_agreed = False
    payload1 = {
        "name": "Partial Candidate 1",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent": {
            "agreed": True,
            "read_understood": True,
            "skill_assessment_agreed": False,
            "policy_version": "v1.2"
        }
    }
    res1 = client.post("/api/interview/start", json=payload1)
    assert res1.status_code == 403
    assert "both acknowledgements must be accepted" in res1.json()["detail"].lower()

    # Only skill_assessment_agreed = True, read_understood = False
    payload2 = {
        "name": "Partial Candidate 2",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent": {
            "agreed": True,
            "read_understood": False,
            "skill_assessment_agreed": True,
            "policy_version": "v1.2"
        }
    }
    res2 = client.post("/api/interview/start", json=payload2)
    assert res2.status_code == 403

def test_start_interview_succeeds_with_explicit_consent():
    """Verify full consent succeeds, returns first question, and stores audit record."""
    payload = {
        "name": "Aarohi Gupta (Consented)",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent": {
            "agreed": True,
            "read_understood": True,
            "skill_assessment_agreed": True,
            "policy_version": "v1.2",
            "categories_disclosed": [
                "ai_question_generation",
                "response_text_analysis",
                "skill_rubric_scoring",
                "voice_transcription",
                "assistive_recruiter_reporting"
            ]
        }
    }
    res = client.post("/api/interview/start", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "interview_id" in data
    assert data["consent"]["status"] == "granted"
    assert data["consent"]["policy_version"] == "v1.2"
    assert "first_question" in data
    assert data["first_question"]["skill"] == "Programming Fundamentals"

    # Verify consent record via retrieval endpoint
    intv_id = data["interview_id"]
    verify_res = client.get(f"/api/interview/{intv_id}/consent")
    assert verify_res.status_code == 200
    vdata = verify_res.json()
    assert vdata["has_consent"] is True
    assert vdata["consent_status"] == "granted"
    assert vdata["policy_version"] == "v1.2"
    assert len(vdata["categories_disclosed"]) == 5
    assert vdata["agreed_at"] is not None

def test_hindi_consent_flow():
    """Verify that Hindi interview requests with Hindi consent metadata succeed."""
    payload = {
        "name": "राहुल कुमार",
        "role": "Software Developer Intern",
        "language": "hi",
        "interview_mode": "text",
        "consent": {
            "agreed": True,
            "read_understood": True,
            "skill_assessment_agreed": True,
            "policy_version": "v1.2",
            "categories_disclosed": [
                "ai_question_generation",
                "response_text_analysis",
                "skill_rubric_scoring",
                "voice_transcription",
                "assistive_recruiter_reporting"
            ]
        }
    }
    res = client.post("/api/interview/start", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["language"] == "hi"
    assert data["consent"]["status"] == "granted"
    assert "first_question" in data

def test_decline_consent_endpoint():
    """Verify that candidate decline is logged without creating an interview session."""
    payload = {
        "candidate_name": "Declining Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "policy_version": "v1.2"
    }
    res = client.post("/api/consent/decline", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["consent_status"] == "declined"
    assert "no interview will be started" in data["message"].lower()

def test_answer_submission_blocked_without_valid_session_consent():
    """Verify submitting an answer to an unconsented / fake interview is blocked with 403."""
    res = client.post("/api/interview/answer", json={
        "interview_id": "intv_fake_no_consent",
        "question_id": "prog_med_1",
        "candidate_answer": "Some answer"
    })
    # Must be 403 Forbidden or 404 Not Found, never 200
    assert res.status_code in [403, 404]

def test_consent_verification_for_unknown_session():
    """Verify that querying consent for an unknown session returns has_consent=False."""
    res = client.get("/api/interview/unknown_123/consent")
    assert res.status_code == 200
    data = res.json()
    assert data["has_consent"] is False
    assert data["consent_status"] == "not_found"
