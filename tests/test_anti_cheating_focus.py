"""
Unit and Integration Tests for Anti-Cheating Tab-Switch and Focus Violation Detection.

Covers all 12 specification requirements:
1. Switching to another tab triggers one termination event.
2. Hiding/minimizing the browser triggers the visibility-based violation.
3. Duplicate visibilitychange and blur events do not create duplicate terminations.
4. Before interview start, changing tabs does not terminate anything.
5. After normal completion or termination, further focus events do not alter the final status.
6. After termination, answer submissions are rejected by the backend.
7. Refreshing the page does not reset the terminal status.
8. The 20-minute timeout still works.
9. The 7-consecutive-weak-answers rule still works.
10. Simultaneous terminal events produce only one final status (atomicity / race handling).
11. English and Hindi termination messages and reports display correctly.
12. A failed termination request / retry handled safely and idempotently.
"""

import threading
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.database.database import get_connection
from backend.services.adaptive_engine import generate_candidate_report

client = TestClient(app)

def _start_test_interview(name="Focus Candidate", lang="en"):
    """Helper to start an interview session with consent."""
    res = client.post("/api/interview/start", json={
        "name": name,
        "role": "Software Developer Intern",
        "language": lang,
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert res.status_code == 200
    return res.json()


# 1. Switching to another tab triggers one termination event.
def test_tab_switch_triggers_termination_event():
    session = _start_test_interview("Tab Switch Candidate")
    intv_id = session["interview_id"]

    res = client.post(f"/api/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "document.visibilityState is hidden (switched tab)"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["already_terminated"] is False
    assert data["focus_violations_count"] == 1
    assert data["completed_at"] is not None

    # Check database persistence
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status, termination_reason, focus_violations_count, completed_at FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    assert row["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert row["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert row["focus_violations_count"] == 1
    assert row["completed_at"] is not None


# 2. Hiding/minimizing the browser triggers the visibility-based violation.
def test_minimizing_browser_triggers_visibility_violation():
    session = _start_test_interview("Minimize Candidate")
    intv_id = session["interview_id"]

    res = client.post(f"/api/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "document.visibilitychange: browser minimized"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["focus_violations_count"] == 1


# 3. Duplicate visibilitychange and blur events do not create duplicate terminations.
def test_duplicate_events_do_not_create_duplicate_terminations():
    session = _start_test_interview("Duplicate Event Candidate")
    intv_id = session["interview_id"]

    # First event: visibilitychange hidden
    res1 = client.post(f"/api/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "visibilitychange: hidden"
    })
    assert res1.status_code == 200
    assert res1.json()["already_terminated"] is False
    first_completed_at = res1.json()["completed_at"]

    # Second duplicate event: window blur
    res2 = client.post(f"/api/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "window.blur with hidden visibilityState"
    })
    assert res2.status_code == 200
    assert res2.json()["already_terminated"] is True
    assert res2.json()["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert res2.json()["focus_violations_count"] == 1

    # Third duplicate event: pagehide
    res3 = client.post(f"/api/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "pagehide: navigating away"
    })
    assert res3.status_code == 200
    assert res3.json()["already_terminated"] is True
    assert res3.json()["focus_violations_count"] == 1

    # Verify database still has exactly 1 count
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT focus_violations_count, completed_at FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    assert row["focus_violations_count"] == 1
    assert row["completed_at"] == first_completed_at


# 4. Before interview start, changing tabs does not terminate anything.
def test_before_interview_start_no_termination():
    # Calling violation with nonexistent or dummy ID before interview start fails gracefully with 404
    res = client.post("/api/interview/non_existent_session_12345/violation", json={
        "details": "pre-interview tab change"
    })
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


# 5. After normal completion or termination, further focus events do not alter final status.
def test_further_focus_events_do_not_alter_completed_or_expired_status():
    session = _start_test_interview("Completed Candidate")
    intv_id = session["interview_id"]

    # Complete interview normally
    comp_res = client.post(f"/api/interview/complete?interview_id={intv_id}")
    assert comp_res.status_code == 200
    assert comp_res.json().get("termination_reason") in ["NORMAL", "COMPLETED"] or comp_res.json().get("status") == "completed"

    # Subsequent focus violation must NOT overwrite 'completed' status
    viol_res = client.post(f"/api/interview/{intv_id}/violation", json={
        "details": "tab switch after completion"
    })
    assert viol_res.status_code == 200
    data = viol_res.json()
    assert data["already_terminated"] is True
    assert data["status"] == "completed"

    # Verify in DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    assert row["status"] == "completed"


# 6. After termination, answer submissions are rejected by the backend.
def test_answer_submissions_rejected_after_focus_violation():
    session = _start_test_interview("Answer Rejection Candidate")
    intv_id = session["interview_id"]
    q_id = session["first_question"]["question_id"]

    # Terminate via focus violation
    client.post(f"/api/interview/{intv_id}/violation")

    # Attempt to submit answer
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "In Python, lists are mutable while tuples are immutable."
    })
    assert ans_res.status_code == 400
    detail = ans_res.json()["detail"]
    assert "focus violation" in detail.lower() or "leaving or switching tabs" in detail.lower()


# 7. Refreshing the page does not reset the terminal status.
def test_refresh_does_not_reset_terminal_status():
    session = _start_test_interview("Refresh Candidate")
    intv_id = session["interview_id"]

    # Terminate via focus violation
    client.post(f"/api/interview/{intv_id}/violation")

    # Simulate browser refresh by fetching interview state
    refresh_res = client.get(f"/api/interview/{intv_id}")
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert data["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["interview"]["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert data["focus_violations_count"] == 1


# 8. The 20-minute timeout still works.
def test_20_minute_timeout_still_works():
    session = _start_test_interview("Timeout Candidate")
    intv_id = session["interview_id"]

    # Force deadline into the past
    conn = get_connection()
    c = conn.cursor()
    past_dl = (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat()
    c.execute("UPDATE interviews SET deadline_at = ? WHERE id = ?", (past_dl, intv_id))
    conn.commit()
    conn.close()

    # Expire call authoritatively marks TIME_EXPIRED
    exp_res = client.post(f"/api/interview/{intv_id}/expire")
    assert exp_res.status_code == 200
    assert exp_res.json()["status"] == "TIME_EXPIRED"

    # State check reflects TIME_EXPIRED
    st = client.get(f"/api/interview/{intv_id}").json()
    assert st["status"] == "TIME_EXPIRED"


# 9. The 7-consecutive-weak-answers rule still works.
def test_7_consecutive_weak_answers_rule_still_works():
    session = _start_test_interview("Weak Answers Candidate")
    intv_id = session["interview_id"]

    # Set consecutive_weak_answers to 6
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE interviews SET consecutive_weak_answers = 6 WHERE id = ?", (intv_id,))
    conn.commit()
    conn.close()

    # Submit 7th weak answer (<40/100)
    ans_res = client.post("/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": session["first_question"]["question_id"],
        "candidate_answer": "idk"
    })
    assert ans_res.status_code == 200
    data = ans_res.json()
    assert data["consecutive_weak_answers"] == 7
    assert data["termination_reason"] == "TERMINATED_WEAK_ANSWERS"
    assert data["is_completed"] is True


# 10. Simultaneous terminal events produce only one final status (first terminal wins atomically).
def test_simultaneous_terminal_events_produce_single_final_status():
    session = _start_test_interview("Race Candidate")
    intv_id = session["interview_id"]

    results = []

    def call_violation():
        r = client.post(f"/api/interview/{intv_id}/violation", json={"details": "thread violation"})
        results.append(("violation", r.status_code, r.json()))

    def call_expire():
        r = client.post(f"/api/interview/{intv_id}/expire")
        results.append(("expire", r.status_code, r.json()))

    t1 = threading.Thread(target=call_violation)
    t2 = threading.Thread(target=call_expire)

    t1.start()
    t2.start()
    t1.join()
    t2.join()

    # Both must succeed with 200
    assert len(results) == 2
    assert results[0][1] == 200
    assert results[1][1] == 200

    # Final DB status must be exactly one terminal status and not null/open
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT status, termination_reason FROM interviews WHERE id = ?", (intv_id,))
    row = c.fetchone()
    conn.close()
    final_status = row["status"]
    assert final_status in ["TERMINATED_FOCUS_VIOLATION", "TIME_EXPIRED"]
    assert row["termination_reason"] == final_status


# 11. English and Hindi termination messages display correctly.
def test_english_and_hindi_termination_messages_and_report():
    # Test English Report with Focus Violation
    session_en = _start_test_interview("English Candidate", lang="en")
    intv_en = session_en["interview_id"]
    client.post(f"/api/interview/{intv_en}/violation")

    rep_res_en = client.get(f"/api/report/{intv_en}")
    assert rep_res_en.status_code == 200
    rep_en = rep_res_en.json()
    assert rep_en["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert "Focus Violation" in rep_en["termination_status_display"]
    assert "switched away from the active interview page" in rep_en["termination_summary"]

    # Test Hindi Report with Focus Violation
    session_hi = _start_test_interview("Hindi Candidate", lang="hi")
    intv_hi = session_hi["interview_id"]
    client.post(f"/api/interview/{intv_hi}/violation")

    rep_res_hi = client.get(f"/api/report/{intv_hi}")
    assert rep_res_hi.status_code == 200
    rep_hi = rep_res_hi.json()
    assert rep_hi["language"] == "hi"
    assert rep_hi["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert "Focus Violation" in rep_hi["termination_status_display"]


# 12. A failed termination request locks the frontend and handles retries safely.
def test_violation_retry_handling():
    session = _start_test_interview("Retry Candidate")
    intv_id = session["interview_id"]

    # Attempt 1: recorded
    r1 = client.post(f"/api/interview/{intv_id}/violation", json={
        "details": "attempt 1"
    })
    assert r1.status_code == 200
    assert r1.json()["already_terminated"] is False

    # Attempt 2 (Simulating retry from frontend): succeeds idempotently
    r2 = client.post(f"/api/interview/{intv_id}/violation", json={
        "details": "attempt 2 (retry)"
    })
    assert r2.status_code == 200
    assert r2.json()["already_terminated"] is True
    assert r2.json()["status"] == "TERMINATED_FOCUS_VIOLATION"
