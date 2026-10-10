import React, { useState, useEffect } from 'react';
import {
  FileText,
  CheckCircle2,
  AlertTriangle,
  UserCheck,
  Sparkles,
  ChevronDown,
  ChevronUp,
  ShieldCheck,
  ArrowLeft,
  Printer,
  Save,
  Clock,
  Code2,
  Briefcase,
  Check,
  X,
  HelpCircle,
  Award
} from 'lucide-react';
import { fetchCandidateReport, recordRecruiterDecision } from '../services/api';

export default function CandidateReportPage({ interviewId, onBackToDashboard }) {
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [expandedSkill, setExpandedSkill] = useState(null);
  const [selectedDecision, setSelectedDecision] = useState(null);
  const [recruiterNotes, setRecruiterNotes] = useState('');
  const [isSavingDecision, setIsSavingDecision] = useState(false);
  const [decisionSavedMessage, setDecisionSavedMessage] = useState(null);

  useEffect(() => {
    async function loadReport() {
      try {
        setLoading(true);
        const data = await fetchCandidateReport(interviewId);
        setReport(data);
        if (data.recruiter_decision) {
          setSelectedDecision(data.recruiter_decision);
        }
        if (data.recruiter_notes) {
          setRecruiterNotes(data.recruiter_notes);
        }
        // Auto-expand first skill
        if (data.skills_breakdown && data.skills_breakdown.length > 0) {
          setExpandedSkill(data.skills_breakdown[0].skill);
        }
      } catch (err) {
        setError(err.message || 'Failed to load report');
      } finally {
        setLoading(false);
      }
    }
    if (interviewId) {
      loadReport();
    }
  }, [interviewId]);

  const handleDecisionSave = async (decision) => {
    setSelectedDecision(decision);
    setIsSavingDecision(true);
    setDecisionSavedMessage(null);
    try {
      await recordRecruiterDecision({
        interview_id: interviewId,
        decision: decision,
        notes: recruiterNotes
      });
      setDecisionSavedMessage(`Decision recorded: ${decision.toUpperCase()}`);
      setTimeout(() => setDecisionSavedMessage(null), 4000);
    } catch (err) {
      alert(`Error saving decision: ${err.message}`);
    } finally {
      setIsSavingDecision(false);
    }
  };

  if (loading) {
    return (
      <div className="container" style={{ textAlign: 'center', paddingTop: '100px' }}>
        <div style={{ fontSize: '1.2rem', color: 'var(--text-muted)' }}>
          Generating Executive Recruiter Report with Evidence Harvest...
        </div>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="container" style={{ textAlign: 'center', paddingTop: '100px' }}>
        <div style={{ color: '#f43f5e', fontSize: '1.2rem', marginBottom: '16px' }}>
          {error || 'Report not found.'}
        </div>
        <button className="btn btn-secondary" onClick={onBackToDashboard}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  const score = report.overall_score || 0;
  const isHigh = score >= 80;
  const isMid = score >= 65 && score < 80;

  return (
    <div className="container" style={{ maxWidth: '1080px', paddingTop: '32px', paddingBottom: '90px' }}>

      {/* Top Navigation */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <button className="btn btn-secondary btn-sm" onClick={onBackToDashboard}>
          <ArrowLeft size={16} />
          Back to Recruiter Dashboard
        </button>

        <button className="btn btn-secondary btn-sm" onClick={() => window.print()}>
          <Printer size={16} />
          Export / Print Report
        </button>
      </div>

      {/* Main Report Header Card */}
      <div className="glass-panel" style={{ padding: '36px', marginBottom: '28px', borderTop: '4px solid #6366f1' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '20px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px', flexWrap: 'wrap' }}>
              <span className="badge badge-purple">Recruiter Technical Dossier</span>
              <span className="badge badge-cyan">
                {report.language === 'hi' ? '🇮🇳 Interviewed in हिंदी' : '🇬🇧 Interviewed in English'}
              </span>
              {report.turns?.some(t => t.evaluator?.includes('gemini')) && (
                <span className="badge badge-purple" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <Sparkles size={12} /> Powered by Gemini AI
                </span>
              )}
            </div>

            <h1 style={{ fontSize: '2.4rem', fontWeight: 800, marginBottom: '6px' }}>
              {report.candidate_name || 'Anonymous Candidate'}
            </h1>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', color: 'var(--text-muted)', fontSize: '0.92rem', flexWrap: 'wrap' }}>
              <span><strong>Role:</strong> {report.role}</span>
              <span>•</span>
              <span><strong>Assessment ID:</strong> {report.interview_id}</span>
              <span>•</span>
              <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <ShieldCheck size={14} /> <strong>Consent:</strong> Verified ({report.consent_record?.policy_version || 'v1.2'})
              </span>
            </div>
          </div>

          {/* Overall Score Dial */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '2px solid',
            borderColor: isHigh ? '#10b981' : isMid ? '#6366f1' : '#f59e0b',
            borderRadius: '16px',
            padding: '16px 28px',
            textAlign: 'center',
            minWidth: '150px'
          }}>
            <div style={{
              fontSize: '2.6rem',
              fontWeight: 800,
              lineHeight: 1,
              color: isHigh ? '#34d399' : isMid ? '#a5b4fc' : '#fbbf24'
            }}>
              {report.overall_score}
            </div>
            <div style={{ fontSize: '0.74rem', color: 'var(--text-dim)', marginTop: '4px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Overall Score / 100
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* INTERVIEW EXECUTION & TERMINATION AUDIT DOSSIER          */}
        {/* ======================================================== */}
        <div style={{
          marginTop: '24px',
          padding: '20px 24px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--bg-card-border)',
          borderRadius: 'var(--radius-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)' }}>
                Interview Status:
              </span>
              <span className={`badge ${report.termination_reason === 'TERMINATED_FOCUS_VIOLATION'
                  ? 'badge-hard'
                  : report.termination_reason === 'TIME_EXPIRED'
                    ? 'badge-medium'
                    : report.termination_reason === 'TERMINATED_WEAK_ANSWERS'
                      ? 'badge-purple'
                      : 'badge-easy'
                }`} style={{ fontSize: '0.86rem', padding: '6px 14px' }}>
                {report.termination_reason === 'TERMINATED_FOCUS_VIOLATION' ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <ShieldAlert size={13} /> TERMINATED_FOCUS_VIOLATION (Tab Switch / Page Focus Lost)
                  </span>
                ) : report.termination_reason === 'TIME_EXPIRED' ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <Clock size={13} /> TIME_EXPIRED (20-Minute Limit Reached)
                  </span>
                ) : report.termination_reason === 'TERMINATED_WEAK_ANSWERS' ? (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <AlertTriangle size={13} /> TERMINATED_WEAK_ANSWERS (7 Consecutive Weak Answers &lt;40/100)
                  </span>
                ) : (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <CheckCircle2 size={13} /> COMPLETED (Completed Normally)
                  </span>
                )}
              </span>
            </div>

            <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
              Backend Authoritative Record
            </div>
          </div>

          {/* Key Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: '14px',
            marginBottom: '14px'
          }}>
            <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Start Time</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', marginTop: '3px' }}>
                {report.started_at ? new Date(report.started_at).toLocaleTimeString() : 'N/A'}
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>End Time</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', marginTop: '3px' }}>
                {report.completed_at ? new Date(report.completed_at).toLocaleTimeString() : 'N/A'}
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Total Duration</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#38bdf8', marginTop: '3px' }}>
                {report.duration_formatted || 'N/A'}
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Questions Answered</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: '#fff', marginTop: '3px' }}>
                {report.questions_answered} Completed
              </div>
            </div>

            <div style={{ padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-dim)', textTransform: 'uppercase' }}>Consecutive Weak Count</div>
              <div style={{ fontSize: '0.88rem', fontWeight: 700, color: report.consecutive_weak_answers >= 7 ? '#f87171' : '#a5b4fc', marginTop: '3px' }}>
                {report.consecutive_weak_answers != null ? report.consecutive_weak_answers : 0}
              </div>
            </div>
          </div>

          {/* Termination Explanation Notice */}
          <div style={{
            fontSize: '0.88rem',
            color: '#cbd5e1',
            lineHeight: 1.5,
            borderTop: '1px solid rgba(255, 255, 255, 0.06)',
            paddingTop: '10px'
          }}>
            <strong>Termination Summary:</strong> {report.termination_summary || 'The interview concluded normally.'}
            <div style={{ fontSize: '0.78rem', color: '#94a3b8', marginTop: '6px', fontStyle: 'italic' }}>
              Note: The interview termination condition reflects session administration rules and does not automatically determine candidate suitability. A human recruiter must review the evidence below.
            </div>
          </div>
        </div>

        {/* ======================================================== */}
        {/* SECTION 15: CRUCIAL AI RECOMMENDATION + HUMAN DECISION SEPARATION */}
        {/* ======================================================== */}
        <div style={{
          marginTop: '20px',
          padding: '20px 24px',
          background: 'rgba(99, 102, 241, 0.07)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: 'var(--radius-sm)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px', marginBottom: '8px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={18} color="#818cf8" />
              <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                AI Assistive Recommendation:
              </span>
              <span className={`badge ${isHigh ? 'badge-easy' : isMid ? 'badge-cyan' : 'badge-medium'}`} style={{ fontSize: '0.88rem' }}>
                {report.ai_recommendation}
              </span>
            </div>

            <div style={{ fontSize: '0.78rem', color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '5px' }}>
              <ShieldCheck size={14} /> Human Recruiter Authority Enforced
            </div>
          </div>

          <p style={{ fontSize: '0.94rem', color: '#cbd5e1', lineHeight: 1.55 }}>
            {report.ai_recommendation_summary}
          </p>

          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '10px', fontStyle: 'italic', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '8px' }}>
            {report.human_decision_notice}
          </div>
        </div>

      </div>

      {/* ======================================================== */}
      {/* SECTION: CANDIDATE RESUME & TECHNICAL DOSSIER */}
      {/* ======================================================== */}
      <div style={{ marginBottom: '32px' }}>
        {report.resume_info ? (
          <div className="glass-panel" style={{ padding: '28px', borderLeft: '4px solid #8b5cf6' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '14px', marginBottom: '18px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                  <FileText size={20} color="#8b5cf6" />
                  <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>
                    Candidate Resume & Technical Dossier
                  </h3>
                  <span className="badge badge-purple" style={{ fontSize: '0.78rem' }}>
                    {report.resume_info.parser === 'gemini_multimodal' || report.resume_info.parser === 'gemini_structured'
                      ? '⚡ AI Analyzed (Gemini)'
                      : 'Keyword Fallback Analyzed'}
                  </span>
                </div>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                  Extracted from <strong style={{ color: '#fff' }}>{report.resume_info.filename || 'uploaded_resume'}</strong> to personalize technical deep-dive questions.
                </p>
              </div>

              <span className="badge badge-easy" style={{ fontSize: '0.82rem' }}>
                <CheckCircle2 size={13} style={{ marginRight: '4px' }} /> Resume Linked to Session
              </span>
            </div>

            {/* Skills Badges */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px', marginBottom: '20px' }}>
              {report.resume_info.languages_frameworks?.length > 0 && (
                <div style={{ padding: '14px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 700 }}>
                    Languages & Frameworks
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {report.resume_info.languages_frameworks.map((lf, i) => (
                      <span key={i} className="badge badge-purple" style={{ fontSize: '0.78rem' }}>
                        {lf}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {report.resume_info.tools_technologies?.length > 0 && (
                <div style={{ padding: '14px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '8px', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 700 }}>
                    Tools & Technologies
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {report.resume_info.tools_technologies.map((tt, i) => (
                      <span key={i} className="badge badge-cyan" style={{ fontSize: '0.78rem' }}>
                        {tt}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Extracted Projects */}
            {report.resume_info.detected_projects?.length > 0 && (
              <div>
                <div style={{ fontSize: '0.86rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Code2 size={16} color="#38bdf8" />
                  Verified Projects & Candidate Responsibilities
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '12px' }}>
                  {report.resume_info.detected_projects.map((proj, idx) => (
                    <div key={idx} style={{
                      padding: '14px 16px',
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.06)'
                    }}>
                      <div style={{ fontWeight: 700, fontSize: '0.94rem', color: '#fff', marginBottom: '4px' }}>
                        {proj.name || `Project ${idx + 1}`}
                      </div>
                      {proj.description && (
                        <p style={{ fontSize: '0.84rem', color: '#cbd5e1', marginBottom: '8px', lineHeight: 1.45 }}>
                          {proj.description}
                        </p>
                      )}
                      {proj.technologies?.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginBottom: '6px' }}>
                          {proj.technologies.map((t, ti) => (
                            <span key={ti} style={{
                              fontSize: '0.72rem',
                              padding: '2px 8px',
                              borderRadius: '4px',
                              background: 'rgba(6, 182, 212, 0.15)',
                              color: '#38bdf8',
                              border: '1px solid rgba(6, 182, 212, 0.25)'
                            }}>
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                      {proj.responsibilities?.length > 0 && (
                        <div style={{ fontSize: '0.76rem', color: '#94a3b8', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '6px', marginTop: '6px' }}>
                          <strong style={{ color: '#cbd5e1' }}>Responsibilities:</strong> {proj.responsibilities.join(' • ')}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="glass-panel" style={{
            padding: '20px 24px',
            borderLeft: '4px solid #64748b',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <FileText size={20} color="#94a3b8" />
              <div>
                <div style={{ fontWeight: 700, fontSize: '0.94rem', color: '#e2e8f0' }}>
                  Standard Job Benchmark Session (Resume Personalization Skipped)
                </div>
                <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                  The candidate chose not to upload a resume. All questions and evaluations followed the standardized core competency rubric for {report.role}.
                </div>
              </div>
            </div>
            <span className="badge" style={{
              background: 'rgba(148, 163, 184, 0.1)',
              border: '1px solid rgba(148, 163, 184, 0.25)',
              color: '#94a3b8',
              fontSize: '0.78rem'
            }}>
              Standardized Rubric
            </span>
          </div>
        )}
      </div>

      {/* ======================================================== */}
      {/* SECTION 14: INTERACTIVE EVIDENCE VIEW */}
      {/* ======================================================== */}
      <div style={{ marginBottom: '36px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.45rem', fontWeight: 800 }}>
              Competency Breakdown & Verbatim Evidence
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>
              Click any competency to inspect direct textual proof harvested from candidate answers.
            </p>
          </div>
          <span className="badge badge-purple">Evidence-Backed</span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {report.skills_breakdown.map((item) => {
            const isExpanded = expandedSkill === item.skill;
            const skillScore = item.score;
            return (
              <div
                key={item.skill}
                className="glass-panel"
                style={{
                  overflow: 'hidden',
                  borderColor: isExpanded ? 'rgba(99, 102, 241, 0.4)' : 'var(--bg-card-border)'
                }}
              >
                {/* Accordion Row Header */}
                <div
                  onClick={() => setExpandedSkill(isExpanded ? null : item.skill)}
                  style={{
                    padding: '20px 24px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer',
                    background: isExpanded ? 'rgba(255, 255, 255, 0.02)' : 'transparent'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                      width: '40px',
                      height: '40px',
                      borderRadius: '10px',
                      background: 'rgba(99, 102, 241, 0.12)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      color: '#818cf8',
                      fontWeight: 700
                    }}>
                      <Code2 size={20} />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#fff' }}>
                        {item.skill}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                        Difficulty reached: {item.difficulty_reached || 'MEDIUM'}
                      </div>
                    </div>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                    {/* Score Bar */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{
                        width: '120px',
                        height: '8px',
                        background: 'rgba(255, 255, 255, 0.08)',
                        borderRadius: '4px',
                        overflow: 'hidden'
                      }}>
                        <div style={{
                          width: `${skillScore}%`,
                          height: '100%',
                          background: skillScore >= 80 ? '#10b981' : skillScore >= 60 ? '#6366f1' : '#f59e0b',
                          borderRadius: '4px'
                        }} />
                      </div>
                      <span style={{ fontWeight: 800, fontSize: '1.1rem', minWidth: '40px' }}>
                        {skillScore}
                      </span>
                    </div>

                    {isExpanded ? <ChevronUp size={20} color="#94a3b8" /> : <ChevronDown size={20} color="#94a3b8" />}
                  </div>
                </div>

                {/* Expanded Evidence & Reason Details */}
                {isExpanded && (
                  <div style={{ padding: '0 24px 24px', borderTop: '1px solid var(--bg-card-border)' }}>

                    {/* Verbatim Evidence Box (Hackathon Star Feature) */}
                    <div style={{
                      marginTop: '20px',
                      padding: '16px 20px',
                      background: 'rgba(16, 185, 129, 0.08)',
                      borderLeft: '4px solid #10b981',
                      borderRadius: '8px'
                    }}>
                      <div style={{
                        fontSize: '0.8rem',
                        fontWeight: 700,
                        color: '#34d399',
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        marginBottom: '6px'
                      }}>
                        Verbatim Candidate Evidence (Direct Transcript Proof):
                      </div>
                      <div style={{ fontSize: '0.96rem', color: '#f1f5f9', fontStyle: 'italic', lineHeight: 1.6 }}>
                        {item.evidence || "Insufficient evidence provided in answer."}
                      </div>
                    </div>

                    {/* Evaluator Rationale */}
                    <div style={{ marginTop: '16px' }}>
                      <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>
                        Rubric Grounded Rationale:
                      </div>
                      <div style={{ fontSize: '0.92rem', color: '#cbd5e1', lineHeight: 1.55 }}>
                        {item.reason}
                      </div>
                    </div>

                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Planned Competencies Not Reached (when interview ends early - strictly no fabricated scores) */}
        {report.pending_skills && report.pending_skills.length > 0 && (
          <div style={{ marginTop: '22px' }}>
            <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '12px' }}>
              Planned Competencies Closed Due to Early Termination (No Scores Fabricated):
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {report.pending_skills.map((ps) => (
                <div
                  key={ps.skill}
                  className="glass-panel"
                  style={{
                    padding: '14px 20px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: 'rgba(255, 255, 255, 0.01)',
                    border: '1px dashed rgba(255, 255, 255, 0.12)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#94a3b8' }} />
                    <div>
                      <div style={{ fontWeight: 600, fontSize: '0.94rem', color: '#94a3b8' }}>{ps.skill}</div>
                      <div style={{ fontSize: '0.76rem', color: 'var(--text-dim)' }}>{ps.reason}</div>
                    </div>
                  </div>
                  <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-dim)', fontSize: '0.75rem' }}>
                    Score Unavailable
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Strengths and Growth Areas Grid */}
      <div className="grid-2" style={{ marginBottom: '36px' }}>

        {/* Strengths */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <CheckCircle2 size={20} color="#10b981" />
            <h4 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Demonstrated Strengths</h4>
          </div>
          <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {report.strengths.map((str, i) => (
              <li key={i} style={{ fontSize: '0.92rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                {str}
              </li>
            ))}
          </ul>
        </div>

        {/* Growth Areas */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <AlertTriangle size={20} color="#f59e0b" />
            <h4 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Areas for Growth</h4>
          </div>
          <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {report.areas_to_improve.map((imp, i) => (
              <li key={i} style={{ fontSize: '0.92rem', color: '#e2e8f0', lineHeight: 1.5 }}>
                {imp}
              </li>
            ))}
          </ul>
        </div>

      </div>

      {/* ======================================================== */}
      {/* SECTION 15: HUMAN RECRUITER ACTION PANEL */}
      {/* ======================================================== */}
      <div className="glass-panel" style={{
        padding: '32px',
        border: '1px solid rgba(16, 185, 129, 0.3)',
        background: 'rgba(16, 185, 129, 0.03)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
          <UserCheck size={24} color="#10b981" />
          <h3 style={{ fontSize: '1.35rem', fontWeight: 800 }}>
            Human Recruiter Hiring Decision
          </h3>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '22px' }}>
          The AI system does NOT make final employment decisions. A human recruiter must review the evidence above and select an official outcome.
        </p>

        {/* Decision Button Group */}
        <div style={{ display: 'flex', gap: '14px', flexWrap: 'wrap', marginBottom: '20px' }}>
          <button
            type="button"
            className={`btn ${selectedDecision === 'shortlist' ? 'btn-success' : 'btn-secondary'}`}
            onClick={() => handleDecisionSave('shortlist')}
            disabled={isSavingDecision}
            style={{ padding: '12px 24px', fontSize: '1rem' }}
          >
            <Check size={18} />
            Shortlist for Team Round
          </button>

          <button
            type="button"
            className={`btn ${selectedDecision === 'review_later' ? 'btn-warning' : 'btn-secondary'}`}
            onClick={() => handleDecisionSave('review_later')}
            disabled={isSavingDecision}
            style={{ padding: '12px 24px', fontSize: '1rem' }}
          >
            <Clock size={18} />
            Review Later / Request Info
          </button>

          <button
            type="button"
            className={`btn ${selectedDecision === 'reject' ? 'btn-danger' : 'btn-secondary'}`}
            onClick={() => handleDecisionSave('reject')}
            disabled={isSavingDecision}
            style={{ padding: '12px 24px', fontSize: '1rem' }}
          >
            <X size={18} />
            Decline Application
          </button>
        </div>

        {/* Recruiter Notes Area */}
        <div>
          <label style={{ display: 'block', fontSize: '0.86rem', fontWeight: 700, marginBottom: '8px', color: '#cbd5e1' }}>
            Recruiter Qualitative Notes:
          </label>
          <textarea
            rows={3}
            value={recruiterNotes}
            onChange={(e) => setRecruiterNotes(e.target.value)}
            placeholder="Add context on candidate's communication style, problem-solving reasoning, or specific questions for the next round..."
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontFamily: 'inherit',
              fontSize: '0.92rem',
              resize: 'vertical',
              marginBottom: '12px'
            }}
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.82rem', color: '#34d399' }}>
              {decisionSavedMessage || (selectedDecision ? `Current Status: ${selectedDecision.toUpperCase()}` : 'No decision recorded yet.')}
            </span>

            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={() => handleDecisionSave(selectedDecision || 'review_later')}
              disabled={isSavingDecision}
            >
              <Save size={14} />
              Save Recruiter Notes
            </button>
          </div>
        </div>

      </div>

    </div>
  );
}
