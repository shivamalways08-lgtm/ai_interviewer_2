import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "intervueai.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=30000;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Candidates table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        role TEXT NOT NULL,
        language TEXT NOT NULL DEFAULT 'en',
        interview_mode TEXT NOT NULL DEFAULT 'text',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Consent table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS consents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id TEXT NOT NULL,
        interview_id TEXT,
        consent_status TEXT NOT NULL DEFAULT 'granted',
        policy_version TEXT NOT NULL DEFAULT 'v1.2',
        categories_disclosed TEXT,
        read_understood INTEGER DEFAULT 1,
        skill_assessment_agreed INTEGER DEFAULT 1,
        consent_text TEXT NOT NULL,
        agreed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fairness_acknowledged INTEGER DEFAULT 1,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    );
    """)

    # Interviews table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id TEXT PRIMARY KEY,
        candidate_id TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'in_progress',
        current_difficulty TEXT NOT NULL DEFAULT 'MEDIUM',
        current_question_index INTEGER NOT NULL DEFAULT 0,
        total_questions INTEGER DEFAULT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        deadline_at TIMESTAMP,
        completed_at TIMESTAMP,
        overall_score REAL,
        consecutive_weak_answers INTEGER DEFAULT 0,
        termination_reason TEXT DEFAULT 'NORMAL',
        focus_violations_count INTEGER DEFAULT 0,
        focus_violation_at TIMESTAMP,
        ai_recommendation TEXT,
        recruiter_decision TEXT,
        recruiter_notes TEXT,
        decision_updated_at TIMESTAMP,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id)
    );
    """)

    # Turns / Questions & Answers evaluated in each step
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_turns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        question_text TEXT NOT NULL,
        language TEXT NOT NULL,
        skill TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        candidate_answer TEXT,
        score REAL,
        reason TEXT,
        evidence TEXT,
        strengths_json TEXT,
        weaknesses_json TEXT,
        confidence REAL,
        evaluator TEXT DEFAULT 'rubric_engine',
        follow_up_suggested TEXT,
        answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (interview_id) REFERENCES interviews(id)
    );
    """)

    # Graceful migration for existing databases
    try:
        cursor.execute("ALTER TABLE interview_turns ADD COLUMN evaluator TEXT DEFAULT 'rubric_engine'")
    except Exception:
        pass

    try:
        cursor.execute("ALTER TABLE interview_turns ADD COLUMN follow_up_suggested TEXT")
    except Exception:
        pass

    # Graceful migrations for consents table
    for col, col_def in [
        ("interview_id", "TEXT"),
        ("consent_status", "TEXT DEFAULT 'granted'"),
        ("policy_version", "TEXT DEFAULT 'v1.2'"),
        ("categories_disclosed", "TEXT"),
        ("read_understood", "INTEGER DEFAULT 1"),
        ("skill_assessment_agreed", "INTEGER DEFAULT 1"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE consents ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    # Graceful migrations for interviews table
    for col, col_def in [
        ("deadline_at", "TIMESTAMP"),
        ("consecutive_weak_answers", "INTEGER DEFAULT 0"),
        ("termination_reason", "TEXT DEFAULT 'NORMAL'"),
        ("focus_violations_count", "INTEGER DEFAULT 0"),
        ("focus_violation_at", "TIMESTAMP"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE interviews ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    # Ensure total_questions column in interviews table is nullable for dynamic questioning
    try:
        cursor.execute("PRAGMA table_info(interviews)")
        cols = cursor.fetchall()
        tq_col = next((c for c in cols if c["name"] == "total_questions"), None)
        if tq_col and tq_col["notnull"] == 1:
            cursor.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interviews_migrated (
                    id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'in_progress',
                    current_difficulty TEXT NOT NULL DEFAULT 'MEDIUM',
                    current_question_index INTEGER NOT NULL DEFAULT 0,
                    total_questions INTEGER DEFAULT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    deadline_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    overall_score REAL,
                    consecutive_weak_answers INTEGER DEFAULT 0,
                    termination_reason TEXT DEFAULT 'NORMAL',
                    focus_violations_count INTEGER DEFAULT 0,
                    focus_violation_at TIMESTAMP,
                    ai_recommendation TEXT,
                    recruiter_decision TEXT,
                    recruiter_notes TEXT,
                    decision_updated_at TIMESTAMP,
                    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
                );
            """)
            cursor.execute("""
                INSERT INTO interviews_migrated (
                    id, candidate_id, status, current_difficulty, current_question_index,
                    total_questions, started_at, deadline_at, completed_at, overall_score,
                    consecutive_weak_answers, termination_reason, focus_violations_count,
                    focus_violation_at, ai_recommendation, recruiter_decision,
                    recruiter_notes, decision_updated_at
                )
                SELECT 
                    id, candidate_id, status, current_difficulty, current_question_index,
                    total_questions, started_at, deadline_at, completed_at, overall_score,
                    COALESCE(consecutive_weak_answers, 0), COALESCE(termination_reason, 'NORMAL'),
                    0, NULL,
                    ai_recommendation, recruiter_decision, recruiter_notes, decision_updated_at
                FROM interviews;
            """)
            cursor.execute("DROP TABLE interviews;")
            cursor.execute("ALTER TABLE interviews_migrated RENAME TO interviews;")
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
    except Exception:
        pass

    # Ensure all columns exist on interviews regardless of prior migrations
    for col, col_def in [
        ("deadline_at", "TIMESTAMP"),
        ("consecutive_weak_answers", "INTEGER DEFAULT 0"),
        ("termination_reason", "TEXT DEFAULT 'NORMAL'"),
        ("focus_violations_count", "INTEGER DEFAULT 0"),
        ("focus_violation_at", "TIMESTAMP"),
        ("resume_id", "TEXT"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE interviews ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    # Ensure interview_turns has timing and adaptive reasoning columns
    for col, col_def in [
        ("response_time_seconds", "REAL DEFAULT 0.0"),
        ("adaptive_reason", "TEXT"),
        ("question_type", "TEXT DEFAULT 'competency'"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE interview_turns ADD COLUMN {col} {col_def}")
        except Exception:
            pass

    # Resumes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resumes (
        id TEXT PRIMARY KEY,
        candidate_id TEXT,
        filename TEXT NOT NULL,
        file_size INTEGER NOT NULL,
        file_type TEXT NOT NULL,
        extracted_text TEXT,
        parsed_data_json TEXT NOT NULL,
        parser_type TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Skill aggregations per interview
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skill_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id TEXT NOT NULL,
        skill TEXT NOT NULL,
        score REAL NOT NULL,
        evidence TEXT NOT NULL,
        reason TEXT NOT NULL,
        turns_count INTEGER DEFAULT 1,
        FOREIGN KEY (interview_id) REFERENCES interviews(id)
    );
    """)

    conn.commit()
    conn.close()

try:
    init_db()
except Exception:
    pass

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
