import React from 'react';
import { 
  Sparkles, 
  ArrowRight, 
  ShieldCheck, 
  Languages, 
  TrendingUp, 
  FileCheck, 
  UserCheck, 
  Code2, 
  Mic, 
  CheckCircle2,
  Cpu,
  Layers,
  Award
} from 'lucide-react';

export default function LandingPage({ onStartInterview, onOpenRecruiter, onLaunchDemo }) {
  return (
    <div className="container" style={{ paddingTop: '50px', paddingBottom: '80px' }}>
      
      {/* Hero Section */}
      <div style={{ textAlign: 'center', maxWidth: '840px', margin: '0 auto 60px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '20px' }}>
          <span className="badge badge-purple" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
            <Sparkles size={14} /> Hackathon Edition 2026
          </span>
          <span className="badge badge-cyan" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
            <Languages size={14} /> English + हिंदी Supported
          </span>
        </div>

        <h1 style={{ fontSize: '3.4rem', fontWeight: 800, lineHeight: 1.15, marginBottom: '22px', letterSpacing: '-0.03em' }}>
          Fair interviews. Smarter evaluation. <br />
          <span className="text-gradient">Every candidate gets a voice.</span>
        </h1>

        <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: '34px' }}>
          An adaptive first-round technical interview platform that dynamically scales question difficulty,
          evaluates substantive technical depth in English or Hindi, cites verifiable evidence from candidate answers,
          and ensures human recruiters make the final hiring decisions.
        </p>

        {/* CTA Button Group */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <button 
            className="btn btn-primary btn-lg" 
            onClick={onStartInterview}
            style={{ fontSize: '1.05rem', padding: '14px 28px' }}
          >
            Start Candidate Interview
            <ArrowRight size={18} />
          </button>

          <button 
            className="btn btn-secondary btn-lg"
            onClick={onLaunchDemo}
            style={{ fontSize: '1.05rem', padding: '14px 24px' }}
          >
            <Sparkles size={18} color="#818cf8" />
            1-Click Interactive Demo
          </button>

          <button 
            className="btn btn-secondary btn-lg"
            onClick={onOpenRecruiter}
            style={{ fontSize: '1.05rem', padding: '14px 24px' }}
          >
            <UserCheck size={18} color="#34d399" />
            Recruiter Dashboard
          </button>
        </div>
      </div>

      {/* Live Active Role Highlight */}
      <div className="glass-panel" style={{ padding: '24px 30px', marginBottom: '70px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '18px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#818cf8'
          }}>
            <Code2 size={26} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Software Developer Intern</h3>
              <span className="badge badge-easy" style={{ fontSize: '0.72rem' }}>Live Assessment Ready</span>
            </div>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Evaluates 5 competencies: Programming Fundamentals, Problem Solving, DSA, Technical Understanding, and Communication.
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Future roles:</span>
          <span className="badge badge-secondary" style={{ background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)' }}>Data Analyst</span>
          <span className="badge badge-secondary" style={{ background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)' }}>Hardware Engineer</span>
          <span className="badge badge-secondary" style={{ background: 'rgba(255,255,255,0.04)', color: 'var(--text-muted)' }}>Marketing Intern</span>
        </div>
      </div>

      {/* ======================================================== */}
      {/* SECTION 31: "Why IntervueAI?" 5 CORE DIFFERENTIATORS */}
      {/* ======================================================== */}
      <div style={{ marginBottom: '80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '45px' }}>
          <span className="badge badge-purple" style={{ marginBottom: '10px' }}>Built For Hackathon Excellence</span>
          <h2 style={{ fontSize: '2.4rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
            Why <span className="text-gradient">IntervueAI?</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', maxWidth: '640px', margin: '8px auto 0' }}>
            Five foundational pillars designed from the ground up to solve bias, language barriers, and opaque scoring.
          </p>
        </div>

        <div className="grid-5">
          {/* 1. Adaptive Questioning */}
          <div className="glass-panel" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#818cf8',
              marginBottom: '16px'
            }}>
              <TrendingUp size={22} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px' }}>
              1. Adaptive Questioning
            </h4>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>
              Questions dynamically scale in real-time. Struggling answers trigger supportive concept-checks; exceptional answers unlock deeper architectural challenges.
            </p>
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#818cf8', fontWeight: 600 }}>
              EASY ⇄ MEDIUM ⇄ HARD
            </div>
          </div>

          {/* 2. Multilingual Equality */}
          <div className="glass-panel" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(6, 182, 212, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#38bdf8',
              marginBottom: '16px'
            }}>
              <Languages size={22} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px' }}>
              2. Multilingual Equality
            </h4>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>
              Full first-class support for English and हिंदी. Evaluates core technical substance rather than accent, pronunciation, or native fluency.
            </p>
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#38bdf8', fontWeight: 600 }}>
              English & हिंदी Native Questions
            </div>
          </div>

          {/* 3. Evidence-Backed Scoring */}
          <div className="glass-panel" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(16, 185, 129, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#34d399',
              marginBottom: '16px'
            }}>
              <FileCheck size={22} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px' }}>
              3. Evidence-Backed Scoring
            </h4>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>
              No black-box hallucinated ratings. Every competency score cites verbatim excerpts and proof directly extracted from candidate answers.
            </p>
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#34d399', fontWeight: 600 }}>
              Zero Unsupported Claims
            </div>
          </div>

          {/* 4. Fairness-by-Design */}
          <div className="glass-panel" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(245, 158, 11, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fbbf24',
              marginBottom: '16px'
            }}>
              <ShieldCheck size={22} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px' }}>
              4. Fairness-by-Design
            </h4>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>
              Protected demographic attributes (gender, age, religion, appearance, caste, accent) are completely ignored during technical assessment.
            </p>
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#fbbf24', fontWeight: 600 }}>
              Strict Rubric Grounding
            </div>
          </div>

          {/* 5. Human-in-the-Loop */}
          <div className="glass-panel" style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column' }}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '10px',
              background: 'rgba(168, 85, 247, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#c084fc',
              marginBottom: '16px'
            }}>
              <UserCheck size={22} />
            </div>
            <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '8px' }}>
              5. Human-in-the-Loop
            </h4>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.5, flex: 1 }}>
              The AI never decides who is hired. It generates structured insights and recommendations, empowering human recruiters to make final hiring choices.
            </p>
            <div style={{ marginTop: '14px', fontSize: '0.75rem', color: '#c084fc', fontWeight: 600 }}>
              Recruiter Makes Final Call
            </div>
          </div>
        </div>
      </div>

      {/* Demo Workflow Section */}
      <div className="glass-panel" style={{ padding: '36px 40px', textAlign: 'center' }}>
        <h3 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '16px' }}>
          Interactive End-to-End Interview Journey
        </h3>
        <p style={{ color: 'var(--text-muted)', maxWidth: '680px', margin: '0 auto 30px', fontSize: '0.95rem' }}>
          From candidate consent to dynamic adaptive questions, verbatim evidence harvesting, and recruiter shortlisting.
        </p>

        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          gap: '12px', 
          flexWrap: 'wrap',
          fontSize: '0.88rem',
          fontWeight: 600
        }}>
          <span className="badge badge-secondary" style={{ padding: '8px 14px' }}>1. Setup & Consent</span>
          <span style={{ color: 'var(--text-dim)' }}>→</span>
          <span className="badge badge-cyan" style={{ padding: '8px 14px' }}>2. Text / Voice Input</span>
          <span style={{ color: 'var(--text-dim)' }}>→</span>
          <span className="badge badge-purple" style={{ padding: '8px 14px' }}>3. Adaptive AI Engine</span>
          <span style={{ color: 'var(--text-dim)' }}>→</span>
          <span className="badge badge-easy" style={{ padding: '8px 14px' }}>4. Evidence Extraction</span>
          <span style={{ color: 'var(--text-dim)' }}>→</span>
          <span className="badge badge-medium" style={{ padding: '8px 14px' }}>5. Recruiter Decision</span>
        </div>
      </div>

    </div>
  );
}
