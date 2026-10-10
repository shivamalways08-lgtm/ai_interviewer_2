"""
End-to-End Full Flow Integration Test for IntervueAI
Simulates candidate journey:
1. Candidate Setup & Consent
2. Question 1 (Medium) -> Strong Answer -> Adapts to Hard
3. Question 2 (Hard) -> Weak Answer -> Adapts to Medium
4. Question 3 (Medium) -> Strong Answer -> Adapts to Hard
5. Question 4 (Hard) -> Strong Answer -> Hard
6. Question 5 (Hard) -> Strong Answer -> Completes
7. Recruiter Report generation with verbatim evidence citations
8. Human recruiter decision: Shortlist & qualitative notes
"""

import os
import pytest
from fastapi.testclient import TestClient
from backend.main import app

def test_full_candidate_and_recruiter_journey():
    client = TestClient(app)

    # 1. Candidate Setup & Consent (Hindi candidate)
    start_payload = {
        "name": "Priya Sharma (E2E Test)",
        "role": "Software Developer Intern",
        "language": "hi",
        "interview_mode": "text",
        "consent_agreed": True,
        "total_questions": 5
    }
    res = client.post("/api/interview/start", json=start_payload)
    assert res.status_code == 200, res.text
    session_data = res.json()
    interview_id = session_data["interview_id"]
    candidate_id = session_data["candidate_id"]
    current_q = session_data["first_question"]

    assert interview_id.startswith("intv_")
    assert current_q["skill"] == "Programming Fundamentals"
    assert current_q["difficulty"] == "MEDIUM"

    # 2. Turn 1: Strong Answer in Hindi -> Expected adaptation to HARD
    t1_ans = "Stack मेमोरी LIFO सिद्धांत पर काम करती है और लोकल वेरिएबल्स के लिए होती है जो बहुत तेज़ है। Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है और इसे गारबेज कलेक्टर से फ्री किया जाता है।"
    ans1_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": current_q["question_id"],
        "candidate_answer": t1_ans
    })
    assert ans1_res.status_code == 200
    t1_eval = ans1_res.json()
    assert t1_eval["score"] >= 70
    assert t1_eval["next_difficulty"] == "HARD"
    assert t1_eval["is_completed"] is False
    current_q = t1_eval["next_question"]
    assert current_q["skill"] == "Problem Solving"
    assert current_q["difficulty"] == "HARD"

    # 3. Turn 2: Weak Answer on Hard question -> Expected adaptation down to MEDIUM
    t2_ans = "सर्च करके देख लेंगे।"
    ans2_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": current_q["question_id"],
        "candidate_answer": t2_ans
    })
    assert ans2_res.status_code == 200
    t2_eval = ans2_res.json()
    assert t2_eval["score"] <= 40
    assert t2_eval["next_difficulty"] == "MEDIUM"
    current_q = t2_eval["next_question"]
    assert current_q["skill"] == "Data Structures & Algorithms"
    assert current_q["difficulty"] == "MEDIUM"

    # 4. Turn 3: Strong Answer on DSA -> Adapts to HARD
    t3_ans = "Hash Collision तब होती है जब दो Keys का एक ही Hash इंडेक्स बने। Separate Chaining में हर बकेट में Linked List होती है और Linear Probing में अगला खाली स्लॉट ढूंढते हैं।"
    ans3_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": current_q["question_id"],
        "candidate_answer": t3_ans
    })
    assert ans3_res.status_code == 200
    t3_eval = ans3_res.json()
    assert t3_eval["score"] >= 70
    assert t3_eval["next_difficulty"] == "HARD"
    current_q = t3_eval["next_question"]
    assert current_q["skill"] == "Technical Understanding"
    assert current_q["difficulty"] == "HARD"

    # 5. Turn 4: Strong Answer on Technical -> Stays HARD
    t4_ans = "Monolith में पूरा ऍप्लिकेशन एक साथ डिप्लॉय होता है, जबकि Microservices में स्वतंत्र सर्विसेज होती हैं। Microservices में नेटवर्क लेटेंसी और डेटा कंसिस्टेंसी की चुनौती आती है जिसके लिए Saga पैटर्न इस्तेमाल होता है।"
    ans4_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": current_q["question_id"],
        "candidate_answer": t4_ans
    })
    assert ans4_res.status_code == 200
    t4_eval = ans4_res.json()
    assert t4_eval["score"] >= 70
    current_q = t4_eval["next_question"]
    assert current_q["skill"] == "Communication"

    # 6. Turn 5: Strong Answer on Communication -> Concludes interview
    t5_ans = "मैं कोड रिव्यु को व्यक्तिगत नहीं लेता और टीम की गुणवत्ता के लिए सुझाव का स्वागत करता हूँ। अगर कोई शंका हो तो लंबी कमेंट्स के बजाय 10 मिनट की कॉल पर बात करने का प्रस्ताव देता हूँ।"
    ans5_res = client.post("/api/interview/answer", json={
        "interview_id": interview_id,
        "question_id": current_q["question_id"],
        "candidate_answer": t5_ans
    })
    assert ans5_res.status_code == 200
    t5_eval = ans5_res.json()
    assert t5_eval["is_completed"] is True
    assert t5_eval["next_question"] is None

    # 7. Verify Synthesized Recruiter Report
    rep_res = client.get(f"/api/report/{interview_id}")
    assert rep_res.status_code == 200
    report = rep_res.json()
    assert report["candidate_name"] == "Priya Sharma (E2E Test)"
    assert len(report["skills_breakdown"]) == 5
    assert report["overall_score"] > 60
    assert "human recruiter" in report["human_decision_notice"].lower()

    # Verify that every skill has non-empty evidence
    for skill_item in report["skills_breakdown"]:
        assert skill_item["evidence"] != ""
        assert "score" in skill_item

    # 8. Human Recruiter Action: Record Final Decision
    decision_payload = {
        "interview_id": interview_id,
        "decision": "shortlist",
        "notes": "Demonstrated strong grasp of systems and collaborative communication. Recommend advancing to live coding."
    }
    dec_res = client.post("/api/recruiter/decision", json=decision_payload)
    assert dec_res.status_code == 200
    assert dec_res.json()["success"] is True

    # 9. Verify updated state in Recruiter Candidate Roster
    roster_res = client.get("/api/recruiter/candidates")
    assert roster_res.status_code == 200
    candidates = roster_res.json()["candidates"]
    matched = [c for c in candidates if c["interview_id"] == interview_id]
    assert len(matched) == 1
    assert matched[0]["recruiter_decision"] == "shortlist"
    assert matched[0]["status"] == "completed"
