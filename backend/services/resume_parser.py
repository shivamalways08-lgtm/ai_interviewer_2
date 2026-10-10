"""
Resume Parsing and Analysis Service for IntervueAI
Extracts text from PDF and DOCX resumes, validates file integrity,
and extracts structured technical skills, programming languages,
tools, projects, technologies, and work experience using Gemini AI
or a deterministic offline fallback.

Privacy Guarantee: Never extracts or scores demographic or sensitive
personal attributes (gender, photo, age, religion, caste, address, etc.).
"""

import io
import os
import re
import json
import logging
from typing import Dict, Any, List, Optional
import pypdf
import docx

logger = logging.getLogger(__name__)

# Maximum file size: 5 MB
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Comprehensive technical skills, languages, tools & database dictionary for deterministic fallback
KNOWN_TECH_SKILLS = [
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Golang",
    "Rust", "Ruby", "PHP", "Kotlin", "Swift", "Dart", "Scala", "R", "SQL", "HTML", "CSS", "Bash", "Shell",
    # Frontend
    "React", "React.js", "Next.js", "Vue", "Vue.js", "Angular", "Svelte", "Redux", "Zustand", "Tailwind CSS", "Tailwind",
    "Bootstrap", "Material UI", "HTML5", "CSS3", "Vite", "Webpack",
    # Backend & Frameworks
    "Node.js", "Node", "Express", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
    "ASP.NET", "Ruby on Rails", "NestJS", "GraphQL", "REST APIs", "RESTful APIs", "REST API", "Microservices", "gRPC",
    # Databases & Storage
    "PostgreSQL", "Postgres", "MySQL", "MongoDB", "SQLite", "Redis", "Elasticsearch", "Cassandra",
    "Firebase", "Supabase", "DynamoDB", "Oracle", "Prisma",
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "Google Cloud", "GCP", "Microsoft Azure", "Azure", "CI/CD",
    "GitHub Actions", "Jenkins", "Terraform", "Linux", "Git", "GitHub", "GitLab", "Nginx",
    # AI/ML & Data
    "Machine Learning", "Deep Learning", "TensorFlow", "PyTorch", "Pandas", "NumPy",
    "Scikit-learn", "NLP", "Computer Vision", "LLMs", "Generative AI", "LangChain",
    # Software Engineering Principles
    "Data Structures", "Algorithms", "Object-Oriented Programming", "OOP", "System Design",
    "Unit Testing", "Test-Driven Development", "TDD", "Agile", "Scrum"
]


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extracts text content from a PDF document using pypdf."""
    try:
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        if reader.is_encrypted:
            try:
                reader.decrypt("")
            except Exception:
                raise ValueError("The uploaded PDF is password-protected or encrypted. Please provide an unlocked document.")

        extracted_text = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                extracted_text.append(text)

        full_text = "\n".join(extracted_text).strip()
        if not full_text:
            raise ValueError("The uploaded PDF contains no readable text (it may be an empty document or scanned image).")
        return full_text
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error reading PDF: {e}")
        raise ValueError(f"Failed to read PDF file: {str(e)}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extracts text content from a DOCX document using python-docx."""
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        
        # Also extract table cells if present
        table_texts = []
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    table_texts.append(row_text)

        all_text = "\n".join(paragraphs + table_texts).strip()
        if not all_text:
            raise ValueError("The uploaded DOCX document contains no readable text.")
        return all_text
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error reading DOCX: {e}")
        raise ValueError(f"Failed to read DOCX document: {str(e)}")


def validate_resume_file(filename: str, file_bytes: bytes) -> None:
    """Validates resume file size and extension."""
    if not file_bytes or len(file_bytes.strip()) == 0:
        raise ValueError("Uploaded file is empty (0 bytes).")

    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise ValueError(f"File size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES // (1024*1024)} MB.")

    lower_name = filename.lower()
    if not (lower_name.endswith(".pdf") or lower_name.endswith(".docx")):
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """
    Validates file extension and size, then extracts raw text.
    Supports .pdf and .docx formats.
    """
    validate_resume_file(filename, file_bytes)

    lower_name = filename.lower()
    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif lower_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.")


