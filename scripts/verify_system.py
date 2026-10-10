"""
System Verification Script for IntervueAI
Tests:
1. Health & Server Connectivity (Backend port 8000 & Frontend port 5173)
2. Question Bank & Roles
3. End-to-End English Adaptive Interview
4. Recruiter Report & Verbatim Evidence Extraction
5. Human Recruiter Decision & Notes
6. Multilingual Hindi Interview & Parity
"""

import sys
import httpx

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

client = httpx.Client(timeout=10.0)

def main():
    print("==================================================")
    print(" IntervueAI Comprehensive System Verification")
    print("==================================================")

    # 1. Health & Server connectivity
    print("\n[1/6] Verifying Server Endpoints...")
    b_health = client.get("http://127.0.0.1:8000/api/health")
    assert b_health.status_code == 200, "Backend /api/health returned non-200"
    print(f"  ✓ FastAPI Backend (127.0.0.1:8000): HEALTHY -> {b_health.json()}")

    f_home = client.get("http://127.0.0.1:5173/")
    assert f_home.status_code == 200, "Frontend returned non-200"
    print(f"  ✓ React Vite Frontend (localhost:5173): ONLINE -> Status {f_home.status_code}")

    f_proxy = client.get("http://127.0.0.1:5173/api/health")
    assert f_proxy.status_code == 200, "Vite Proxy to FastAPI returned non-200"
    print(f"  ✓ Frontend /api Proxy: FUNCTIONAL -> Status {f_proxy.status_code}")

    # 2. Roles & Question Bank
    print("\n[2/6] Verifying Roles & Question Bank Catalog...")
    roles = client.get("http://127.0.0.1:8000/api/roles").json()
    role_titles = [r["title"] for r in roles["roles"]]
    print(f"  ✓ Configured Roles: {role_titles}")
    assert "Software Developer Intern" in role_titles

    questions = client.get("http://127.0.0.1:8000/api/questions").json()
    q_count = questions["total_questions"]
    print(f"  ✓ Total Questions Loaded in Bank: {q_count}")
    assert q_count >= 25, "Question bank catalog is too small"

    # 3. Full Adaptive Interview Lifecycle in English
    print("\n[3/6] Simulating English Adaptive Interview Lifecycle...")
    start_res = client.post("http://127.0.0.1:8000/api/interview/start", json={
        "name": "Live Verification Candidate (EN)",
        "role": "Software Developer Intern",
        "language": "en",
        "interview_mode": "text",
        "consent_agreed": True
    })
    assert start_res.status_code == 200
    session = start_res.json()
    intv_id = session["interview_id"]
    q = session["first_question"]
    print(f"  ✓ Session Created: {intv_id}")
    print(f"  ✓ Q1: {q['skill']} | Initial Difficulty: {q['difficulty']}")
    assert q["difficulty"] == "MEDIUM"

    # Turn 1: Strong Answer -> Scale to HARD
    a1 = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q["question_id"],
        "candidate_answer": "Stack memory is used for static allocation and local function execution frames following LIFO. Heap memory is used for dynamic memory allocation where objects survive beyond a single function, requiring garbage collection."
    }).json()
    print(f"  ✓ Turn 1 Evaluated: Score {a1['score']}/100 -> Next Difficulty: {a1['next_difficulty']}")
    assert a1["score"] >= 75
    assert a1["next_difficulty"] == "HARD"
    q = a1["next_question"]

    # Turn 2: Weak Answer -> Scale down to MEDIUM
    a2 = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q["question_id"],
        "candidate_answer": "I will loop through everything."
    }).json()
    print(f"  ✓ Turn 2 Evaluated: Score {a2['score']}/100 -> Next Difficulty: {a2['next_difficulty']}")
    assert a2["score"] <= 45
    assert a2["next_difficulty"] == "MEDIUM"
    q = a2["next_question"]

    # Turn 3: Strong Answer -> Scale back to HARD
    a3 = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q["question_id"],
        "candidate_answer": "A collision occurs when two keys hash to the same bucket index. Separate Chaining uses a linked list at each bucket, while Open Addressing probes subsequent slots."
    }).json()
    print(f"  ✓ Turn 3 Evaluated: Score {a3['score']}/100 -> Next Difficulty: {a3['next_difficulty']}")
    assert a3["score"] >= 75
    assert a3["next_difficulty"] == "HARD"
    q = a3["next_question"]

    # Turn 4: Strong Answer -> Stays HARD
    a4 = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q["question_id"],
        "candidate_answer": "A monolith deploys as a single unit, whereas microservices split into independent bounded domains. Challenges include network latency, partial failures, and CAP theorem consistency."
    }).json()
    print(f"  ✓ Turn 4 Evaluated: Score {a4['score']}/100 -> Next Difficulty: {a4['next_difficulty']}")
    assert a4["score"] >= 75
    q = a4["next_question"]

    # Turn 5: Strong Answer -> Interview Completes
    a5 = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": intv_id,
        "question_id": q["question_id"],
        "candidate_answer": "I separate ego from code and assume positive intent. If comments disagree, I propose a quick 10-minute sync to align on the best solution for the team."
    }).json()
    print(f"  ✓ Turn 5 Evaluated: Score {a5['score']}/100 -> Completed: {a5['is_completed']}")
    assert a5["is_completed"] is True

    # 4. Report & Evidence Extraction
    print("\n[4/6] Verifying Recruiter Dossier & Verbatim Evidence...")
    report = client.get(f"http://127.0.0.1:8000/api/report/{intv_id}").json()
    print(f"  ✓ Overall Score: {report['overall_score']}/100")
    print(f"  ✓ AI Recommendation: {report['ai_recommendation']}")
    print(f"  ✓ Human Governance Notice: {report['human_decision_notice']}")
    for skill_data in report["skills_breakdown"]:
        skill_name = skill_data["skill"]
        skill_score = skill_data["score"]
        evidence_snippet = skill_data["evidence"][:45]
        print(f"    - {skill_name}: {skill_score} | Evidence: \"{evidence_snippet}...\"")
        assert len(skill_data["evidence"]) > 0, f"Evidence for {skill_name} was empty"

    # 5. Human Recruiter Action
    print("\n[5/6] Verifying Human Recruiter Action & Persistence...")
    decision_res = client.post("http://127.0.0.1:8000/api/recruiter/decision", json={
        "interview_id": intv_id,
        "decision": "shortlist",
        "notes": "Verified through automated live pipeline. Strong systems grasp."
    }).json()
    assert decision_res["success"] is True
    print(f"  ✓ Recruiter Decision Saved: {decision_res['decision'].upper()}")

    # Verify state in roster
    roster = client.get("http://127.0.0.1:8000/api/recruiter/candidates").json()
    matched = [c for c in roster["candidates"] if c["interview_id"] == intv_id]
    assert len(matched) == 1
    assert matched[0]["recruiter_decision"] == "shortlist"
    print(f"  ✓ Roster Update Confirmed: Decision={matched[0]['recruiter_decision']}, Status={matched[0]['status']}")

    # 6. Multilingual Parity in Hindi
    print("\n[6/6] Verifying Multilingual Hindi Interview & Equal Evaluation...")
    hi_start = client.post("http://127.0.0.1:8000/api/interview/start", json={
        "name": "Live Verification Candidate (HI)",
        "role": "Software Developer Intern",
        "language": "hi",
        "interview_mode": "text",
        "consent_agreed": True
    }).json()
    hi_q_text = hi_start["first_question"]["question_text"]
    print(f"  ✓ Hindi Question 1: \"{hi_q_text[:50]}...\"")

    hi_ans = client.post("http://127.0.0.1:8000/api/interview/answer", json={
        "interview_id": hi_start["interview_id"],
        "question_id": hi_start["first_question"]["question_id"],
        "candidate_answer": "Stack मेमोरी LIFO सिद्धांत पर काम करती है और लोकल वेरिएबल्स के लिए होती है जो बहुत तेज़ है। Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है और इसे गारबेज कलेक्टर से फ्री किया जाता है।"
    }).json()
    print(f"  ✓ Hindi Answer Score: {hi_ans['score']}/100 | Next Diff: {hi_ans['next_difficulty']}")
    assert hi_ans["score"] >= 70, "Hindi answer failed parity evaluation"
    assert hi_ans["next_difficulty"] == "HARD", "Hindi answer difficulty adaptation failed"
    print(f"  ✓ Hindi Verbatim Evidence: \"{hi_ans['evidence'][:50]}...\"")

    print("\n==================================================")
    print(" ✅ ALL 6 VERIFICATION PHASES PASSED WITH 100% SUCCESS!")
    print(" The IntervueAI platform is completely runnable and operational.")
    print("==================================================")

if __name__ == "__main__":
    main()
