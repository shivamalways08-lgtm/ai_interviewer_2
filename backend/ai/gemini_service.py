"""
Gemini AI Integration Service for IntervueAI
Uses Google GenAI SDK (google-genai) to power live adaptive evaluation,
evidence harvesting, and dynamic follow-up questioning.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from google import genai
from google.genai import types

from backend.prompts.eval_prompt import FAIRNESS_SYSTEM_INSTRUCTION, EVALUATION_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash"
]

def get_gemini_client(api_key: Optional[str] = None) -> Optional[genai.Client]:
    key = api_key or os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None
    try:
        return genai.Client(api_key=key)
    except Exception as e:
        logger.error(f"Failed to initialize Gemini client: {e}")
        return None

def validate_gemini_key(api_key: str) -> Dict[str, Any]:
    """Tests an API key against the Gemini API to verify validity."""
    if not api_key or not api_key.strip():
        return {"valid": False, "error": "API key cannot be empty."}
    
    clean_key = api_key.strip()
    try:
        client = genai.Client(api_key=clean_key)
        # Fast test generation
        res = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'OK' in one word.",
            config=types.GenerateContentConfig(max_output_tokens=10)
        )
        if res and res.text:
            return {"valid": True, "model": "gemini-2.5-flash", "message": "Gemini API key is active and working!"}
        return {"valid": False, "error": "Empty response from Gemini API."}
    except Exception as e:
        # Try fallback model
        try:
            client = genai.Client(api_key=clean_key)
            res = client.models.generate_content(
                model="gemini-1.5-flash",
                contents="Say 'OK' in one word.",
                config=types.GenerateContentConfig(max_output_tokens=10)
            )
            if res and res.text:
                return {"valid": True, "model": "gemini-1.5-flash", "message": "Gemini API key verified with gemini-1.5-flash!"}
        except Exception as e2:
            pass
        return {"valid": False, "error": str(e)}

def save_gemini_key_to_env(api_key: str) -> bool:
    """Saves the API key to runtime environment and persists to .env file."""
    clean_key = api_key.strip()
    os.environ["GEMINI_API_KEY"] = clean_key
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
    try:
        lines = []
        key_found = False
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith("GEMINI_API_KEY="):
                    new_lines.append(f"GEMINI_API_KEY={clean_key}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            lines = new_lines

        if not key_found:
            lines.append(f"\nGEMINI_API_KEY={clean_key}\n")

        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True
    except Exception as e:
        logger.error(f"Error saving key to .env: {e}")
        return False

def evaluate_with_gemini(
    question_obj: Dict[str, Any],
    candidate_answer: str,
    language: str = "en",
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Evaluates candidate answer using Google Gemini with structured JSON output,
    strictly adhering to the fairness system instruction and job rubric.
    """
    client = get_gemini_client(api_key)
    if not client:
        return None

    lang_name = "Hindi (हिंदी)" if language == "hi" else "English"
    prompt_text = EVALUATION_USER_PROMPT_TEMPLATE.format(
        role=question_obj.get("role", "Software Developer Intern"),
        skill=question_obj.get("skill", "Technical Understanding"),
        difficulty=question_obj.get("difficulty", "MEDIUM"),
        question=question_obj.get(f"question_{language}", question_obj.get("question_en", "")),
        expected_concepts=", ".join(question_obj.get("expected_concepts", [])),
        rubric=json.dumps(question_obj.get("rubric", {})),
        candidate_answer=candidate_answer,
        language=lang_name
    )

    # Append instruction for dynamic follow-up question
    prompt_text += f"""
Also include in your JSON:
- "contextual_follow_up": "<a relevant, personalized follow-up technical question in {lang_name} addressing what the candidate stated>"
- "ai_insight": "<a brief 1-sentence analytical insight on candidate's technical reasoning depth>"
"""

    config = types.GenerateContentConfig(
        system_instruction=FAIRNESS_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        temperature=0.2,
    )

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=config
            )
            if response and response.text:
                data = json.loads(response.text)
                data["evaluator"] = f"gemini_live ({model_name})"
                data["difficulty"] = question_obj.get("difficulty", "MEDIUM")
                # Clamp score
                score_val = max(0.0, min(100.0, float(data.get("score", 70))))
                data["score"] = score_val
                data["score_out_of_10"] = round(score_val / 10.0, 1)
                data["score_band"] = "weak" if score_val < 40 else ("strong" if score_val > 70 else "moderate")
                if not data.get("correct_concepts"):
                    data["correct_concepts"] = data.get("matched_concepts") or []
                if not data.get("missing_concepts"):
                    data["missing_concepts"] = []
                if not data.get("adaptive_decision"):
                    data["adaptive_decision"] = f"Candidate score band is {data['score_band']} ({score_val}/100). Adapting difficulty and follow-up."
                data["adaptive_reason"] = data["adaptive_decision"]
                # Ensure evidence field exists
                if not data.get("evidence"):
                    data["evidence"] = "Insufficient evidence from this answer."
                return data
        except Exception as e:
            logger.warning(f"Gemini model {model_name} failed: {e}. Trying next model...")

    return None

