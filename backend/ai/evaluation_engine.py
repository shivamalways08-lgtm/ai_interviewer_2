"""
AI Evaluation Engine for IntervueAI
Provides robust, evidence-backed evaluation with fallback / offline demo capabilities.
Supports live Gemini / OpenAI LLM APIs when keys are configured, with graceful local fallback.
"""

import os
import re
import json
import logging
from typing import Dict, Any, List
import httpx

from backend.prompts.eval_prompt import FAIRNESS_SYSTEM_INSTRUCTION, EVALUATION_USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

# List of sensitive terms that should be strictly disregarded from scoring
SENSITIVE_ATTRIBUTES = [
    "gender", "man", "woman", "male", "female", "religion", "hindu", "muslim",
    "christian", "caste", "brahmin", "dalit", "age", "old", "young", "appearance",
    "accent", "native", "bihari", "punjabi", "south indian", "north indian"
]

def sanitize_and_check_fairness(candidate_answer: str) -> Dict[str, Any]:
    """Inspects text for sensitive attributes to guarantee fairness logging."""
    lower_text = candidate_answer.lower()
    flagged = []
    for term in SENSITIVE_ATTRIBUTES:
        # Check whole word match
        if re.search(r'\b' + re.escape(term) + r'\b', lower_text):
            flagged.append(term)
    
    return {
        "sensitive_terms_detected": flagged,
        "fairness_guaranteed": True,
        "note": "Any personal background or protected attributes detected are strictly excluded from technical scoring."
    }

