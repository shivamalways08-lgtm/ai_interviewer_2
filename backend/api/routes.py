"""
API Endpoints for IntervueAI
Handles interview lifecycle, answers, evaluation, recruiter dashboard, and seed demo data.
"""

import uuid
import json
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

import os
import logging
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from backend.models.schemas import (
    StartInterviewRequest,
    SubmitAnswerRequest,
    StandaloneEvaluateRequest,
    RecruiterDecisionRequest,
    QuestionResponse,
    AnswerEvaluationResponse,
    GeminiKeyRequest,
    AiSettingsResponse,
    ConsentPayload,
    DeclineConsentRequest,
    ConsentVerificationResponse,
    FocusViolationRequest,
    ResumeAnalysisResponse
)
from backend.database.database import get_connection, init_db
from backend.data.question_bank import (
    QUESTION_BANK,
    get_question_by_id,
    get_questions_by_role
)
from backend.ai.evaluation_engine import evaluate_answer, sanitize_and_check_fairness
from backend.ai.gemini_service import (
    validate_gemini_key,
    save_gemini_key_to_env,
    GEMINI_MODELS
)
from backend.services.adaptive_engine import (
    select_next_question,
    calculate_next_difficulty,
    generate_candidate_report,
    SKILL_SEQUENCE
)
from backend.services.resume_parser import (
    parse_and_analyze_resume,
    MAX_FILE_SIZE_BYTES
)

logger = logging.getLogger(__name__)

def calculate_remaining_seconds(deadline_at: Optional[Any]) -> float:
    """Calculates remaining seconds before authoritative deadline in UTC."""
    if not deadline_at:
        return 0.0
    try:
        d_str = str(deadline_at).replace("Z", "+00:00")
        deadline = datetime.fromisoformat(d_str)
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        return max(0.0, (deadline - now).total_seconds())
    except Exception:
        return 0.0

router = APIRouter(prefix="/api")

@router.get("/roles")
def get_roles():
    """Returns available job roles and skill competencies."""
    return {
        "roles": [
            {
                "id": "swe_intern",
                "title": "Software Developer Intern",
                "active": True,
                "skills": SKILL_SEQUENCE,
                "description": "First-round technical assessment testing fundamentals, problem solving, data structures, technical design, and collaboration."
            },
            {
                "id": "data_analyst",
                "title": "Data Analyst (Coming Soon)",
                "active": False,
                "skills": ["SQL", "Statistical Analysis", "Data Wrangling", "Visualization", "Business Logic"],
                "description": "Evaluates analytical queries, metrics definition, and data storytelling."
            },
            {
                "id": "hardware_intern",
                "title": "Electronics Engineer (Coming Soon)",
                "active": False,
                "skills": ["Circuit Analysis", "Microcontrollers", "Embedded C", "Troubleshooting", "Hardware Design"],
                "description": "Evaluates embedded systems, schematic reading, and testing."
            }
        ]
    }

@router.get("/questions")
def get_questions():
    """Lists question bank catalog."""
    return {
        "total_questions": len(QUESTION_BANK),
        "questions": QUESTION_BANK
    }

@router.get("/settings/ai", response_model=AiSettingsResponse)
def get_ai_settings():
    """Returns current AI provider status and model configuration."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    is_conf = bool(key)
    masked = f"{key[:6]}...{key[-4:]}" if (key and len(key) > 10) else (key[:3] + "..." if key else None)
    
    return AiSettingsResponse(
        provider="gemini" if is_conf else "rubric_fallback",
        is_configured=is_conf,
        masked_key=masked,
        active_model="gemini-2.5-flash" if is_conf else "rubric_engine",
        supported_models=GEMINI_MODELS,
        status_message="Google Gemini 2.5 Flash active for real-time multilingual AI evaluation." if is_conf else "Running in offline deterministic rubric mode (100% functional without API key)."
    )

@router.post("/settings/ai")
def configure_gemini_key(payload: GeminiKeyRequest):
    """Configures or resets the Google Gemini API key with immediate validation."""
    key = payload.gemini_api_key.strip()
    if not key or key.lower() == "reset":
        os.environ["GEMINI_API_KEY"] = ""
        save_gemini_key_to_env("")
        return {
            "success": True,
            "provider": "rubric_fallback",
            "message": "Switched to offline deterministic rubric engine mode."
        }
    
    # Validate key against Google Gemini API
    test_result = validate_gemini_key(key)
    if not test_result.get("valid"):
        return {
            "success": False,
            "error": test_result.get("error", "Failed to validate Gemini API key."),
            "message": "Gemini key verification failed. Please check your key from Google AI Studio."
        }
    
    # Save to runtime environment and .env
    save_gemini_key_to_env(key)
    return {
        "success": True,
        "provider": "gemini",
        "model": test_result.get("model", "gemini-2.5-flash"),
        "message": test_result.get("message", "Gemini API key verified and active!")
    }

@router.post("/settings/test-key")
def test_gemini_key(payload: GeminiKeyRequest):
    """Tests a Gemini API key without saving it."""
    return validate_gemini_key(payload.gemini_api_key)

@router.post("/resume/upload", response_model=ResumeAnalysisResponse)
@router.post("/resume/analyze", response_model=ResumeAnalysisResponse)
async def upload_resume(file: UploadFile = File(...)):
    """
    Accepts PDF or DOCX file upload, extracts text, validates size/extension,
    parses skills/projects via Gemini AI or deterministic fallback,
    and returns structured profile information for candidate preview.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No resume file uploaded.")

    filename = file.filename
    ext = os.path.splitext(filename)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only PDF and DOCX files are supported."
        )

    file_bytes = await file.read()
    if not file_bytes or len(file_bytes.strip()) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum allowed size of 5MB ({len(file_bytes) / (1024*1024):.2f}MB uploaded)."
        )

    try:
        parsed_data = parse_and_analyze_resume(file_bytes, filename)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error parsing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract text from resume: {str(e)}")

    resume_id = f"res_{uuid.uuid4().hex[:12]}"
    file_type = "pdf" if ext == ".pdf" else "docx"

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumes (
            id, filename, file_size, file_type, extracted_text,
            parsed_data_json, parser_type, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        resume_id,
        filename,
        len(file_bytes),
        file_type,
        f"Length: {parsed_data.get('raw_text_length', 0)} chars",
        json.dumps(parsed_data),
        parsed_data.get("parser", "deterministic_fallback")
    ))
    conn.commit()
    conn.close()

    return ResumeAnalysisResponse(
        success=True,
        resume_id=resume_id,
        filename=filename,
        file_size=len(file_bytes),
        file_type=file_type,
        parser=parsed_data.get("parser", "deterministic_fallback"),
        is_fallback=parsed_data.get("is_fallback", False),
        detected_skills=parsed_data.get("detected_skills", []),
        languages_frameworks=parsed_data.get("languages_frameworks", []),
        tools_technologies=parsed_data.get("tools_technologies", []),
        detected_projects=parsed_data.get("projects", []),
        experience=parsed_data.get("experience", []),
        summary=parsed_data.get("summary"),
        raw_text_length=parsed_data.get("raw_text_length", 0)
    )