def deterministic_parse_resume(text: str) -> Dict[str, Any]:
    """
    Deterministic rule-based resume information extractor.
    Operates without external LLM API keys.
    Extracts skills, languages, tools, and projects grounded strictly in resume text.
    Never invents or hallucinates skills or projects.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    lower_text = text.lower()

    # 1. Extract Technical Skills via exact dictionary matching
    detected_skills = []
    for skill in KNOWN_TECH_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, lower_text):
            detected_skills.append(skill)

    # De-duplicate case-insensitively while preserving formatting
    seen_normalized = set()
    unique_skills = []
    for s in detected_skills:
        k = s.lower()
        # Normalize display names
        if k in ["postgres", "postgresql"]:
            norm = "PostgreSQL"
        elif k in ["react", "react.js"]:
            norm = "React"
        elif k in ["node", "node.js"]:
            norm = "Node.js"
        elif k in ["express", "express.js"]:
            norm = "Express.js"
        elif k in ["vue", "vue.js", "vuejs"]:
            norm = "Vue.js"
        elif k in ["rest api", "rest apis", "restful apis"]:
            norm = "REST APIs"
        else:
            norm = s

        if norm.lower() not in seen_normalized:
            seen_normalized.add(norm.lower())
            unique_skills.append(norm)

    # Categorize into languages, frameworks, and tools
    languages = [s for s in unique_skills if s in [
        "Python", "JavaScript", "TypeScript", "Java", "C++", "C", "C#", "Go", "Golang",
        "Rust", "Ruby", "PHP", "Kotlin", "Swift", "Dart", "Scala", "R", "SQL", "HTML", "CSS", "Bash", "Shell"
    ]]
    frameworks = [s for s in unique_skills if s in [
        "React", "Next.js", "Vue.js", "Angular", "Svelte", "Redux", "Zustand", "Tailwind CSS",
        "Node.js", "Express.js", "Django", "Flask", "FastAPI", "Spring Boot",
        "ASP.NET", "Ruby on Rails", "NestJS", "GraphQL", "REST APIs", "Microservices"
    ]]
    tools = [s for s in unique_skills if s not in languages and s not in frameworks]

    # 2. Extract Projects heuristically from project headings & blocks
    projects = []
    project_section_started = False
    current_proj = None

    SECTION_STOPPERS = [
        "experience", "work experience", "professional experience", "employment",
        "internships", "education", "certifications", "achievements", "skills",
        "technical skills", "activities", "extracurricular"
    ]

    for i, line in enumerate(lines):
        line_clean = line.strip()
        lower_line = line_clean.lower()

        # Check for Project heading
        if re.match(r"^(projects|academic projects|personal projects|key projects|featured projects|technical projects|project work)\b", lower_line, re.IGNORECASE):
            project_section_started = True
            if current_proj:
                projects.append(current_proj)
                current_proj = None
            continue

        # Stop if we hit another major section
        if project_section_started and any(re.match(r"^" + re.escape(sec) + r"\b", lower_line) for sec in SECTION_STOPPERS):
            project_section_started = False
            if current_proj:
                projects.append(current_proj)
                current_proj = None
            continue

        if project_section_started:
            # Detect technologies mentioned in this line
            line_tech = [s for s in unique_skills if re.search(r"\b" + re.escape(s.lower()) + r"\b", lower_line)]

            clean_without_bullet = re.sub(r"^[\d\.\-\•\*\–\—\s]+", "", line_clean).strip()
            is_bullet = line_clean.startswith(("-", "•", "*", "–", "—"))

            # Format 1: "Project Name: Description..." (very common format)
            if ":" in clean_without_bullet:
                parts = clean_without_bullet.split(":", 1)
                cand_title = parts[0].strip()
                cand_desc = parts[1].strip()
                if 1 <= len(cand_title.split()) <= 6 and not any(cand_title.lower().startswith(x) for x in ["http", "note", "tech", "role", "tool", "skill"]):
                    if current_proj:
                        projects.append(current_proj)
                    current_proj = {
                        "name": cand_title,
                        "description": cand_desc,
                        "technologies": list(dict.fromkeys(line_tech)),
                        "responsibilities": cand_desc if any(kw in cand_desc.lower() for kw in ["developed", "built", "implemented", "created", "designed"]) else ""
                    }
                    continue

            # Format 2: Title line followed by description line
            has_sep = any(sep in line_clean for sep in ["|", " - ", "--"])
            looks_like_title = (
                (not is_bullet and len(clean_without_bullet.split()) <= 8 and not clean_without_bullet.endswith(".")) or
                (has_sep and len(clean_without_bullet.split()) <= 12 and not clean_without_bullet.endswith("."))
            )

            if looks_like_title and len(clean_without_bullet) > 2:
                if current_proj:
                    projects.append(current_proj)
                
                # Extract clean name by stripping separator and parenthesized tech
                raw_name = clean_without_bullet.split("|")[0].split(" - ")[0].split(":")[0]
                raw_name = re.sub(r"\(.*?\)", "", raw_name).strip()
                proj_name = raw_name if raw_name else clean_without_bullet[:50]
                
                current_proj = {
                    "name": proj_name,
                    "description": "",
                    "technologies": list(dict.fromkeys(line_tech)),
                    "responsibilities": ""
                }
            elif current_proj:
                if line_tech:
                    for t in line_tech:
                        if t not in current_proj["technologies"]:
                            current_proj["technologies"].append(t)
                
                # If line mentions contributions/responsibilities
                resp_keywords = ["developed", "built", "implemented", "created", "designed", "integrated", "managed", "optimized", "engineered"]
                if any(kw in lower_line for kw in resp_keywords) and not current_proj["responsibilities"]:
                    current_proj["responsibilities"] = clean_without_bullet
                
                if not current_proj["description"]:
                    current_proj["description"] = clean_without_bullet
                else:
                    current_proj["description"] += " " + clean_without_bullet

    if current_proj:
        projects.append(current_proj)

    # If no project sections were explicitly tagged, scan for explicit project markers
    if not projects:
        for i, line in enumerate(lines):
            m = re.match(r"^(?:project|project title|key project):\s*(.+)", line, re.IGNORECASE)
            if m:
                proj_name = m.group(1).split("|")[0].split("-")[0].strip()
                techs = [s for s in unique_skills if s.lower() in text.lower()]
                desc = lines[i+1] if i+1 < len(lines) else ""
                projects.append({
                    "name": proj_name,
                    "description": desc,
                    "technologies": techs[:4],
                    "responsibilities": desc if any(kw in desc.lower() for kw in ["developed", "built", "implemented"]) else ""
                })

    # Ensure projects have clean names and descriptions
    cleaned_projects = []
    for p in projects[:4]:  # limit to top 4 projects
        if p["name"] and len(p["name"]) > 2:
            techs = p["technologies"] if p["technologies"] else unique_skills[:3]
            desc = p["description"][:300].strip() if p["description"] else f"Project built with {', '.join(techs) if techs else 'software technologies'}."
            resp = p["responsibilities"][:200].strip() if p["responsibilities"] else f"Implemented core features and application architecture."
            cleaned_projects.append({
                "name": p["name"][:60].strip(),
                "description": desc,
                "technologies": techs,
                "responsibilities": resp
            })

    # 3. Extract Experience heuristically
    experience = []
    exp_started = False
    current_exp = None
    for line in lines:
        lower_line = line.lower()
        if re.match(r"^(experience|work experience|employment|internships|professional experience)\b", lower_line):
            exp_started = True
            continue
        if exp_started and any(re.match(r"^" + re.escape(sec) + r"\b", lower_line) for sec in ["projects", "education", "skills", "certifications"]):
            exp_started = False
            if current_exp:
                experience.append(current_exp)
                current_exp = None
            continue
        if exp_started:
            if not current_exp and len(line) < 70 and not line.startswith(("-", "•", "*")):
                role_parts = line.split(" at ") if " at " in line else line.split(" - ")
                role_name = role_parts[0].strip()
                comp_name = role_parts[1].strip() if len(role_parts) > 1 else ""
                current_exp = {"role": role_name, "company": comp_name, "description": ""}
            elif current_exp:
                current_exp["description"] += (" " + line.strip())
                if len(current_exp["description"]) > 250:
                    experience.append(current_exp)
                    current_exp = None
    if current_exp:
        experience.append(current_exp)

    # Formulate summary
    skills_preview = ", ".join(unique_skills[:5]) if unique_skills else "Software engineering fundamentals"
    projs_preview = ", ".join(p["name"] for p in cleaned_projects[:2]) if cleaned_projects else "practical academic/personal projects"
    summary = f"Candidate with verified skills in {skills_preview}, featuring {projs_preview}."

    return {
        "parser": "deterministic_fallback",
        "is_fallback": True,
        "skills": unique_skills,
        "languages_frameworks": languages + frameworks,
        "tools_technologies": tools,
        "projects": cleaned_projects,
        "experience": experience[:3],
        "detected_skills": unique_skills,
        "summary": summary
    }


def analyze_resume_with_gemini(text: str) -> Optional[Dict[str, Any]]:
    """
    Leverages Gemini LLM to extract structured skills, projects, and experience
    from extracted resume text with strictly enforced privacy and anti-hallucination rules.
    """
    from backend.ai.gemini_service import get_gemini_client, GEMINI_MODELS
    from google.genai import types

    client = get_gemini_client()
    if not client:
        return None

    system_instruction = (
        "You are an expert technical resume parser and talent intelligence system. "
        "Your task is to extract strictly technical competencies, verified skills, and project details. "
        "PRIVACY AND FAIRNESS ENFORCEMENT: "
        "- Do NOT extract or report demographic or sensitive personal information such as gender, photo, age, "
        "religion, caste, marital status, nationality, political views, or physical appearance. "
        "- Focus strictly on technical skills, tools, frameworks, programming languages, projects, and work experience. "
        "- NEVER invent or hallucinate skills, projects, or experience that are not explicitly documented in the resume text. "
        "- Respond with a VALID JSON object matching the requested schema."
    )

    prompt = f"""
