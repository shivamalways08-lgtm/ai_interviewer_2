"""
Unit and Integration Tests for 20-Minute Interview Timer and Consecutive Weak-Answer Termination.
Covers:
1. Feature 1: Authoritative 20-Minute Timer & Expiration Handling
2. Feature 2: Consecutive Weak-Answer Termination (7 consecutive < 40/100)
3. Feature 3 & 4: Dual Condition Enforcement, Atomicity & Resiliency
4. Feature 5: Candidate Report & Recruiter Dashboard Reporting
"""

from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
import pytest

from backend.main import app
from backend.database.database import get_connection

client = TestClient(app)

def test_timer_initialization_20_minutes():
    """Verify interview starts with authoritative 20-minute deadline (1200 seconds)."""
    res = client.post("/api/interview/start", json={
        "name": "Timer Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert res.status_code == 200
    data = res.json()
    assert "deadline_at" in data
    assert data["deadline_at"] is not None
    assert "remaining_seconds" in data
    # Should be close to 1200 seconds
    assert 1195.0 <= data["remaining_seconds"] <= 1200.0

    # Verify database record
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT deadline_at, status, consecutive_weak_answers FROM interviews WHERE id = ?", (data["interview_id"],))
    row = c.fetchone()
    conn.close()
    assert row["deadline_at"] is not None
    assert row["status"] == "in_progress"
    assert row["consecutive_weak_answers"] == 0

def test_timer_restore_on_refresh():
    """Verify refreshing interview state restores accurate remaining time from backend deadline."""
    res = client.post("/api/interview/start", json={
        "name": "Refresh Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]

    # Call get_interview_state (simulating page reload)
    state_res = client.get(f"/api/interview/{intv_id}")
    assert state_res.status_code == 200
    state = state_res.json()
    assert state["interview"]["id"] == intv_id
    assert state["remaining_seconds"] is not None
    assert 1190.0 <= state["remaining_seconds"] <= 1200.0
    assert state["interview"]["status"] == "in_progress"

def test_rejection_after_deadline_expired():
    """Verify answers submitted after the 20-minute deadline are rejected with 400 and marked TIME_EXPIRED."""
    res = client.post("/api/interview/start", json={
        "name": "Expired Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]
    q_id = res.json()["first_question"]["question_id"]

    # Manually backdate deadline_at to the past in the database
    past_dl = (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE interviews SET deadline_at = ? WHERE id = ?", (past_dl, intv_id))
    conn.commit()
    conn.close()

    # Attempt to submit an answer after deadline
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "This is an answer after the deadline expired."
    })
    assert ans_res.status_code == 400
    assert "expired" in ans_res.json()["detail"].lower()

    # Verify interview marked as TIME_EXPIRED
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status, termination_reason FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    assert row["status"] == "TIME_EXPIRED"
    assert row["termination_reason"] == "TIME_EXPIRED"

def test_explicit_expire_endpoint():
    """Verify POST /api/interview/{id}/expire closes session."""
    res = client.post("/api/interview/start", json={
        "name": "Expire Endpoint Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]

    exp_res = client.post(f"/api/interview/{intv_id}/expire")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["status"] == "TIME_EXPIRED"
    assert exp_data["termination_reason"] == "TIME_EXPIRED"

def test_six_weak_answers_do_not_terminate():
    """Verify 6 consecutive weak answers (<40/100) do NOT terminate the interview."""
    res = client.post("/api/interview/start", json={
        "name": "Six Weak Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "total_questions": 10
    })
    intv_id = res.json()["interview_id"]
    current_q = res.json()["first_question"]

    # Submit 6 weak answers
    for turn in range(6):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": current_q["question_id"],
            "candidate_answer": "I do not know this concept."  # scores < 40
        })
        assert ans_res.status_code == 200
        data = ans_res.json()
        assert data["score"] < 40.0
        assert data["consecutive_weak_answers"] == turn + 1
        assert data["is_completed"] is False
        assert data["termination_reason"] is None
        current_q = data["next_question"]
        assert current_q is not None

    # Verify database state after 6 answers
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status, consecutive_weak_answers, termination_reason FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    assert row["status"] == "in_progress"
    assert row["consecutive_weak_answers"] == 6
    assert row["termination_reason"] == "NORMAL"

def test_seventh_consecutive_weak_answer_terminates_immediately():
    """Verify 7th consecutive weak answer (<40/100) terminates session atomically."""
    res = client.post("/api/interview/start", json={
        "name": "Seven Weak Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "total_questions": 10
    })
    intv_id = res.json()["interview_id"]
    current_q = res.json()["first_question"]

    # Submit 7 consecutive weak answers
    last_res = None
    for turn in range(7):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": current_q["question_id"],
            "candidate_answer": "No idea about this topic."
        })
        assert ans_res.status_code == 200
        last_res = ans_res.json()
        if turn < 6:
            assert last_res["is_completed"] is False
            current_q = last_res["next_question"]

    # Check 7th answer response
    assert last_res["consecutive_weak_answers"] == 7
    assert last_res["is_completed"] is True
    assert last_res["next_question"] is None
    assert last_res["termination_reason"] == "TERMINATED_WEAK_ANSWERS"
    assert "7 consecutive answers scored below" in last_res["termination_message"]

    # Verify 7th answer and evidence are saved in DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) as count FROM interview_turns WHERE interview_id = ?", (intv_id,))
    turns_count = c.fetchone()["count"]
    c.execute("SELECT status, consecutive_weak_answers, termination_reason FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()

    assert turns_count == 7
    assert row["status"] == "TERMINATED_WEAK_ANSWERS"
    assert row["consecutive_weak_answers"] == 7
    assert row["termination_reason"] == "TERMINATED_WEAK_ANSWERS"

    # Attempting to submit another answer is rejected
    post_term_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": "prog_med_1",
        "candidate_answer": "Trying to answer again."
    })
    assert post_term_res.status_code == 400

def test_counter_resets_on_score_40_or_above():
    """Verify that a score of 40 or higher resets the consecutive_weak_answers counter to 0."""
    res = client.post("/api/interview/start", json={
        "name": "Reset Counter Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "total_questions": 10
    })
    intv_id = res.json()["interview_id"]
    current_q = res.json()["first_question"]

    # Turn 1: Weak answer -> counter becomes 1
    ans1 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": current_q["question_id"],
        "candidate_answer": "No idea."
    })
    assert ans1.json()["consecutive_weak_answers"] == 1
    current_q = ans1.json()["next_question"]

    # Turn 2: Weak answer -> counter becomes 2
    ans2 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": current_q["question_id"],
        "candidate_answer": "Dunno."
    })
    assert ans2.json()["consecutive_weak_answers"] == 2
    current_q = ans2.json()["next_question"]

    # Turn 3: Strong answer -> score >= 40 -> counter resets to 0
    ans3 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": current_q["question_id"],
        "candidate_answer": (
            "We use a Hash Map to store elements seen so far in O(N) time and O(1) average lookup, "
            "calculating complement target minus current number."
        )
    })
    assert ans3.json()["score"] >= 40.0
    assert ans3.json()["consecutive_weak_answers"] == 0
    current_q = ans3.json()["next_question"]

    # Turn 4: Weak answer -> counter restarts at 1
    ans4 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": current_q["question_id"],
        "candidate_answer": "Empty response."
    })
    assert ans4.json()["consecutive_weak_answers"] == 1