@router.get("/resume/{resume_id}", response_model=ResumeAnalysisResponse)
def get_resume(resume_id: str):
    """Retrieves previously parsed resume information by resume_id."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Resume record not found.")

    p_data = json.loads(row["parsed_data_json"])
    return ResumeAnalysisResponse(
        success=True,
        resume_id=row["id"],
        filename=row["filename"],
        file_size=row["file_size"],
        file_type=row["file_type"],
        parser=row["parser_type"],
        is_fallback=p_data.get("is_fallback", False),
        detected_skills=p_data.get("detected_skills", []),
        languages_frameworks=p_data.get("languages_frameworks", []),
        tools_technologies=p_data.get("tools_technologies", []),
        detected_projects=p_data.get("projects", []),
        experience=p_data.get("experience", []),
        summary=p_data.get("summary"),
        raw_text_length=p_data.get("raw_text_length", 0)
    )

@router.post("/interview/start")
async def start_interview(payload: StartInterviewRequest):
    """
    Initializes a new interview session.
    Enforces explicit candidate consent before session creation and question generation.
    """
    consent_valid = False
    disclosed_categories = [
        "ai_question_generation",
        "response_text_analysis",
        "skill_rubric_scoring",
        "voice_transcription",
        "assistive_recruiter_reporting"
    ]
    policy_ver = "v1.2"
    read_understood = 0
    skill_assessment_agreed = 0

    if payload.consent:
        if (payload.consent.agreed and 
            payload.consent.read_understood and 
            payload.consent.skill_assessment_agreed):
            consent_valid = True
            read_understood = 1
            skill_assessment_agreed = 1
            policy_ver = payload.consent.policy_version or "v1.2"
            if payload.consent.categories_disclosed:
                disclosed_categories = payload.consent.categories_disclosed
    elif payload.consent_agreed:
        # Fallback for simple flag
        consent_valid = True
        read_understood = 1
        skill_assessment_agreed = 1

    if not consent_valid:
        raise HTTPException(
            status_code=403,
            detail="Candidate consent is mandatory before starting an AI interview session. Both acknowledgements must be accepted."
        )

    candidate_id = f"cand_{uuid.uuid4().hex[:8]}"
    interview_id = f"intv_{uuid.uuid4().hex[:8]}"

    conn = get_connection()
    cursor = conn.cursor()

    # Save Candidate (minimal necessary info: name/alias, role, language, mode)
    cursor.execute("""
        INSERT INTO candidates (id, name, email, role, language, interview_mode)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        candidate_id,
        payload.name or "Anonymous Candidate",
        payload.email,
        payload.role,
        payload.language,
        payload.interview_mode
    ))

    # Save Consent Record linked to interview session
    consent_notice_text = (
        "Candidate explicitly consented to AI-assisted job-skill evaluation with evidence tracking, "
        f"rubric scoring, and human recruiter final decision authority under policy {policy_ver}."
    )
    cursor.execute("""
        INSERT INTO consents (
            candidate_id, interview_id, consent_status, policy_version,
            categories_disclosed, read_understood, skill_assessment_agreed,
            consent_text, fairness_acknowledged
        )
        VALUES (?, ?, 'granted', ?, ?, ?, ?, ?, 1)
    """, (
        candidate_id,
        interview_id,
        policy_ver,
        json.dumps(disclosed_categories),
        read_understood,
        skill_assessment_agreed,
        consent_notice_text
    ))
    consent_row_id = cursor.lastrowid

    now_utc = datetime.now(timezone.utc)
    deadline_utc = now_utc + timedelta(minutes=20)
    started_at_str = now_utc.isoformat()
    deadline_at_str = deadline_utc.isoformat()

    total_q = payload.total_questions if (payload.total_questions and payload.total_questions > 0) else None

    # Retrieve parsed resume data if resume_id is provided
    resume_data = payload.resume_data
    if not resume_data and payload.resume_id:
        cursor.execute("SELECT parsed_data_json FROM resumes WHERE id = ?", (payload.resume_id,))
        r_row = cursor.fetchone()
        if r_row and r_row["parsed_data_json"]:
            try:
                resume_data = json.loads(r_row["parsed_data_json"])
            except Exception:
                resume_data = None

    # Start Interview (Baseline: MEDIUM difficulty, 20-min deadline, 0 weak answers, optional resume)
    cursor.execute("""
        INSERT INTO interviews (
            id, candidate_id, status, current_difficulty, current_question_index,
            total_questions, started_at, deadline_at, consecutive_weak_answers, termination_reason,
            resume_id
        )
        VALUES (?, ?, 'in_progress', 'MEDIUM', 0, ?, ?, ?, 0, 'NORMAL', ?)
    """, (
        interview_id,
        candidate_id,
        total_q,
        started_at_str,
        deadline_at_str,
        payload.resume_id
    ))

    conn.commit()
    conn.close()

    # Select the very first question ONLY AFTER consent has been recorded
    # When resume_data is provided, Turn 0 is personalized to the candidate's actual projects & skills
    first_q = select_next_question(
        interview_turn_index=0,
        current_difficulty="MEDIUM",
        asked_question_ids=[],
        role=payload.role,
        language=payload.language,
        total_questions=total_q,
        remaining_seconds=1200.0,
        resume_data=resume_data
    )

    if not first_q:
        raise HTTPException(status_code=500, detail="Could not select initial interview question.")

    first_q["deadline_at"] = deadline_at_str
    first_q["remaining_seconds"] = 1200.0

    return {
        "candidate_id": candidate_id,
        "interview_id": interview_id,
        "role": payload.role,
        "language": payload.language,
        "interview_mode": payload.interview_mode,
        "status": "in_progress",
        "started_at": started_at_str,
        "deadline_at": deadline_at_str,
        "remaining_seconds": 1200.0,
        "total_questions": total_q,
        "consecutive_weak_answers": 0,
        "resume_id": payload.resume_id,
        "consent": {
            "consent_id": consent_row_id,
            "status": "granted",
            "policy_version": policy_ver,
            "categories_disclosed": disclosed_categories
        },
        "first_question": first_q
    }

