"""
IntervueAI - Backend Application Entry Point
FastAPI server providing adaptive interview orchestration, multilingual evaluation,
and recruiter decision management.
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables
load_dotenv()

from backend.database.database import init_db
from backend.api.routes import router, seed_demo_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize SQLite DB and seed initial demo data for instant dashboard preview
    init_db()
    seed_demo_data()
    print(">>> IntervueAI Backend successfully started. SQLite DB ready and seeded.")
    yield

app = FastAPI(
    title="IntervueAI - Adaptive AI Interviewer API",
    description="Adaptive First-Round Technical Interview Engine supporting English and Hindi with Evidence-Based Scoring.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits local development on Vite / preview ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def root():
    return {
        "project": "IntervueAI",
        "tagline": "Fair interviews. Smarter evaluation. Every candidate gets a voice.",
        "status": "online",
        "docs_url": "/docs",
        "health_check": "/api/health"
    }

@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "llm_gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "llm_openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "fallback_mode_ready": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