def test_duplicate_submission_does_not_increment_counter():
    """Verify duplicate submission of the same question is rejected and cannot inflate counter."""
    res = client.post("/api/interview/start", json={
        "name": "Duplicate Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    intv_id = res.json()["interview_id"]
    q_id = res.json()["first_question"]["question_id"]

    # First submission
    ans1 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "First weak answer."
    })
    assert ans1.status_code == 200
    assert ans1.json()["consecutive_weak_answers"] == 1

    # Duplicate submission of the same question
    ans2 = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "Duplicate submission attempt."
    })
    assert ans2.status_code == 400
    assert "already been submitted" in ans2.json()["detail"].lower()

    # Counter remains 1
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT consecutive_weak_answers FROM interviews WHERE id = ?", (intv_id,))
    count = c.fetchone()["consecutive_weak_answers"]
    conn.close()
    assert count == 1

def test_report_and_dashboard_reflect_termination_and_pending_skills():
    """Verify candidate report contains accurate duration, termination status, and pending skills."""
    res = client.post("/api/interview/start", json={
        "name": "Dossier Test Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True,
        "total_questions": 10
    })
    intv_id = res.json()["interview_id"]
    current_q = res.json()["first_question"]

    # Submit 7 weak answers to trigger termination
    for _ in range(7):
        ans_res = client.post("/api/interview/answer", json={
            "interview_id": intv_id,
            "question_id": current_q["question_id"],
            "candidate_answer": "I do not know."
        })
        current_q = ans_res.json().get("next_question")

    # Fetch report
    rep_res = client.get(f"/api/report/{intv_id}")
    assert rep_res.status_code == 200
    report = rep_res.json()

    assert report["termination_reason"] == "TERMINATED_WEAK_ANSWERS"
    assert "Terminated (7 Consecutive Weak Answers" in report["termination_status_display"]
    assert report["questions_answered"] == 7
    assert report["consecutive_weak_answers"] == 7
    assert "duration_formatted" in report
    assert "pending_skills" in report
    # All planned skills covered or listed under pending without fabrication
    assert isinstance(report["skills_breakdown"], list)

    # Check recruiter candidates roster
    rec_res = client.get("/api/recruiter/candidates")
    assert rec_res.status_code == 200
    cands = rec_res.json()["candidates"]
    matched = next((c for c in cands if c["interview_id"] == intv_id), None)
    assert matched is not None
    assert matched["termination_reason"] == "TERMINATED_WEAK_ANSWERS"
    assert matched["consecutive_weak_answers"] == 7