@router.post("/consent/decline")
def decline_consent(payload: DeclineConsentRequest):
    """
    Records a candidate's explicit refusal of consent.
    Ensures that no interview session is created and no AI questions are generated.
    """
    candidate_id = f"cand_declined_{uuid.uuid4().hex[:8]}"
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO candidates (id, name, email, role, language, interview_mode)
        VALUES (?, ?, NULL, ?, ?, 'none')
    """, (
        candidate_id,
        payload.candidate_name or "Anonymous Candidate (Declined)",
        payload.role,
        payload.language
    ))

    cursor.execute("""
        INSERT INTO consents (
            candidate_id, interview_id, consent_status, policy_version,
            categories_disclosed, read_understood, skill_assessment_agreed,
            consent_text, fairness_acknowledged
        )
        VALUES (?, NULL, 'declined', ?, ?, 0, 0, ?, 0)
    """, (
        candidate_id,
        payload.policy_version,
        json.dumps(["none"]),
        f"Candidate declined consent for {payload.role} ({payload.language}). No interview started."
    ))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "consent_status": "declined",
        "message": "You have declined consent. No interview will be started."
    }

@router.get("/interview/{id}/consent", response_model=ConsentVerificationResponse)
def get_interview_consent(id: str):
    """Retrieves and verifies the consent record for an interview session."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM consents WHERE interview_id = ? ORDER BY id DESC LIMIT 1
    """, (id,))
    row = cursor.fetchone()
    conn.close()

    if not row or row["consent_status"] != "granted":
        return ConsentVerificationResponse(
            interview_id=id,
            has_consent=False,
            consent_status="not_found" if not row else row["consent_status"],
            policy_version=row["policy_version"] if row else "unknown",
            categories_disclosed=[],
            agreed_at=None,
            candidate_id=row["candidate_id"] if row else None
        )

    categories = []
    if row["categories_disclosed"]:
        try:
            categories = json.loads(row["categories_disclosed"])
        except Exception:
            categories = [row["categories_disclosed"]]

    return ConsentVerificationResponse(
        interview_id=id,
        has_consent=True,
        consent_status=row["consent_status"],
        policy_version=row["policy_version"] or "v1.2",
        categories_disclosed=categories,
        agreed_at=str(row["agreed_at"]),
        candidate_id=row["candidate_id"]
    )

@router.post("/interview/answer")
async def submit_answer(payload: SubmitAnswerRequest):
    """
    Submits a candidate's answer for evaluation.
    Enforces active consent, authoritative 20-minute deadline, duplicate prevention,
    updates consecutive-weak counter (<40/100), terminates after 7 consecutive weak answers,
    and returns adaptive progression.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Enforce active candidate consent check on backend
    cursor.execute("""
        SELECT consent_status FROM consents
        WHERE interview_id = ? AND consent_status = 'granted'
    """, (payload.interview_id,))
    consent_row = cursor.fetchone()
    if not consent_row:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="Consent verification failed: No active granted consent record found for this interview session. Answer processing is disallowed."
        )

    # Retrieve interview
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (payload.interview_id,))
    interview_row = cursor.fetchone()
    if not interview_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    current_status = interview_row["status"]
    if current_status in ["completed", "TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"]:
        conn.close()
        term_reason = interview_row["termination_reason"] or current_status
        if term_reason == "TIME_EXPIRED":
            msg = "Interview time limit of 20 minutes has expired. No further answers are accepted."
        elif term_reason == "TERMINATED_WEAK_ANSWERS":
            msg = "Interview was terminated after 7 consecutive weak answers. No further answers are accepted."
        elif term_reason == "TERMINATED_FOCUS_VIOLATION":
            msg = "Interview was terminated due to a focus violation (leaving or switching tabs). No further answers are accepted."
        else:
            msg = "Interview is already completed."
        raise HTTPException(status_code=400, detail=msg)

    # Validate that this question has not already been submitted (prevent duplicate count)
    cursor.execute("""
        SELECT id FROM interview_turns WHERE interview_id = ? AND question_id = ?
    """, (payload.interview_id, payload.question_id))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Answer for this question has already been submitted.")

    # Validate authoritative 20-minute deadline BEFORE evaluating
    remaining_sec = calculate_remaining_seconds(interview_row["deadline_at"])
    if remaining_sec <= 0:
        cursor.execute("""
            UPDATE interviews
            SET status = 'TIME_EXPIRED',
                termination_reason = 'TIME_EXPIRED',
                completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP)
            WHERE id = ?
        """, (payload.interview_id,))
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Interview time limit of 20 minutes has expired. No further answers are accepted."
        )

    # Retrieve candidate
    cursor.execute("SELECT * FROM candidates WHERE id = ?", (interview_row["candidate_id"],))
    candidate_row = cursor.fetchone()

    # Retrieve question object
    q_obj = get_question_by_id(payload.question_id)
    if not q_obj:
        conn.close()
        raise HTTPException(status_code=404, detail="Question not found in question bank.")

    # Fairness pre-check
    fairness_meta = sanitize_and_check_fairness(payload.candidate_answer)

    # AI Evaluation (with automatic fallback to local rubric evaluator)
    eval_result = await evaluate_answer(
        question_obj=q_obj,
        candidate_answer=payload.candidate_answer,
        language=candidate_row["language"]
    )

    # Check if session was terminated concurrently (focus violation or manual termination)
    cursor.execute("SELECT status, termination_reason FROM interviews WHERE id = ?", (payload.interview_id,))
    concurrent_check = cursor.fetchone()
    if concurrent_check and concurrent_check["status"] in ["completed", "TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"]:
        conn.close()
        t_reason = concurrent_check["termination_reason"] or concurrent_check["status"]
        if t_reason == "TERMINATED_FOCUS_VIOLATION":
            msg = "Interview was terminated due to a focus violation (leaving or switching tabs). No further answers are accepted."
        elif t_reason == "TIME_EXPIRED":
            msg = "Interview time limit of 20 minutes has expired. No further answers are accepted."
        elif t_reason == "TERMINATED_WEAK_ANSWERS":
            msg = "Interview was terminated after 7 consecutive weak answers. No further answers are accepted."
        else:
            msg = "Interview is already completed."
        raise HTTPException(status_code=400, detail=msg)

    # Validate 20-minute deadline AGAIN after evaluation
    post_eval_remaining = calculate_remaining_seconds(interview_row["deadline_at"])
    if post_eval_remaining <= 0:
        cursor.execute("""
            UPDATE interviews
            SET status = 'TIME_EXPIRED',
                termination_reason = 'TIME_EXPIRED',
                completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP)
            WHERE id = ?
        """, (payload.interview_id,))
        conn.commit()
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Interview time limit of 20 minutes expired during evaluation. Interview is now closed."
        )

    evaluator_name = eval_result.get("evaluator", "rubric_engine")
    follow_up_suggested = eval_result.get("contextual_follow_up")
    ai_insight = eval_result.get("ai_insight")
    score_val = float(eval_result["score"])

    # Store Turn in Database atomically before state transitions
    turn_resp_time = payload.response_time_seconds or 0.0
    turn_q_type = q_obj.get("question_type") or "competency"
    turn_adapt_reason = eval_result.get("adaptive_reason") or eval_result.get("reason")

    cursor.execute("""
        INSERT INTO interview_turns (
            interview_id, question_id, question_text, language, skill, difficulty,
            candidate_answer, score, reason, evidence, strengths_json, weaknesses_json, confidence,
            evaluator, follow_up_suggested, response_time_seconds, adaptive_reason, question_type
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        payload.interview_id,
        payload.question_id,
        q_obj.get(f"question_{candidate_row['language']}", q_obj["question_en"]),
        candidate_row["language"],
        q_obj["skill"],
        q_obj["difficulty"],
        payload.candidate_answer,
        score_val,
        eval_result["reason"],
        eval_result["evidence"],
        json.dumps(eval_result.get("strengths", [])),
        json.dumps(eval_result.get("weaknesses", [])),
        eval_result.get("confidence", 0.85),
        evaluator_name,
        follow_up_suggested,
        turn_resp_time,
        turn_adapt_reason,
        turn_q_type
    ))
    turn_id = cursor.lastrowid

    # Update consecutive weak answers counter
    # Score strictly below 40/100 is weak. Score >= 40 resets counter to 0.
    current_weak = interview_row["consecutive_weak_answers"] or 0
    if score_val < 40.0:
        new_weak_count = current_weak + 1
    else:
        new_weak_count = 0

    next_turn_idx = interview_row["current_question_index"] + 1

    # Check termination condition: 7 consecutive weak answers
    if new_weak_count >= 7:
        cursor.execute("""
            UPDATE interviews
            SET status = 'TERMINATED_WEAK_ANSWERS',
                termination_reason = 'TERMINATED_WEAK_ANSWERS',
                consecutive_weak_answers = ?,
                completed_at = CURRENT_TIMESTAMP,
                current_question_index = ?
            WHERE id = ?
        """, (new_weak_count, next_turn_idx, payload.interview_id))
        conn.commit()
        conn.close()

        term_msg = (
            "Your interview has ended because 7 consecutive answers scored below the required threshold of 40/100. "
            "Your responses have been saved, and your interview report is available."
        )

        return {
            "turn_id": turn_id,
            "question_id": payload.question_id,
            "skill": q_obj["skill"],
            "difficulty": q_obj["difficulty"],
            "score": score_val,
            "reason": eval_result["reason"],
            "evidence": eval_result["evidence"],
            "strengths": eval_result.get("strengths", []),
            "weaknesses": eval_result.get("weaknesses", []),
            "confidence": eval_result.get("confidence", 0.85),
            "next_difficulty": interview_row["current_difficulty"],
            "is_completed": True,
            "next_question": None,
            "fairness_guaranteed": fairness_meta["fairness_guaranteed"],
            "evaluator": evaluator_name,
            "contextual_follow_up": None,
            "ai_insight": ai_insight,
            "consecutive_weak_answers": new_weak_count,
            "termination_reason": "TERMINATED_WEAK_ANSWERS",
            "termination_message": term_msg,
            "remaining_seconds": max(0.0, post_eval_remaining),
            "deadline_at": interview_row["deadline_at"]
        }

    # Normal Adaptive calculation for next step
    new_difficulty = calculate_next_difficulty(
        current_difficulty=interview_row["current_difficulty"],
        last_score=score_val
    )

    total_q = interview_row["total_questions"]

    # Get already asked question IDs and turn history for gap analysis
    cursor.execute("SELECT question_id, skill, difficulty, score FROM interview_turns WHERE interview_id = ?", (payload.interview_id,))
    asked_rows = cursor.fetchall()
    asked_ids = [r["question_id"] for r in asked_rows]
    turns_history = [dict(r) for r in asked_rows]

    # Retrieve candidate's resume data if available
    resume_data = None
    if "resume_id" in interview_row.keys() and interview_row["resume_id"]:
        cursor.execute("SELECT parsed_data_json FROM resumes WHERE id = ?", (interview_row["resume_id"],))
        res_row = cursor.fetchone()
        if res_row and res_row["parsed_data_json"]:
            try:
                resume_data = json.loads(res_row["parsed_data_json"])
            except Exception:
                resume_data = None

    # Select next adaptive question (incorporates answer quality, previous questions, difficulty, and resume)
    next_question = select_next_question(
        interview_turn_index=next_turn_idx,
        current_difficulty=new_difficulty,
        asked_question_ids=asked_ids,
        role=candidate_row["role"],
        language=candidate_row["language"],
        total_questions=total_q,
        previous_answer=payload.candidate_answer,
        last_score=score_val,
        remaining_seconds=post_eval_remaining,
        turns_history=turns_history,
        resume_data=resume_data
    )

    if total_q is not None and total_q > 0:
        is_completed = (next_question is None or next_turn_idx >= total_q)
    else:
        is_completed = (next_question is None)

    if is_completed:
        cursor.execute("""
            UPDATE interviews
            SET status = 'completed',
                termination_reason = 'NORMAL',
                consecutive_weak_answers = ?,
                completed_at = CURRENT_TIMESTAMP,
                current_question_index = ?
            WHERE id = ?
        """, (new_weak_count, next_turn_idx, payload.interview_id))
    else:
        cursor.execute("""
            UPDATE interviews
            SET current_difficulty = ?,
                current_question_index = ?,
                consecutive_weak_answers = ?
            WHERE id = ?
        """, (new_difficulty, next_turn_idx, new_weak_count, payload.interview_id))

    conn.commit()
    conn.close()

    if next_question:
        next_question["deadline_at"] = interview_row["deadline_at"]
        next_question["remaining_seconds"] = max(0.0, post_eval_remaining)

    # Adaptive decision summary
    adaptive_decision = eval_result.get("adaptive_decision")
    if not adaptive_decision:
        if score_val < 40.0:
            adaptive_decision = "foundational_diagnostic"
        elif score_val > 70.0:
            adaptive_decision = "advanced_challenge"
        else:
            adaptive_decision = "practical_follow_up"

    chosen_adaptive_reason = (next_question.get("adaptive_reason") if next_question else None) or eval_result.get("adaptive_reason")

    return {
        "turn_id": turn_id,
        "question_id": payload.question_id,
        "skill": q_obj["skill"],
        "difficulty": q_obj["difficulty"],
        "score": score_val,
        "score_out_of_10": eval_result.get("score_out_of_10", round(score_val / 10.0, 1)),
        "score_band": eval_result.get("score_band", ("weak" if score_val < 40 else ("strong" if score_val > 70 else "moderate"))),
        "reason": eval_result["reason"],
        "evidence": eval_result["evidence"],
        "strengths": eval_result.get("strengths", []),
        "weaknesses": eval_result.get("weaknesses", []),
        "correct_concepts": eval_result.get("correct_concepts", eval_result.get("strengths", [])),
        "missing_concepts": eval_result.get("missing_concepts", eval_result.get("weaknesses", [])),
        "adaptive_decision": adaptive_decision,
        "adaptive_reason": chosen_adaptive_reason,
        "confidence": eval_result.get("confidence", 0.85),
        "next_difficulty": new_difficulty,
        "is_completed": is_completed,
        "next_question": next_question,
        "fairness_guaranteed": fairness_meta["fairness_guaranteed"],
        "evaluator": evaluator_name,
        "contextual_follow_up": follow_up_suggested,
        "ai_insight": ai_insight,
        "consecutive_weak_answers": new_weak_count,
        "termination_reason": "NORMAL" if is_completed else None,
        "termination_message": None,
        "remaining_seconds": max(0.0, post_eval_remaining),
        "deadline_at": interview_row["deadline_at"],
        "response_time_seconds": payload.response_time_seconds or 0.0
    }

@router.post("/interview/complete")
def complete_interview(interview_id: str):
    """Forces completion of an interview and returns the synthesized report."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interviews
        SET status = 'completed', completed_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (interview_id,))
    conn.commit()
    conn.close()

    return get_report(interview_id)