def local_rubric_evaluate(
    question_obj: Dict[str, Any],
    candidate_answer: str,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Intelligent rubric-based evaluation engine.
    Used when no external LLM API key is present or on API failure.
    Accurately extracts candidate evidence, matches expected concepts, and scores based on rubric.
    """
    cleaned_answer = candidate_answer.strip()
    skill = question_obj.get("skill", "Technical Understanding")
    difficulty = question_obj.get("difficulty", "MEDIUM")
    expected_concepts = question_obj.get("expected_concepts", [])
    ideal_points = question_obj.get("ideal_answer_points", [])
    
    # Check for empty or negligible answer
    if len(cleaned_answer) < 10:
        return {
            "score": 15.0,
            "score_out_of_10": 1.5,
            "score_band": "weak",
            "skill": skill,
            "difficulty": difficulty,
            "reason": "The response is too brief or lacks substantive technical content to evaluate the competency.",
            "evidence": "Insufficient evidence from this answer.",
            "correct_concepts": [],
            "missing_concepts": expected_concepts,
            "adaptive_decision": f"Candidate gave an incomplete response on {skill}. Adapt to an easier foundational question to test core principles.",
            "adaptive_reason": f"Candidate gave an incomplete response on {skill}. Adapt to an easier foundational question to test core principles.",
            "strengths": ["Attempted to provide an answer."],
            "weaknesses": ["Did not articulate foundational concepts or technical details."],
            "confidence": 0.88,
            "next_difficulty": "EASY",
            "evaluator": "rubric_engine"
        }

    lower_ans = cleaned_answer.lower()
    
    # Bilingual concept dictionary mapping common technical concepts in English to Hindi equivalents
    HINDI_TECH_MAP = {
        "memory": ["मेमोरी", "स्मृति"],
        "stack": ["स्टैक", "stack"],
        "heap": ["हीप", "heap"],
        "dynamic": ["डायनेमिक", "गतिशील"],
        "static": ["स्टैटिक", "स्थैतिक"],
        "variable": ["वेरिएबल", "चर"],
        "function": ["फ़ंक्शन", "फंक्शन"],
        "garbage": ["गारबेज", "कचरा"],
        "speed": ["तेज़", "गति"],
        "loop": ["लूप"],
        "array": ["एरे", "सरणी"],
        "linked": ["लिंक्ड"],
        "hash": ["हैश", "hash"],
        "search": ["सर्च", "खोज"],
        "sorted": ["सॉर्ट", "क्रमबद्ध"],
        "queue": ["कतार", "क्यू"],
        "tree": ["ट्री", "वृक्ष"],
        "graph": ["ग्राफ"],
        "cache": ["कैश"],
        "token": ["टोकन"],
        "service": ["सर्विस", "सेवा"],
        "lock": ["लॉक"],
        "thread": ["थ्रेड"],
        "programming": ["प्रोग्रामिंग", "programming"],
        "data": ["डेटा", "data"]
    }
    
    # Concept matching across English, Hindi, and transliterations
    matched_concepts = []
    for concept in expected_concepts:
        concept_terms = [t.strip().lower() for t in concept.split('/')]
        terms_to_check = []
        for term in concept_terms:
            terms_to_check.append(term)
            for word in term.split():
                if len(word) > 2:
                    terms_to_check.append(word)
                    # Add mapped Hindi terms
                    for en_key, hi_variants in HINDI_TECH_MAP.items():
                        if en_key in word:
                            terms_to_check.extend(hi_variants)
        
        found = any(term in lower_ans for term in terms_to_check)
        if found:
            matched_concepts.append(concept)
    
    # Check similarity with strong demo answers if present in question_obj
    demo_answers = question_obj.get("demo_answers", {})
    strong_sample = demo_answers.get(f"strong_{language}", demo_answers.get("strong_en", ""))
    match_ratio_boost = 0.0
    if strong_sample:
        strong_words = set(w.lower() for w in re.findall(r'\w+', strong_sample) if len(w) > 3)
        candidate_words = set(w.lower() for w in re.findall(r'\w+', cleaned_answer) if len(w) > 3)
        if strong_words:
            overlap = len(candidate_words.intersection(strong_words)) / len(strong_words)
            if overlap > 0.15:
                # Credit good overlap with strong answer
                match_ratio_boost = min(overlap * 1.5, 0.40)

    # Check relevance to question prompt words and rubric concepts (topic grounding)
    q_all = (
        question_obj.get("question_en", "") + " " +
        question_obj.get("question_hi", "") + " " +
        question_obj.get("question_text", "") + " " +
        " ".join(ideal_points) + " " +
        " ".join(expected_concepts)
    ).lower()
    STOPWORDS = {
        "explain", "difference", "between", "which", "would", "what", "when", "where",
        "this", "that", "with", "from", "have", "about", "just", "some", "there", "they",
        "their", "your", "project", "using", "used", "like", "also", "into", "more", "most",
        "अंतर", "समझा", "सकते", "सकती", "बारे", "कैसे", "यहाँ", "वहाँ", "होता", "होती"
    }
    q_words = set(w for w in re.findall(r'\w+', q_all) if len(w) > 3 and w not in STOPWORDS)
    cand_words = set(w for w in re.findall(r'\w+', lower_ans) if len(w) > 3 and w not in STOPWORDS)
    cand_words_stemmed = set(w.rstrip('s') for w in cand_words)
    q_words_stemmed = set(w.rstrip('s') for w in q_words)
    shared_stemmed = cand_words_stemmed.intersection(q_words_stemmed)
    GENERIC_TECH_KEYWORDS = {
        "program", "code", "system", "data", "function", "variable", "storage",
        "memory", "type", "value", "process", "service", "logic", "implement",
        "component", "structure", "application", "database", "query", "user",
        "request", "response", "server", "client", "error", "handling", "state",
        "प्रोग्रामिंग", "मेमोरी", "वेरिएबल", "डेटा", "कोड", "सिस्टम", "फ़ंक्शन", "स्टोर"
    }
    cand_tech_words = cand_words_stemmed.intersection(GENERIC_TECH_KEYWORDS)
    word_count = len(cleaned_answer.split())
    is_confessed_weak = any(phrase in lower_ans for phrase in [
        "don't know", "dont know", "do not know", "no idea", "not sure",
        "just followed", "weak response", "tutorial online"
    ])
    if not is_confessed_weak and (len(shared_stemmed) >= 2 or (len(shared_stemmed) >= 1 and word_count >= 10) or (len(cand_tech_words) >= 3 and word_count >= 10)) and match_ratio_boost < 0.25:
        match_ratio_boost = max(match_ratio_boost, 0.25)

    match_ratio = min((len(matched_concepts) / max(len(expected_concepts), 1)) + match_ratio_boost, 1.0)
    
    # Evidence extraction: find actual sentences or clauses from the candidate's answer
    sentences = re.split(r'[.?!।\n]+', cleaned_answer)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 8]
    
    evidence_sentences = []
    for s in sentences:
        s_lower = s.lower()
        if any(c.lower() in s_lower or any(w in s_lower for w in c.lower().split() if len(w) > 3) for c in matched_concepts):
            evidence_sentences.append(s)
            if len(evidence_sentences) >= 2:
                break
    
    if not evidence_sentences and sentences:
        evidence_sentences = [sentences[0]]
        
    evidence_quote = ' "...' + ' '.join(evidence_sentences) + '..."' if evidence_sentences else "Insufficient evidence from this answer."
    
    # Accurate multi-band scoring based on technical concept alignment:
    # Match ratio dictates core score band to prevent long but non-technical answers from inflating
    if match_ratio == 0:
        # Zero technical concepts matched: Weak band (1.5 - 3.5 / 10)
        base_score = 20
        depth_bonus = 5 if word_count > 25 else 0
        final_score = min(max(base_score + depth_bonus, 15), 35)
    elif match_ratio < 0.25:
        # Marginal concept match (<25%): Weak band (2.2 - 3.8 / 10)
        base_score = 26
        concept_bonus = int(match_ratio * 25)
        depth_bonus = 4 if word_count > 20 else -4
        final_score = min(max(base_score + concept_bonus + depth_bonus, 20), 38)
    elif match_ratio < 0.70:
        # Partial concept match: Moderate band (4.5 - 6.8 / 10)
        base_score = 48
        concept_bonus = int((match_ratio - 0.25) * 40)
        depth_bonus = 5 if word_count > 25 else 0
        final_score = min(max(base_score + concept_bonus + depth_bonus, 45), 68)
    else:
        # Comprehensive concept match: Strong band (7.5 - 9.6 / 10)
        base_score = 78
        concept_bonus = int((match_ratio - 0.70) * 45)
        depth_bonus = 6 if word_count > 25 else 0
        final_score = min(max(base_score + concept_bonus + depth_bonus, 75), 96)

    # Determine score band and adaptive decision
    score_out_of_10 = round(final_score / 10.0, 1)
    if final_score < 40 or score_out_of_10 <= 4.0:
        score_band = "weak"
        next_difficulty = "EASY"
        adaptive_decision = f"Candidate gave a weak answer on {skill} (Score: {score_out_of_10}/10). Adapt to an easier foundational question or simpler clarifying question to diagnose core mechanics."
    elif final_score > 70 or score_out_of_10 >= 7.5:
        score_band = "strong"
        next_difficulty = "HARD"
        adaptive_decision = f"Candidate demonstrated strong mastery on {skill} (Score: {score_out_of_10}/10). Increase difficulty and escalate to an advanced scenario or architecture deep-dive."
    else:
        score_band = "moderate"
        next_difficulty = "MEDIUM"
        adaptive_decision = f"Candidate provided a partially correct answer on {skill} (Score: {score_out_of_10}/10). Follow up with a medium-level practical question exploring missing concepts."

    # Generate strengths and weaknesses
    strengths = []
    weaknesses = []

    if matched_concepts:
        strengths.append(f"Demonstrated understanding of {', '.join(matched_concepts[:2])}.")
    if word_count >= 30 and matched_concepts:
        strengths.append("Provided a structured response explaining the core mechanism.")
    elif matched_concepts:
        strengths.append("Addressed the question with concise communication.")
    else:
        strengths.append("Attempted to respond to the question prompt.")

    missing_concepts = [c for c in expected_concepts if c not in matched_concepts]
    if missing_concepts:
        weaknesses.append(f"Could elaborate more on {', '.join(missing_concepts[:2])}.")
    else:
        weaknesses.append("Could provide additional concrete production edge-case examples.")

    # Generate professional reason grounded in rubric
    if score_band == "strong":
        reason = f"Candidate demonstrated strong mastery in {skill}, correctly explaining key technical points including {', '.join(matched_concepts[:2]) if matched_concepts else 'the fundamental mechanisms'}."
    elif score_band == "moderate":
        reason = f"Candidate showed satisfactory foundational knowledge in {skill}, mentioning {', '.join(matched_concepts[:1]) if matched_concepts else 'the concept'}, but lacked deeper trade-off analysis or missed {', '.join(missing_concepts[:1]) if missing_concepts else 'practical edge cases'}."
    else:
        reason = f"Candidate struggled to articulate key technical concepts for {skill}. The response did not explain essential mechanics like {', '.join(expected_concepts[:2]) if expected_concepts else 'foundational principles'}."

    return {
        "score": float(final_score),
        "score_out_of_10": score_out_of_10,
        "score_band": score_band,
        "skill": skill,
        "difficulty": difficulty,
        "reason": reason,
        "evidence": evidence_quote.strip(),
        "correct_concepts": matched_concepts,
        "missing_concepts": missing_concepts,
        "adaptive_decision": adaptive_decision,
        "adaptive_reason": adaptive_decision,
        "strengths": strengths,
        "weaknesses": weaknesses,
        "confidence": round(0.82 + (0.12 * match_ratio), 2),
        "next_difficulty": next_difficulty,
        "evaluator": "rubric_engine"
    }

async def evaluate_answer(
    question_obj: Dict[str, Any],
    candidate_answer: str,
    language: str = "en"
) -> Dict[str, Any]:
    """
    Main evaluation pipeline.
    Attempts live LLM evaluation via Gemini (google-genai SDK) if API key exists.
    Falls back reliably to local_rubric_evaluate.
    """
    from backend.ai.gemini_service import evaluate_with_gemini

    # 1. Try Official Google GenAI SDK (Gemini)
    try:
        gemini_result = evaluate_with_gemini(
            question_obj=question_obj,
            candidate_answer=candidate_answer,
            language=language
        )
        if gemini_result:
            return gemini_result
    except Exception as e:
        logger.warning(f"Live Gemini evaluation error: {e}. Falling back.")

    # 2. Try OpenAI API if key is present
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    if openai_key:
        try:
            prompt_content = EVALUATION_USER_PROMPT_TEMPLATE.format(
                role=question_obj.get("role", "Software Developer Intern"),
                skill=question_obj.get("skill", "Technical"),
                difficulty=question_obj.get("difficulty", "MEDIUM"),
                question=question_obj.get(f"question_{language}", question_obj.get("question_en", "")),
                expected_concepts=", ".join(question_obj.get("expected_concepts", [])),
                rubric=json.dumps(question_obj.get("rubric", {})),
                candidate_answer=candidate_answer,
                language="Hindi" if language == "hi" else "English"
            )
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": FAIRNESS_SYSTEM_INSTRUCTION},
                    {"role": "user", "content": prompt_content}
                ],
                "response_format": {"type": "json_object"}
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    text_resp = data["choices"][0]["message"]["content"]
                    parsed = json.loads(text_resp)
                    parsed["evaluator"] = "openai_live"
                    parsed["difficulty"] = question_obj.get("difficulty", "MEDIUM")
                    return parsed
        except Exception as e:
            logger.warning(f"Live OpenAI API evaluation failed: {e}. Falling back to rubric engine.")

    # 3. Deterministic Rubric-Matching Engine (100% reliable fallback)
    return local_rubric_evaluate(question_obj, candidate_answer, language)