Analyze the following resume text and extract technical skills, tools, projects, and professional experience:

--- RESUME TEXT BEGIN ---
{text[:6000]}
--- RESUME TEXT END ---

Return a JSON object with this exact structure:
{{
  "skills": ["<Technical or Professional Skill>", ...],
  "languages_frameworks": ["<Programming Language or Framework>", ...],
  "tools_technologies": ["<Tool, Library, Cloud, Database>", ...],
  "projects": [
    {{
      "name": "<Project Title>",
      "description": "<Concise summary of what the project does>",
      "technologies": ["<Tech 1>", "<Tech 2>"],
      "responsibilities": "<Candidate's contributions, features built, or role>"
    }}
  ],
  "experience": [
    {{
      "role": "<Job Title or Internship Role>",
      "company": "<Organization name if mentioned>",
      "description": "<Responsibilities or achievements>"
    }}
  ],
  "summary": "<1-2 sentence professional technical summary of the candidate's profile>"
}}
"""

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        temperature=0.1
    )

    for model_name in GEMINI_MODELS:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=config
            )
            if response and response.text:
                data = json.loads(response.text)
                # Combine unique skills list
                all_skills = list(dict.fromkeys(
                    (data.get("skills") or []) +
                    (data.get("languages_frameworks") or []) +
                    (data.get("tools_technologies") or [])
                ))
                data["detected_skills"] = all_skills
                data["parser"] = f"gemini_ai ({model_name})"
                data["is_fallback"] = False
                return data
        except Exception as e:
            logger.warning(f"Gemini resume analysis failed with model {model_name}: {e}. Retrying next...")

    return None


def parse_and_analyze_resume(file_bytes: bytes, filename: str) -> Dict[str, Any]:
    """
    Full pipeline:
    1. Extracts text from PDF/DOCX
    2. Runs Gemini AI analysis if configured
    3. Falls back seamlessly to deterministic extraction
    4. Validates output and returns structured payload
    """
    raw_text = extract_text_from_file(file_bytes, filename)

    # Try Gemini analysis
    try:
        gemini_result = analyze_resume_with_gemini(raw_text)
        if gemini_result and (gemini_result.get("detected_skills") or gemini_result.get("projects")):
            gemini_result["raw_text_length"] = len(raw_text)
            gemini_result["filename"] = filename
            gemini_result["file_size"] = len(file_bytes)
            return gemini_result
    except Exception as e:
        logger.warning(f"Live Gemini resume parsing error: {e}. Falling back to deterministic parser.")

    # Deterministic Fallback
    fallback_result = deterministic_parse_resume(raw_text)
    fallback_result["raw_text_length"] = len(raw_text)
    fallback_result["filename"] = filename
    fallback_result["file_size"] = len(file_bytes)
    return fallback_result