@router.get("/interview/{id}")
def get_interview_state(id: str):
    """Retrieves current interview state, turns, candidate information, and live timer sync."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    intv_dict = dict(intv)
    remaining_sec = calculate_remaining_seconds(intv_dict.get("deadline_at"))

    # Auto-expire if session is still marked in_progress but backend deadline passed
    if remaining_sec <= 0 and intv_dict.get("status") == "in_progress":
        cursor.execute("""
            UPDATE interviews
            SET status = 'TIME_EXPIRED',
                termination_reason = 'TIME_EXPIRED',
                completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP)
            WHERE id = ?
        """, (id,))
        conn.commit()
        intv_dict["status"] = "TIME_EXPIRED"
        intv_dict["termination_reason"] = "TIME_EXPIRED"

    intv_dict["remaining_seconds"] = max(0.0, remaining_sec)

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (intv["candidate_id"],))
    cand = cursor.fetchone()

    cursor.execute("SELECT * FROM interview_turns WHERE interview_id = ? ORDER BY id ASC", (id,))
    turns = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "interview": intv_dict,
        "candidate": dict(cand) if cand else None,
        "turns": turns,
        "remaining_seconds": max(0.0, remaining_sec),
        "deadline_at": intv_dict.get("deadline_at"),
        "status": intv_dict.get("status"),
        "termination_reason": intv_dict.get("termination_reason"),
        "focus_violations_count": intv_dict.get("focus_violations_count", 0),
        "focus_violation_at": intv_dict.get("focus_violation_at")
    }

@router.get("/interview/{id}/history")
def get_interview_history(id: str):
    """Retrieves full question-and-answer turn history with evaluations and response times."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")
    
    cursor.execute("SELECT * FROM interview_turns WHERE interview_id = ? ORDER BY id ASC", (id,))
    turns = [dict(r) for r in cursor.fetchall()]
    conn.close()

    formatted_turns = []
    for t in turns:
        t_copy = dict(t)
        t_copy["answer"] = t.get("candidate_answer") or ""
        t_copy["question"] = t.get("question_text") or ""
        t_copy["score_out_of_10"] = round(t["score"] / 10.0, 1) if t.get("score") is not None else 0.0
        formatted_turns.append(t_copy)

    return {
        "success": True,
        "interview_id": id,
        "turns_count": len(turns),
        "total_turns": len(turns),
        "turns": formatted_turns,
        "history": formatted_turns
    }