def generate_dynamic_question_with_gemini(
    role: str,
    skill: str,
    difficulty: str,
    language: str = "en",
    asked_question_texts: Optional[list] = None,
    previous_answer: Optional[str] = None,
    last_score: Optional[float] = None,
    remaining_seconds: Optional[float] = None,
    resume_data: Optional[Dict[str, Any]] = None,
    question_type: Optional[str] = "competency",
    api_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Generates a dynamic, novel, rubric-grounded interview question using Gemini.
    Adapts based on candidate's previous response, resume skills & projects,
    skill domain, target difficulty, and remaining time.
    """
    client = get_gemini_client(api_key)
    if not client:
        return None

    lang_name = "Hindi (हिंदी)" if language == "hi" else "English"
    asked_summary = "\n- ".join(asked_question_texts[-6:]) if asked_question_texts else "None"

    context_prompt = ""
    if previous_answer and last_score is not None:
        if last_score < 40:
            context_prompt = (
                f"The candidate gave a weak response to the previous question (score {last_score}/100): \"{previous_answer[:150]}\". "
                "Ask a supportive, foundational diagnostic question to test their core understanding at an accessible foundational level. "
                "Do NOT repeat the previous question."
            )
        elif last_score > 70:
            context_prompt = (
                f"The candidate gave a strong answer to the previous question (score {last_score}/100): \"{previous_answer[:150]}\". "
                "Ask a more challenging, deeper architectural, optimization, or trade-off question to test their advanced expertise."
            )
        else:
            context_prompt = (
                f"The candidate gave a satisfactory answer to the previous question (score {last_score}/100). "
                "Ask a practical, scenario-based question to verify applied implementation knowledge and trade-offs."
            )

    resume_context = ""
    if resume_data:
        r_skills = ", ".join(resume_data.get("detected_skills", [])[:8])
        proj_list = []
        for p in (resume_data.get("detected_projects") or resume_data.get("projects") or [])[:3]:
            p_name = p.get("name", "Project")
            p_tech = ", ".join(p.get("technologies", []))
            proj_list.append(f"{p_name} (using {p_tech})")
        proj_str = "; ".join(proj_list)
        resume_context = f"""
CANDIDATE RESUME EVIDENCE:
- Detected Technical Skills: {r_skills}
- Detected Projects: {proj_str}
Personalize the question using the candidate's actual projects or claimed skills while aligning with the {role} requirements.
"""

    time_context = ""
    if remaining_seconds is not None:
        mins_left = max(1, int(remaining_seconds) // 60)
        time_context = f"Session timing: Approximately {mins_left} minutes remain in the 20-minute interview. Keep the question crisp and focused."

    prompt_text = f"""
You are an expert AI technical interviewer for a fair hiring platform.
Generate the next adaptive technical interview question for a candidate.

SPECIFICATIONS:
- Role: {role}
- Competency to assess: {skill}
- Target Difficulty: {difficulty}
- Language: {lang_name}
- Question Category: {question_type}
{context_prompt}
{resume_context}
{time_context}

CRITICAL RULES:
- Ask exactly ONE clear, focused question.
- Do NOT repeat or closely reword any of the following questions already asked:
- {asked_summary}
- Provide an adaptive explanation for why this question is being asked.

Return a VALID JSON object with this exact structure:
{{
  "question_text": "<Clear, professional interview question in {lang_name}>",
  "question_type": "{question_type}",
  "reason": "<Brief 1-sentence adaptive rationale for asking this question>",
  "expected_concepts": ["<key technical concept 1>", "<key technical concept 2>", "<key technical concept 3>"],
  "ideal_answer_points": [
    "<key explanation or trade-off point 1>",
    "<key explanation or trade-off point 2>"
  ],
  "rubric": {{
    "excellent": "<criteria for 80-100 score>",
    "good": "<criteria for 65-79 score>",
    "average": "<criteria for 45-64 score>",
    "poor": "<criteria for below 40 score>"
  }},
  "follow_ups": [
    "<optional follow-up sub-question 1>",
    "<optional follow-up sub-question 2>"
  ]
}}
"""

    config = types.GenerateContentConfig(
        system_instruction=FAIRNESS_SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        temperature=0.3,
    )

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_text,
                config=config
            )
            if response and response.text:
                data = json.loads(response.text)
                if data.get("question_text"):
                    data["role"] = role
                    data["skill"] = skill
                    data["difficulty"] = difficulty
                    data["language"] = language
                    data["question_type"] = data.get("question_type") or question_type
                    data["reason"] = data.get("reason") or f"Adaptive {difficulty.lower()} question on {skill}."
                    data["evaluator"] = f"gemini_live ({model_name})"
                    return data
        except Exception as e:
            logger.warning(f"Gemini dynamic question generation with {model_name} failed: {e}. Trying next...")

    return None
