import React, { useEffect } from 'react';
import { CheckCircle2, ArrowRight, Award, Users, FileText, Sparkles } from 'lucide-react';
import confetti from 'canvas-confetti';

export default function InterviewCompletePage({ interviewId, onViewReport, onGoToDashboard }) {
  useEffect(() => {
    try {
      confetti({
        particleCount: 80,
        spread: 70,
        origin: { y: 0.6 }
      });
    } catch (e) {
      // ignore
    }
  }, []);

  return (
    <div className="container" style={{ maxWidth: '680px', paddingTop: '60px', paddingBottom: '80px', textAlign: 'center' }}>
      <div className="glass-panel" style={{ padding: '50px 36px' }}>
        
        {/* Success Icon */}
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'rgba(16, 185, 129, 0.15)',
          border: '2px solid #10b981',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#34d399',
          margin: '0 auto 24px',
          boxShadow: '0 0 30px rgba(16, 185, 129, 0.3)'
        }}>
          <CheckCircle2 size={38} />
        </div>

        <span className="badge badge-easy" style={{ marginBottom: '12px', padding: '6px 14px' }}>
          Interview Successfully Concluded
        </span>

        <h2 style={{ fontSize: '2.4rem', fontWeight: 800, marginBottom: '14px' }}>
          Assessment <span className="text-gradient">Complete!</span>
        </h2>

        <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', lineHeight: 1.6, maxWidth: '520px', margin: '0 auto 32px' }}>
          All completed interview questions have been evaluated against standard rubrics with direct textual evidence harvested from your answers.
        </p>

        {/* Feature Pill Callouts */}
        <div style={{
          padding: '18px 24px',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid var(--bg-card-border)',
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          justifyContent: 'space-around',
          marginBottom: '36px',
          textAlign: 'left'
        }}>
          <div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Session Scope</div>
            <div style={{ fontWeight: 700, fontSize: '0.98rem' }}>20-Min Adaptive</div>
          </div>
          <div style={{ borderLeft: '1px solid var(--bg-card-border)', paddingLeft: '20px' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Evidence Quotes</div>
            <div style={{ fontWeight: 700, fontSize: '0.98rem', color: '#34d399' }}>Verified</div>
          </div>
          <div style={{ borderLeft: '1px solid var(--bg-card-border)', paddingLeft: '20px' }}>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Fairness Filter</div>
            <div style={{ fontWeight: 700, fontSize: '0.98rem', color: '#818cf8' }}>Applied</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', flexWrap: 'wrap' }}>
          <button 
            type="button" 
            className="btn btn-primary btn-lg"
            onClick={onViewReport}
          >
            <FileText size={18} />
            View Candidate Report
            <ArrowRight size={18} />
          </button>

          <button 
            type="button" 
            className="btn btn-secondary btn-lg"
            onClick={onGoToDashboard}
          >
            <Users size={18} />
            Go to Recruiter Dashboard
          </button>
        </div>

      </div>
    </div>
  );
}
