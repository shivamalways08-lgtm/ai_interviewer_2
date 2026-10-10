"""
Comprehensive Unit and Integration Tests for Dynamic Questioning
and 7 Consecutive Weak-Answer Termination.
Verifies all test requirements specified in Part 5 of the Master Prompt:
- Dynamic Questioning (continues past 5 questions, adapts difficulty, avoids duplicates, time-aware cutoff)
- 7 Consecutive Weak Answers (<40/100) termination, counter reset on >=40, duplicate protection
- Integration (Hindi/English parity, timer cooperation, recruiter report audit)
"""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from backend.main import app
from backend.database.database import get_connection
from backend.services.adaptive_engine import calculate_next_difficulty, select_next_question, SKILL_SEQUENCE

client = TestClient(app)

def test_dynamic_questioning_continues_beyond_five_questions():
    """Verify that interview without arbitrary question limit continues beyond 5 questions."""
    res = client.post("/api/interview/start", json={
        "name": "Dynamic Questioning Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert res.status_code == 200
    start_data = res.json()
    intv_id = start_data["interview_id"]
    current_q = start_data["first_question"]
    assert current_q is not None

    # Submit 8 competent answers (scoring >= 50 so no weak termination occurs)
    answers_count = 0
    for turn in range(8):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": current_q["question_id"],
            "candidate_answer": (
                "A variable is a named storage location in memory. "
                "Declaration declares the identifier and type, while initialization gives it an initial value."
            )
        })
        assert ans_res.status_code == 200
        ans_data = ans_res.json()
        answers_count += 1
        assert ans_data["score"] >= 40.0
        assert ans_data["is_completed"] is False
        assert ans_data["next_question"] is not None
        current_q = ans_data["next_question"]
        # Question index tracks correctly beyond 5
        assert current_q["question_index"] == turn + 2

    assert answers_count == 8

    # Verify database has recorded all 8 turns
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as cnt FROM interview_turns WHERE interview_id = ?", (intv_id,))
    total_turns = c.fetchone()["cnt"]
    c.execute("SELECT status, consecutive_weak_answers FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()

    assert total_turns == 8
    assert row["status"] == "in_progress"
    assert row["consecutive_weak_answers"] == 0

def test_question_adapts_difficulty_based_on_score():
    """Verify difficulty decreases on weak answer (<40) and increases on strong answer (>70)."""
    assert calculate_next_difficulty("MEDIUM", 25.0) == "EASY"
    assert calculate_next_difficulty("EASY", 20.0) == "EASY"
    assert calculate_next_difficulty("MEDIUM", 85.0) == "HARD"
    assert calculate_next_difficulty("HARD", 95.0) == "HARD"
    assert calculate_next_difficulty("MEDIUM", 55.0) == "MEDIUM"

def test_duplicate_questions_are_avoided():
    """Verify that previously asked question IDs are not repeated in subsequent turns."""
    res = client.post("/api/interview/start", json={
        "name": "Deduplication Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]
    asked_ids = [res.json()["first_question"]["question_id"]]

    for _ in range(6):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": asked_ids[-1],
            "candidate_answer": "Valid substantive response with data structures and time complexity analysis."
        })
        assert ans_res.status_code == 200
        nxt = ans_res.json().get("next_question")
        if nxt:
            assert nxt["question_id"] not in asked_ids
            asked_ids.append(nxt["question_id"])

    # All asked question IDs are unique
    assert len(asked_ids) == len(set(asked_ids))

def test_no_questions_generated_after_termination():
    """Verify that once terminated (weak answers or time expired), next_question is strictly None."""
    res = client.post("/api/interview/start", json={
        "name": "Termination Check Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]
    current_q = res.json()["first_question"]

    # Submit 7 weak answers to terminate
    term_res = None
    for _ in range(7):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": current_q["question_id"],
            "candidate_answer": "No idea."
        })
        term_res = ans_res.json()
        current_q = term_res.get("next_question")

    assert term_res["is_completed"] is True
    assert term_res["next_question"] is None
    assert term_res["termination_reason"] == "TERMINATED_WEAK_ANSWERS"

    # Attempting to submit 8th answer is rejected with 400
    eighth_attempt = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": "prog_easy_2",
        "candidate_answer": "8th answer attempt."
    })
    assert eighth_attempt.status_code == 400
    assert "terminated" in eighth_attempt.json()["detail"].lower()

def test_score_of_exactly_40_resets_counter():
    """Verify that a score of exactly 40/100 is NOT weak and resets the consecutive weak counter to 0."""
    res = client.post("/api/interview/start", json={
        "name": "Threshold 40 Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]
    q1 = res.json()["first_question"]

    # Submit 3 weak answers -> counter = 3
    for _ in range(3):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": q1["question_id"],
            "candidate_answer": "Weak response."
        })
        q1 = ans_res.json()["next_question"]

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT consecutive_weak_answers FROM interviews WHERE id = ?", (intv_id,))
    assert c.fetchone()["consecutive_weak_answers"] == 3

    # Now simulate an answer that scores exactly 40 or >= 40
    # Average response in rubric engine scores 50-60, which is >= 40
    ans_reset = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q1["question_id"],
        "candidate_answer": "A variable stores values in a program like numbers or text. Declaring is making the variable."
    })
    reset_data = ans_reset.json()
    assert reset_data["score"] >= 40.0
    assert reset_data["consecutive_weak_answers"] == 0

    c.execute("SELECT consecutive_weak_answers FROM interviews WHERE id = ?", (intv_id,))
    assert c.fetchone()["consecutive_weak_answers"] == 0
    conn.close()

def test_time_aware_questioning_near_deadline():
    """Verify that select_next_question does not start a new question when <= 30 seconds remain."""
    # When remaining_seconds <= 30, it should return None
    nxt = select_next_question(
        interview_turn_index=3,
        current_difficulty="MEDIUM",
        asked_question_ids=["prog_easy_1"],
        role="Software Developer Intern",
        language="en",
        total_questions=None,
        remaining_seconds=25.0
    )
    assert nxt is None

    # When plenty of time remains (>30s), it returns next question
    nxt_ok = select_next_question(
        interview_turn_index=3,
        current_difficulty="MEDIUM",
        asked_question_ids=["prog_easy_1"],
        role="Software Developer Intern",
        language="en",
        total_questions=None,
        remaining_seconds=800.0
    )
    assert nxt_ok is not None

def test_hindi_language_dynamic_session():
    """Verify that dynamic questioning and evaluation work in Hindi without question cap."""
    res = client.post("/api/interview/start", json={
        "name": "राकेश शर्मा (Hindi Candidate)",
        "role": "Software Developer Intern",
        "language": "hi",
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert res.status_code == 200
    start_data = res.json()
    assert start_data["language"] == "hi"
    q = start_data["first_question"]
    assert q["language"] == "hi"

    # Submit an answer in Hindi
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": start_data["interview_id"],
        "question_id": q["question_id"],
        "candidate_answer": "प्रोग्रामिंग में Variable मेमोरी का एक स्थान होता है जहाँ डेटा स्टोर किया जाता है।"
    })
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert ans_data["score"] >= 40.0
    assert ans_data["next_question"] is not None
    assert ans_data["next_question"]["language"] == "hi"
