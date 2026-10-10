"""
Test suite for Google Gemini API integration and AI Engine settings in IntervueAI
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.ai.gemini_service import validate_gemini_key

client = TestClient(app)

def test_ai_settings_endpoint():
    """Verify /api/settings/ai returns configured state and model list."""
    res = client.get("/api/settings/ai")
    assert res.status_code == 200
    data = res.json()
    assert "provider" in data
    assert "is_configured" in data
    assert "supported_models" in data
    assert "gemini-2.5-flash" in data["supported_models"]
    assert "status_message" in data

def test_gemini_test_key_endpoint_validation():
    """Verify testing an invalid key returns clear validation error rather than crashing."""
    res = client.post("/api/settings/test-key", json={"gemini_api_key": "invalid_test_key_xyz"})
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert "error" in data

def test_gemini_settings_reset():
    """Verify resetting API key safely switches back to offline rubric fallback."""
    res = client.post("/api/settings/ai", json={"gemini_api_key": "reset"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["provider"] == "rubric_fallback"

def test_interview_turn_evaluator_metadata():
    """Verify that submitting an answer includes evaluator metadata in response."""
    # 1. Start interview
    start_res = client.post("/api/interview/start", json={
        "name": "Integration Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "consent_agreed": True
    })
    assert start_res.status_code == 200
    start_data = start_res.json()
    intv_id = start_data["interview_id"]
    q_id = start_data["first_question"]["question_id"]

    # 2. Submit answer
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "Stack is LIFO and memory is allocated statically for local variables."
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert "evaluator" in ans_data
    assert ans_data["score"] > 0
    assert "evidence" in ans_data