@router.post("/interview/{id}/next-question")
def get_next_adaptive_question_endpoint(id: str):
    """
    Retrieves or generates the next adaptive question for an active interview session.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    if intv["status"] != "in_progress":
        conn.close()
        raise HTTPException(status_code=400, detail=f"Interview is not in progress ({intv['status']}).")

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (intv["candidate_id"],))
    cand = cursor.fetchone()

    cursor.execute("SELECT question_id, skill, difficulty, score FROM interview_turns WHERE interview_id = ? ORDER BY id ASC", (id,))
    asked_rows = cursor.fetchall()
    asked_ids = [r["question_id"] for r in asked_rows]
    turns_history = [dict(r) for r in asked_rows]
    last_turn = turns_history[-1] if turns_history else None

    resume_data = None
    if "resume_id" in intv.keys() and intv["resume_id"]:
        cursor.execute("SELECT parsed_data_json FROM resumes WHERE id = ?", (intv["resume_id"],))
        r_row = cursor.fetchone()
        if r_row and r_row["parsed_data_json"]:
            try:
                resume_data = json.loads(r_row["parsed_data_json"])
            except Exception:
                resume_data = None

    conn.close()

    rem_sec = calculate_remaining_seconds(intv["deadline_at"])
    next_turn_idx = len(turns_history)
    next_q = select_next_question(
        interview_turn_index=next_turn_idx,
        current_difficulty=intv["current_difficulty"],
        asked_question_ids=asked_ids,
        role=cand["role"] if cand else "Software Developer Intern",
        language=cand["language"] if cand else "en",
        total_questions=intv["total_questions"],
        last_score=last_turn["score"] if last_turn else None,
        remaining_seconds=rem_sec,
        turns_history=turns_history,
        resume_data=resume_data
    )

    if not next_q:
        return {"next_question": None, "is_completed": True}

    next_q["deadline_at"] = intv["deadline_at"]
    next_q["remaining_seconds"] = max(0.0, rem_sec)
    return {"next_question": next_q, "is_completed": False}

@router.post("/interview/{id}/expire")
def expire_interview(id: str):
    """
    Authoritatively marks an interview session as expired when the 20-minute countdown ends.
    First terminal condition wins atomically.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    curr_status = intv["status"]
    curr_reason = intv["termination_reason"] or curr_status
    if curr_status not in ["completed", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION", "TIME_EXPIRED"]:
        cursor.execute("""
            UPDATE interviews
            SET status = 'TIME_EXPIRED',
                termination_reason = 'TIME_EXPIRED',
                completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP)
            WHERE id = ? AND status = 'in_progress'
        """, (id,))
        conn.commit()
        conn.close()
        return {
            "success": True,
            "interview_id": id,
            "status": "TIME_EXPIRED",
            "termination_reason": "TIME_EXPIRED",
            "already_terminated": False,
            "message": "Your 20-minute interview time has ended. Your interview is now closed. You can view your interview report."
        }

    conn.close()
    return {
        "success": True,
        "interview_id": id,
        "status": curr_status,
        "termination_reason": curr_reason,
        "already_terminated": True,
        "message": f"Interview is already finalized ({curr_reason})."
    }

@router.post("/interview/{id}/violation")
@router.post("/interview/{id}/terminate")
def record_focus_violation(id: str, payload: Optional[FocusViolationRequest] = None):
    """
    Atomically records a focus violation and terminates the interview session.
    First terminal condition wins (TIME_EXPIRED, TERMINATED_WEAK_ANSWERS, TERMINATED_FOCUS_VIOLATION, completed).
    Idempotent: duplicate calls do not overwrite terminal state or increment duplicate terminations.
    Preserves all previously completed answers, evaluations, and progress.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    curr_status = intv["status"]
    curr_reason = intv["termination_reason"] or curr_status

    # If already in any terminal state, the first terminal event won!
    if curr_status in ["completed", "TIME_EXPIRED", "TERMINATED_WEAK_ANSWERS", "TERMINATED_FOCUS_VIOLATION"]:
        conn.close()
        return {
            "success": True,
            "interview_id": id,
            "status": curr_status,
            "termination_reason": curr_reason,
            "already_terminated": True,
            "focus_violations_count": intv["focus_violations_count"] or 0,
            "completed_at": str(intv["completed_at"]) if intv["completed_at"] else None,
            "message": f"Interview is already finalized with status: {curr_status}."
        }

    # Atomically transition in_progress -> TERMINATED_FOCUS_VIOLATION
    cursor.execute("""
        UPDATE interviews
        SET status = 'TERMINATED_FOCUS_VIOLATION',
            termination_reason = 'TERMINATED_FOCUS_VIOLATION',
            completed_at = COALESCE(completed_at, CURRENT_TIMESTAMP),
            focus_violations_count = COALESCE(focus_violations_count, 0) + 1,
            focus_violation_at = CURRENT_TIMESTAMP
        WHERE id = ? AND status = 'in_progress'
    """, (id,))
    conn.commit()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    updated_intv = cursor.fetchone()
    conn.close()

    return {
        "success": True,
        "interview_id": id,
        "status": "TERMINATED_FOCUS_VIOLATION",
        "termination_reason": "TERMINATED_FOCUS_VIOLATION",
        "already_terminated": False,
        "completed_at": str(updated_intv["completed_at"]) if updated_intv and updated_intv["completed_at"] else None,
        "focus_violations_count": updated_intv["focus_violations_count"] if updated_intv else 1,
        "message": "Interview terminated: interview page lost focus."
    }

@router.get("/report/{id}")
@router.get("/interview/{id}/report")
def get_report(id: str):
    """Generates and returns comprehensive candidate report for recruiter dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (id,))
    intv = cursor.fetchone()
    if not intv:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    cursor.execute("SELECT * FROM candidates WHERE id = ?", (intv["candidate_id"],))
    cand = cursor.fetchone()

    cursor.execute("SELECT * FROM interview_turns WHERE interview_id = ? ORDER BY id ASC", (id,))
    turns = [dict(r) for r in cursor.fetchall()]

    report = generate_candidate_report(
        candidate=dict(cand) if cand else {},
        interview=dict(intv),
        turns=turns
    )

    # Save overall score and recommendation to interview table if not already set
    cursor.execute("""
        UPDATE interviews
        SET overall_score = ?,
            ai_recommendation = ?
        WHERE id = ?
    """, (report["overall_score"], report["ai_recommendation"], id))
    
    # Fetch linked consent record for audit verification
    cursor.execute("""
        SELECT * FROM consents WHERE interview_id = ? ORDER BY id DESC LIMIT 1
    """, (id,))
    consent_record = cursor.fetchone()

    conn.commit()
    conn.close()

    # Include recruiter decision fields from DB
    report["recruiter_decision"] = intv["recruiter_decision"]
    report["recruiter_notes"] = intv["recruiter_notes"]
    report["decision_updated_at"] = intv["decision_updated_at"]
    
    # Include verified consent metadata
    if consent_record:
        cats = []
        if consent_record["categories_disclosed"]:
            try:
                cats = json.loads(consent_record["categories_disclosed"])
            except Exception:
                cats = [consent_record["categories_disclosed"]]
        report["consent_record"] = {
            "status": consent_record["consent_status"],
            "policy_version": consent_record["policy_version"] or "v1.2",
            "agreed_at": str(consent_record["agreed_at"]),
            "categories_disclosed": cats
        }
    else:
        report["consent_record"] = {
            "status": "granted",
            "policy_version": "v1.2",
            "agreed_at": str(intv["started_at"]),
            "categories_disclosed": [
                "ai_question_generation",
                "response_text_analysis",
                "skill_rubric_scoring",
                "assistive_recruiter_reporting"
            ]
        }

    return report

