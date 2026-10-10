import requests
import json

BASE = "http://127.0.0.1:8000/api"

def test_live_server():
    print("1. Checking server health...")
    r = requests.get(f"{BASE}/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("   Health check OK:", r.json())

    print("2. Starting interview with consent...")
    r = requests.post(f"{BASE}/interview/start", json={
        "name": "Live Anti-Cheat Candidate",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert r.status_code == 200, f"Start failed: {r.text}"
    session = r.json()
    intv_id = session["interview_id"]
    print("   Started session:", intv_id)

    print("3. Submitting 1 valid answer before violation...")
    q_id = session["first_question"]["question_id"]
    r = requests.post(f"{BASE}/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q_id,
        "candidate_answer": "In Python, lists are mutable dynamic arrays, whereas tuples are immutable fixed sequences."
    })
    assert r.status_code == 200, f"Answer failed: {r.text}"
    ans_data = r.json()
    print("   Answer evaluated successfully. Score:", ans_data["score"], "Next Q:", ans_data.get("next_question", {}).get("skill"))

    print("4. Triggering tab-switch focus violation...")
    r = requests.post(f"{BASE}/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "User switched browser tab (visibilityState hidden)"
    })
    assert r.status_code == 200, f"Violation failed: {r.text}"
    viol_data = r.json()
    print("   Violation recorded:", viol_data)
    assert viol_data["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert viol_data["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert viol_data["already_terminated"] is False

    print("5. Submitting second duplicate violation event (window.blur)...")
    r = requests.post(f"{BASE}/interview/{intv_id}/violation", json={
        "interview_id": intv_id,
        "reason": "TERMINATED_FOCUS_VIOLATION",
        "details": "window.blur duplicate event"
    })
    assert r.status_code == 200
    dup_data = r.json()
    print("   Duplicate violation response:", dup_data)
    assert dup_data["already_terminated"] is True
    assert dup_data["status"] == "TERMINATED_FOCUS_VIOLATION"
    assert dup_data["focus_violations_count"] == 1

    print("6. Verifying subsequent answer submission is REJECTED with 400...")
    r = requests.post(f"{BASE}/interview/answer", json={
        "interview_id": intv_id,
        "question_id": ans_data.get("next_question", {}).get("question_id", "algo_01"),
        "candidate_answer": "Trying to answer after focus violation..."
    })
    print("   Status code after termination:", r.status_code, "Detail:", r.text)
    assert r.status_code == 400
    assert "focus violation" in r.text.lower() or "leaving or switching tabs" in r.text.lower()

    print("7. Verifying report generation preserves prior answer, scores, and records violation reason...")
    r = requests.get(f"{BASE}/report/{intv_id}")
    assert r.status_code == 200
    rep = r.json()
    print("   Report generated successfully:")
    print("   - Candidate:", rep["candidate_name"])
    print("   - Questions Answered:", rep["questions_answered"])
    print("   - Termination Reason:", rep["termination_reason"])
    print("   - Termination Display:", rep["termination_status_display"])
    print("   - Termination Summary:", rep["termination_summary"])
    assert rep["termination_reason"] == "TERMINATED_FOCUS_VIOLATION"
    assert rep["questions_answered"] == 1
    assert len(rep["turns"]) == 1

    print("\n>>> ALL LIVE VERIFICATION CHECKS PASSED PERFECTLY! <<<")

if __name__ == "__main__":
    test_live_server()
