"""
Unit Tests for IntervueAI Backend
Tests adaptive engine, evidence-based scoring, fairness checks, and multilingual support.
"""

import pytest
from backend.services.adaptive_engine import (
    calculate_next_difficulty,
    select_next_question,
    SKILL_SEQUENCE
)
from backend.ai.evaluation_engine import (
    local_rubric_evaluate,
    sanitize_and_check_fairness
)
from backend.data.question_bank import get_question_by_id, QUESTION_BANK

def test_adaptive_difficulty_transitions():
    """Verify that score thresholds adjust difficulty accurately."""
    # From MEDIUM:
    assert calculate_next_difficulty("MEDIUM", 85) == "HARD"
    assert calculate_next_difficulty("MEDIUM", 55) == "MEDIUM"
    assert calculate_next_difficulty("MEDIUM", 30) == "EASY"

    # From HARD:
    assert calculate_next_difficulty("HARD", 90) == "HARD"
    assert calculate_next_difficulty("HARD", 60) == "HARD"
    assert calculate_next_difficulty("HARD", 25) == "MEDIUM"

    # From EASY:
    assert calculate_next_difficulty("EASY", 20) == "EASY"
    assert calculate_next_difficulty("EASY", 50) == "EASY"
    assert calculate_next_difficulty("EASY", 80) == "MEDIUM"

def test_question_selection_and_language():
    """Verify adaptive question selection produces Hindi and English text."""
    q_en = select_next_question(
        interview_turn_index=0,
        current_difficulty="MEDIUM",
        asked_question_ids=[],
        role="Software Developer Intern",
        language="en"
    )
    assert q_en is not None
    assert q_en["skill"] == "Programming Fundamentals"
    assert "Stack and Heap" in q_en["question_text"] or "pass by value" in q_en["question_text"]

    q_hi = select_next_question(
        interview_turn_index=0,
        current_difficulty="MEDIUM",
        asked_question_ids=[],
        role="Software Developer Intern",
        language="hi"
    )
    assert q_hi is not None
    assert ("मेमोरी" in q_hi["question_text"]) or ("अंतर" in q_hi["question_text"])

def test_evidence_extraction_and_scoring():
    """Verify that candidate quotes are extracted as evidence and scores reflect content."""
    q_obj = get_question_by_id("prog_med_1")
    assert q_obj is not None

    sample_answer = (
        "Stack memory is used for static allocation and local variables following LIFO, which is very fast. "
        "Heap memory is used for dynamic memory allocation for objects that live across functions, requiring garbage collection."
    )

    eval_res = local_rubric_evaluate(q_obj, sample_answer, language="en")
    assert eval_res["score"] >= 75
    assert eval_res["skill"] == "Programming Fundamentals"
    assert "LIFO" in eval_res["evidence"] or "Stack" in eval_res["evidence"]
    assert len(eval_res["strengths"]) > 0
    assert eval_res["next_difficulty"] == "HARD"

def test_hindi_evaluation_fairness():
    """Verify that a technical answer in Hindi is evaluated fairly on technical merit."""
    q_obj = get_question_by_id("prog_med_1")
    assert q_obj is not None

    hindi_answer = (
        "Stack मेमोरी LIFO सिद्धांत पर काम करती है और लोकल वेरिएबल्स के लिए होती है जो बहुत तेज़ है। "
        "Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है और इसे गारबेज कलेक्टर से फ्री किया जाता है।"
    )

    eval_res = local_rubric_evaluate(q_obj, hindi_answer, language="hi")
    assert eval_res["score"] >= 70
    assert "LIFO" in eval_res["evidence"] or "Stack" in eval_res["evidence"] or "मेमोरी" in eval_res["evidence"]

def test_fairness_protected_attributes_check():
    """Verify that protected attributes are flagged and excluded from influencing scores."""
    sample_text = "As a young female candidate from Delhi, I declare variables using let and const."
    fairness = sanitize_and_check_fairness(sample_text)
    assert fairness["fairness_guaranteed"] is True
    assert "female" in fairness["sensitive_terms_detected"] or "young" in fairness["sensitive_terms_detected"]