@router.post("/recruiter/decision")
def save_recruiter_decision(payload: RecruiterDecisionRequest):
    """
    Human-in-the-loop action.
    A human recruiter records the final hiring decision: 'shortlist', 'review_later', or 'reject'.
    """
    if payload.decision not in ["shortlist", "review_later", "reject"]:
        raise HTTPException(status_code=400, detail="Invalid decision value.")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE interviews
        SET recruiter_decision = ?,
            recruiter_notes = ?,
            decision_updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (payload.decision, payload.notes, payload.interview_id))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Interview not found.")

    conn.commit()
    conn.close()

    return {
        "success": True,
        "interview_id": payload.interview_id,
        "decision": payload.decision,
        "notes": payload.notes,
        "message": f"Human recruiter decision recorded: {payload.decision.upper()}."
    }

@router.get("/recruiter/candidates")
def list_candidates():
    """Returns candidate roster and scores for the Recruiter Dashboard."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            i.id as interview_id,
            i.status,
            COALESCE(i.termination_reason, 'NORMAL') as termination_reason,
            COALESCE(i.consecutive_weak_answers, 0) as consecutive_weak_answers,
            i.deadline_at,
            i.current_difficulty,
            i.overall_score,
            i.ai_recommendation,
            i.recruiter_decision,
            i.started_at,
            i.completed_at,
            c.id as candidate_id,
            c.name as candidate_name,
            c.role,
            c.language,
            c.interview_mode,
            i.resume_id,
            (SELECT filename FROM resumes WHERE id = i.resume_id) as resume_filename,
            (SELECT COUNT(*) FROM interview_turns WHERE interview_id = i.id) as turns_count,
            COALESCE((SELECT consent_status FROM consents WHERE interview_id = i.id ORDER BY id DESC LIMIT 1), 'granted') as consent_status,
            COALESCE((SELECT policy_version FROM consents WHERE interview_id = i.id ORDER BY id DESC LIMIT 1), 'v1.2') as consent_policy_version
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        ORDER BY i.started_at DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    return {"candidates": rows}

@router.post("/evaluate")
async def standalone_evaluate(payload: StandaloneEvaluateRequest):
    """Standalone evaluation test endpoint."""
    q_obj = get_question_by_id(payload.question_id)
    if not q_obj:
        raise HTTPException(status_code=404, detail="Question not found.")

    result = await evaluate_answer(
        question_obj=q_obj,
        candidate_answer=payload.candidate_answer,
        language=payload.language
    )
    return result

@router.post("/demo/seed")
def seed_demo_data():
    """
    Populates sample candidates so judges and users can immediately explore the
    Recruiter Dashboard and Candidate Evidence without running a fresh interview.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Demo 1: English Candidate (Software Developer Intern, High score)
    c1_id = "cand_demo_001"
    i1_id = "intv_demo_001"
    cursor.execute("DELETE FROM candidates WHERE id IN ('cand_demo_001', 'cand_demo_002', 'cand_demo_003')")
    cursor.execute("DELETE FROM interviews WHERE id IN ('intv_demo_001', 'intv_demo_002', 'intv_demo_003')")
    cursor.execute("DELETE FROM interview_turns WHERE interview_id IN ('intv_demo_001', 'intv_demo_002', 'intv_demo_003')")
    cursor.execute("DELETE FROM consents WHERE candidate_id IN ('cand_demo_001', 'cand_demo_002', 'cand_demo_003') OR interview_id IN ('intv_demo_001', 'intv_demo_002', 'intv_demo_003')")

    demo_categories = json.dumps([
        "ai_question_generation",
        "response_text_analysis",
        "skill_rubric_scoring",
        "voice_transcription",
        "assistive_recruiter_reporting"
    ])

    # Insert Consents for Demo Candidates
    cursor.execute("""
        INSERT INTO consents (candidate_id, interview_id, consent_status, policy_version, categories_disclosed, read_understood, skill_assessment_agreed, consent_text, fairness_acknowledged)
        VALUES (?, ?, 'granted', 'v1.2', ?, 1, 1, 'Candidate explicitly consented to AI-assisted job-skill assessment (Demo).', 1)
    """, (c1_id, i1_id, demo_categories))

    # Insert Candidate 1
    cursor.execute("""
        INSERT INTO candidates (id, name, email, role, language, interview_mode)
        VALUES (?, 'Aarav Sharma (English)', 'aarav@example.com', 'Software Developer Intern', 'en', 'voice')
    """, (c1_id,))
    cursor.execute("""
        INSERT INTO interviews (
            id, candidate_id, status, current_difficulty, current_question_index, total_questions,
            overall_score, ai_recommendation, recruiter_decision, recruiter_notes,
            started_at, deadline_at, completed_at, consecutive_weak_answers, termination_reason
        )
        VALUES (?, ?, 'completed', 'HARD', 5, 5, 84.4, 'Strong Match', 'shortlist',
                'Excellent grasp of memory management and system trade-offs. Proceed to team fit round.',
                '2026-10-09T06:40:00+00:00', '2026-10-09T07:00:00+00:00', '2026-10-09T06:58:14+00:00', 0, 'NORMAL')
    """, (i1_id, c1_id))

    # Insert Turns for Candidate 1
    t1_data = [
        ("prog_med_1", "Programming Fundamentals", "MEDIUM", 86.0,
         "Stack is organized as LIFO for local variables and function calls, which is extremely fast. Heap is dynamic allocation for objects that live beyond single scopes.",
         "Candidate demonstrated clear grasp of LIFO structure and execution memory.",
         '"...Stack is organized as LIFO for local variables... Heap is dynamic allocation for objects... "'),
        ("prob_med_1", "Problem Solving", "MEDIUM", 84.0,
         "Brute force checks every pair in O(N^2). We optimize to O(N) by using a Hash Map where we look up target minus current number in O(1) time.",
         "Correctly identified complement calculation and linear hash map lookup.",
         '"...optimize to O(N) by using a Hash Map where we look up target minus current number..."'),
        ("dsa_hard_1", "Data Structures & Algorithms", "HARD", 88.0,
         "To get O(1) for both get and put in an LRU cache, combine a Hash Map and a Doubly Linked List. Map gives O(1) lookup, list maintains recency with head and tail.",
         "Superb explanation of dual data structure mechanics.",
         '"...combine a Hash Map and a Doubly Linked List. Map gives O(1) lookup, list maintains recency..."'),
        ("tech_hard_1", "Technical Understanding", "HARD", 82.0,
         "Monoliths deploy together while microservices break into independent bounded domains. The trade-off is network latency, partial failures, and CAP theorem data consistency.",
         "Articulated distributed trade-offs and CAP theorem.",
         '"...trade-off is network latency, partial failures, and CAP theorem data consistency..."'),
        ("comm_med_1", "Communication", "MEDIUM", 82.0,
         "I separate ego from code and assume positive intent. I review the architectural rationale, and if we disagree, I suggest a quick 10-minute sync rather than comment wars.",
         "Demonstrated high emotional maturity and proactive collaboration.",
         '"...separate ego from code and assume positive intent... suggest a quick 10-minute sync..."')
    ]

    for q_id, skill, diff, sc, ans, reason, ev in t1_data:
        cursor.execute("""
            INSERT INTO interview_turns (
                interview_id, question_id, question_text, language, skill, difficulty,
                candidate_answer, score, reason, evidence, strengths_json, weaknesses_json, confidence
            ) VALUES (?, ?, ?, 'en', ?, ?, ?, ?, ?, ?, '["Clear articulation", "Correct technical foundation"]', '["Add more production examples"]', 0.92)
        """, (i1_id, q_id, q_id, skill, diff, ans, sc, reason, ev))

    # Demo 2: Hindi Candidate (Software Developer Intern, Demonstrating Multilingual Fairness)
    c2_id = "cand_demo_002"
    i2_id = "intv_demo_002"
    cursor.execute("""
        INSERT INTO consents (candidate_id, interview_id, consent_status, policy_version, categories_disclosed, read_understood, skill_assessment_agreed, consent_text, fairness_acknowledged)
        VALUES (?, ?, 'granted', 'v1.2', ?, 1, 1, 'अभ्यर्थी ने AI-सहायता प्राप्त कौशल मूल्यांकन के लिए स्पष्ट सहमति दी (डेमो)।', 1)
    """, (c2_id, i2_id, demo_categories))
    cursor.execute("""
        INSERT INTO candidates (id, name, email, role, language, interview_mode)
        VALUES (?, 'Pooja Verma (हिंदी)', 'pooja@example.com', 'Software Developer Intern', 'hi', 'text')
    """, (c2_id,))
    cursor.execute("""
        INSERT INTO interviews (
            id, candidate_id, status, current_difficulty, current_question_index, total_questions,
            overall_score, ai_recommendation, recruiter_decision, recruiter_notes,
            started_at, deadline_at, completed_at, consecutive_weak_answers, termination_reason
        )
        VALUES (?, ?, 'completed', 'HARD', 5, 5, 82.8, 'Strong Match', 'review_later',
                'Strong technical reasoning in Hindi. Verified that language choice did not negatively affect score.',
                '2026-10-09T06:15:00+00:00', '2026-10-09T06:35:00+00:00', '2026-10-09T06:33:45+00:00', 0, 'NORMAL')
    """, (i2_id, c2_id))

    t2_data = [
        ("prog_med_1", "Programming Fundamentals", "MEDIUM", 84.0,
         "Stack मेमोरी LIFO सिद्धांत पर काम करती है और लोकल वेरिएबल्स के लिए होती है जो बहुत तेज़ है। Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है और इसे गारबेज कलेक्टर से फ्री किया जाता है।",
         "अभ्यर्थी ने स्टैक और हीप के अंतर को सटीकता से समझाया।",
         '"...Stack मेमोरी LIFO सिद्धांत पर काम करती है... Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है..."'),
        ("prob_med_1", "Problem Solving", "MEDIUM", 82.0,
         "Brute force में दो लूप से O(N^2) समय लगता है। अनुकूलित समाधान Hash Map का उपयोग करना है जिसमें target - x को O(1) में ढूँढकर O(N) समय में हल हो जाता है।",
         "Hash Map आधारित O(N) समाधान का सटीक विश्लेषण।",
         '"...अनुकूलित समाधान Hash Map का उपयोग करना है जिसमें target - x को O(1) में ढूँढकर..."'),
        ("dsa_hard_1", "Data Structures & Algorithms", "HARD", 85.0,
         "O(1) get और put के लिए Hash Map और Doubly Linked List का संयोजन इस्तेमाल करते हैं। Hash Map O(1) सर्च देता है और Doubly Linked List O(1) में नोड्स अपडेट करती है।",
         "डबल लिंक्ड लिस्ट और हैश मैप के संयोजन की उत्कृष्ट व्याख्या।",
         '"...Hash Map और Doubly Linked List का संयोजन इस्तेमाल करते हैं..."'),
        ("tech_hard_1", "Technical Understanding", "HARD", 80.0,
         "Monolith में एक ही कोडबेस होता है जबकि Microservices में स्वतंत्र सर्विसेज होती हैं। Microservices में नेटवर्क फेलियर और डेटा कंसिस्टेंसी की समस्या आती है जिसके लिए Saga पैटर्न यूज़ करते हैं।",
         "माइक्रोसर्विस चुनौतियों और सागा पैटर्न का उल्लेख।",
         '"...Microservices में नेटवर्क फेलियर और डेटा कंसिस्टेंसी की समस्या आती है जिसके लिए Saga पैटर्न..."'),
        ("comm_med_1", "Communication", "MEDIUM", 83.0,
         "मैं कोड रिव्यु को व्यक्तिगत नहीं लेता। अगर सुझाव अच्छा है तो अपनाता हूँ, और अगर कोई शंका है तो कमेंट्स में बहस करने के बजाय 10 मिनट की कॉल पर चर्चा करने का प्रस्ताव देता हूँ।",
         "रचनात्मक दृष्टिकोण और टीम सहयोग की परिपक्व सोच।",
         '"...कमेंट्स में बहस करने के बजाय 10 मिनट की कॉल पर चर्चा करने का प्रस्ताव देता हूँ..."')
    ]

    for q_id, skill, diff, sc, ans, reason, ev in t2_data:
        cursor.execute("""
            INSERT INTO interview_turns (
                interview_id, question_id, question_text, language, skill, difficulty,
                candidate_answer, score, reason, evidence, strengths_json, weaknesses_json, confidence
            ) VALUES (?, ?, ?, 'hi', ?, ?, ?, ?, ?, ?, '["स्पष्ट तकनीकी तर्क", "सटीक डेटा स्ट्रक्चर ज्ञान"]', '["और अधिक प्रोडक्शन उदाहरण दिए जा सकते हैं"]', 0.90)
        """, (i2_id, q_id, q_id, skill, diff, ans, sc, reason, ev))

    # Demo 3: Adaptive Candidate showing difficulty transitions
    c3_id = "cand_demo_003"
    i3_id = "intv_demo_003"
    cursor.execute("""
        INSERT INTO consents (candidate_id, interview_id, consent_status, policy_version, categories_disclosed, read_understood, skill_assessment_agreed, consent_text, fairness_acknowledged)
        VALUES (?, ?, 'granted', 'v1.2', ?, 1, 1, 'Candidate explicitly consented to AI-assisted job-skill assessment (Demo).', 1)
    """, (c3_id, i3_id, demo_categories))
    cursor.execute("""
        INSERT INTO candidates (id, name, email, role, language, interview_mode)
        VALUES (?, 'Rohan Patel (Adaptive Demo)', 'rohan@example.com', 'Software Developer Intern', 'en', 'text')
    """, (c3_id,))
    cursor.execute("""
        INSERT INTO interviews (
            id, candidate_id, status, current_difficulty, current_question_index, total_questions,
            overall_score, ai_recommendation, recruiter_decision, recruiter_notes,
            started_at, deadline_at, completed_at, consecutive_weak_answers, termination_reason
        )
        VALUES (?, ?, 'completed', 'MEDIUM', 5, 5, 68.6, 'Potential Match', NULL, '',
                '2026-10-09T06:00:00+00:00', '2026-10-09T06:20:00+00:00', '2026-10-09T06:17:10+00:00', 0, 'NORMAL')
    """, (i3_id, c3_id))

    t3_data = [
        ("prog_easy_1", "Programming Fundamentals", "EASY", 92.0,
         "A variable is a named storage location in memory. Declaration specifies name and type, while initialization assigns the starting value.",
         "Solid foundational answer on declaration vs initialization.",
         '"...named storage location in memory. Declaration specifies name and type..."'),
        ("prob_med_1", "Problem Solving", "MEDIUM", 76.0,
         "We can use a hash map to store elements we have seen so far. For each number, we look up target minus number.",
         "Understands hash map lookup technique.",
         '"...use a hash map to store elements we have seen so far..."'),
        ("dsa_hard_2", "Data Structures & Algorithms", "HARD", 48.0,
         "Dynamic programming is when you use loops to remember things. It avoids doing the same work.",
         "Basic intuition on caching, but missed Optimal Substructure and Overlapping Subproblems definitions.",
         '"...Dynamic programming is when you use loops to remember things..."'),
        ("tech_med_1", "Technical Understanding", "MEDIUM", 65.0,
         "SQL has tables and relationships, while NoSQL has JSON documents. SQL is good for consistency and NoSQL is good for scaling.",
         "Acceptable high level contrast, missing deep ACID or indexing breakdown.",
         '"...SQL has tables and relationships, while NoSQL has JSON documents..."'),
        ("comm_easy_1", "Communication", "EASY", 62.0,
         "I would explain the bug in simple terms without using too much code jargon, and let the client know when it will be fixed.",
         "Understands avoiding jargon, but lacked structured communication framework.",
         '"...explain the bug in simple terms without using too much code jargon..."')
    ]

    for q_id, skill, diff, sc, ans, reason, ev in t3_data:
        cursor.execute("""
            INSERT INTO interview_turns (
                interview_id, question_id, question_text, language, skill, difficulty,
                candidate_answer, score, reason, evidence, strengths_json, weaknesses_json, confidence
            ) VALUES (?, ?, ?, 'en', ?, ?, ?, ?, ?, ?, '["Concise"]', '["Provide deeper technical trade-offs"]', 0.85)
        """, (i3_id, q_id, q_id, skill, diff, ans, sc, reason, ev))

    conn.commit()
    conn.close()

    return {
        "success": True,
        "message": "Seeded 3 diverse demonstration candidates (English, Hindi, Adaptive).",
        "demo_candidates": [
            {"candidate_id": c1_id, "interview_id": i1_id, "name": "Aarav Sharma", "lang": "English", "score": 84.4},
            {"candidate_id": c2_id, "interview_id": i2_id, "name": "Pooja Verma", "lang": "Hindi", "score": 82.8},
            {"candidate_id": c3_id, "interview_id": i3_id, "name": "Rohan Patel", "lang": "Adaptive Demo", "score": 68.6}
        ]
    }
