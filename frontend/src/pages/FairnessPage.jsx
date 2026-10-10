import React from 'react';
import { 
  ShieldCheck, 
  CheckCircle2, 
  XCircle, 
  Languages, 
  FileCheck, 
  UserCheck, 
  Scale, 
  EyeOff, 
  Lock,
  Cpu
} from 'lucide-react';

export default function FairnessPage({ onStartInterview }) {
  return (
    <div className="container" style={{ maxWidth: '920px', paddingTop: '40px', paddingBottom: '90px' }}>
      
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: '45px' }}>
        <span className="badge badge-purple" style={{ marginBottom: '10px' }}>
          Algorithmic Ethics & Privacy Framework
        </span>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
          How IntervueAI Keeps <span className="text-gradient">Interviews Fair</span>
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', maxWidth: '640px', margin: '10px auto 0' }}>
          IntervueAI is engineered with ethical guardrails to guarantee merit-based evaluations,
          linguistic equity across English and Hindi, and strict human accountability.
        </p>
      </div>

      {/* Fairness Principles Grid */}
      <div className="grid-2" style={{ marginBottom: '40px' }}>
        
        {/* What We Strictly Ignore */}
        <div className="glass-panel" style={{ padding: '30px', borderLeft: '4px solid #f43f5e' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <EyeOff size={22} color="#f43f5e" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fca5a5' }}>
              Attributes Strictly Disregarded
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
            Our evaluation pipeline actively sanitizes inputs and prohibits any scoring variance based on:
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.86rem', color: '#cbd5e1' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Gender & pronouns
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Religion & caste
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Age & appearance
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Regional accents
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Socioeconomic status
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <XCircle size={15} color="#f43f5e" /> Grammar perfection
            </div>
          </div>
        </div>

        {/* What We Explicitly Evaluate */}
        <div className="glass-panel" style={{ padding: '30px', borderLeft: '4px solid #10b981' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <Scale size={22} color="#10b981" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#6ee7b7' }}>
              Job Competencies Evaluated
            </h3>
          </div>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '18px' }}>
            Scoring is 100% grounded in verifiable technical competencies defined by the role rubric:
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '0.86rem', color: '#cbd5e1' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Programming Fundamentals
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Problem Solving Logic
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Data Structures & Algorithms
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Technical System Design
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Collaboration & Trade-offs
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <CheckCircle2 size={15} color="#10b981" /> Verbatim Proof Citations
            </div>
          </div>
        </div>

      </div>

      {/* Multilingual Parity Section */}
      <div className="glass-panel" style={{ padding: '32px', marginBottom: '36px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'rgba(6, 182, 212, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#38bdf8'
          }}>
            <Languages size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              Multilingual Equity: English & हिंदी
            </h3>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              Breaking the language barrier in technical recruitment
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.94rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '16px' }}>
          Traditional first-round technical interviews frequently penalize candidates whose first language is not English,
          even when their algorithmic reasoning and core software engineering fundamentals are outstanding.
        </p>

        <div style={{ 
          padding: '16px 20px', 
          background: 'rgba(6, 182, 212, 0.08)', 
          borderRadius: '8px',
          borderLeft: '4px solid #06b6d4',
          fontSize: '0.9rem',
          color: '#e2e8f0',
          lineHeight: 1.55
        }}>
          <strong>The IntervueAI Standard:</strong> A candidate explaining memory allocation, time complexity, or race conditions in
          Hindi is scored on the identical competency rubric as an English speaker. Technical concept recognition operates seamlessly across
          Devanagari, English, and transliterated terminology.
        </div>
      </div>

      {/* Human-in-the-Loop & Privacy Callout */}
      <div className="glass-panel" style={{ padding: '32px', marginBottom: '40px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '14px' }}>
          <div style={{
            width: '42px',
            height: '42px',
            borderRadius: '10px',
            background: 'rgba(168, 85, 247, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#c084fc'
          }}>
            <UserCheck size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 800 }}>
              Human-in-the-Loop Decision Governance
            </h3>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
              AI as an Assistant, Not an Autonomous Gatekeeper
            </div>
          </div>
        </div>

        <p style={{ fontSize: '0.94rem', color: '#cbd5e1', lineHeight: 1.6, marginBottom: '16px' }}>
          IntervueAI will <strong>never</strong> render autonomous hiring decisions. The system synthesizes objective evidence,
          computes rubrics, and offers an AI recommendation (e.g. "Strong Match", "Potential Match"), but <strong>all shortlist and
          rejection actions require a human recruiter</strong>.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#a5b4fc', fontSize: '0.85rem' }}>
          <Lock size={16} /> Privacy First: No candidate personal identifying information is stored or profiled.
        </div>
      </div>

      {/* Start Interview CTA */}
      <div style={{ textAlign: 'center' }}>
        <button className="btn btn-primary btn-lg" onClick={onStartInterview}>
          Experience a Fair Interview Session
        </button>
      </div>

    </div>
  );
}
