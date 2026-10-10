"""
Pydantic schemas for request and response validation in IntervueAI.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ConsentPayload(BaseModel):
    agreed: bool = False
    read_understood: bool = False
    skill_assessment_agreed: bool = False
    policy_version: str = "v1.2"
    categories_disclosed: Optional[List[str]] = Field(default_factory=list)

class StartInterviewRequest(BaseModel):
    name: Optional[str] = "Anonymous Candidate"
    email: Optional[str] = None
    role: str = "Software Developer Intern"
    language: str = "en"  # "en" or "hi"
    interview_mode: str = "text"  # "text" or "voice"
    consent_agreed: bool = False
    consent: Optional[ConsentPayload] = None
    total_questions: Optional[int] = None
    resume_id: Optional[str] = None
    resume_data: Optional[Dict[str, Any]] = None

class DeclineConsentRequest(BaseModel):
    candidate_name: Optional[str] = "Anonymous Candidate"
    role: str = "Software Developer Intern"
    language: str = "en"
    policy_version: str = "v1.2"
    reason: Optional[str] = "candidate_declined"

class ConsentVerificationResponse(BaseModel):
    interview_id: str
    has_consent: bool
    consent_status: str
    policy_version: str
    categories_disclosed: List[str]
    agreed_at: Optional[str] = None
    candidate_id: Optional[str] = None

class SubmitAnswerRequest(BaseModel):
    interview_id: str
    question_id: str
    candidate_answer: str
    response_time_seconds: Optional[float] = 0.0

class StandaloneEvaluateRequest(BaseModel):
    question_id: str
    candidate_answer: str
    language: str = "en"

class RecruiterDecisionRequest(BaseModel):
    interview_id: str
    decision: str  # "shortlist", "review_later", "reject"
    notes: Optional[str] = ""

class GeminiKeyRequest(BaseModel):
    gemini_api_key: str

class ResumeAnalysisResponse(BaseModel):
    success: bool = True
    resume_id: str
    filename: str
    file_size: int
    file_type: str
    parser: str
    is_fallback: bool
    detected_skills: List[str] = Field(default_factory=list)
    languages_frameworks: List[str] = Field(default_factory=list)
    tools_technologies: List[str] = Field(default_factory=list)
    detected_projects: List[Dict[str, Any]] = Field(default_factory=list)
    experience: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[str] = None
    raw_text_length: Optional[int] = 0

class QuestionResponse(BaseModel):
    question_id: str
    skill: str
    difficulty: str
    question_text: str
    question: Optional[str] = None  # alias for convenient frontend consumption
    question_index: int
    total_questions: Optional[int] = None
    language: str
    question_type: Optional[str] = "competency"  # "project_deep_dive", "skill_verification", "foundational_diagnostic", "practical_application", "advanced_challenge", etc.
    reason: Optional[str] = None
    adaptive_reason: Optional[str] = None
    follow_ups: Optional[List[str]] = []
    deadline_at: Optional[str] = None
    remaining_seconds: Optional[float] = None

class AnswerEvaluationResponse(BaseModel):
    turn_id: int
    question_id: str
    skill: str
    difficulty: str
    score: float
    score_out_of_10: Optional[float] = None
    score_band: Optional[str] = "moderate"  # "weak", "moderate", "strong"
    reason: str
    evidence: str
    strengths: List[str]
    weaknesses: List[str]
    correct_concepts: Optional[List[str]] = Field(default_factory=list)
    missing_concepts: Optional[List[str]] = Field(default_factory=list)
    adaptive_decision: Optional[str] = None
    adaptive_reason: Optional[str] = None
    confidence: float
    next_difficulty: str
    is_completed: bool
    next_question: Optional[QuestionResponse] = None
    evaluator: Optional[str] = "rubric_engine"
    contextual_follow_up: Optional[str] = None
    ai_insight: Optional[str] = None
    consecutive_weak_answers: Optional[int] = 0
    termination_reason: Optional[str] = None
    termination_message: Optional[str] = None
    remaining_seconds: Optional[float] = None
    deadline_at: Optional[str] = None
    response_time_seconds: Optional[float] = 0.0

class AiSettingsResponse(BaseModel):
    provider: str
    is_configured: bool
    masked_key: Optional[str] = None
    active_model: str
    supported_models: List[str]
    status_message: str

class FocusViolationRequest(BaseModel):
    interview_id: Optional[str] = None
    reason: str = "TERMINATED_FOCUS_VIOLATION"
    details: Optional[str] = "Interview page lost focus (tab switch, window minimized, or navigated away)."


