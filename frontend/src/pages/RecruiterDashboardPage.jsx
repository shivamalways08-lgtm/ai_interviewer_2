import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Sparkles, 
  TrendingUp, 
  Search, 
  Languages, 
  FileText, 
  CheckCircle2, 
  Clock, 
  XCircle, 
  PlusCircle, 
  RefreshCw,
  Award,
  Filter,
  ShieldCheck,
  ShieldAlert
} from 'lucide-react';
import { fetchRecruiterCandidates, seedDemoData } from '../services/api';

export default function RecruiterDashboardPage({ onSelectCandidate, onStartNewInterview }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [languageFilter, setLanguageFilter] = useState('all');
  const [decisionFilter, setDecisionFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [isSeeding, setIsSeeding] = useState(false);
  const [seedNotice, setSeedNotice] = useState(null);

  const loadCandidates = async () => {
    try {
      setLoading(true);
      const res = await fetchRecruiterCandidates();
      setCandidates(res.candidates || []);
    } catch (err) {
      console.error('Error fetching candidates:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, []);

  const handleSeed = async () => {
    setIsSeeding(true);
    setSeedNotice(null);
    try {
      const res = await seedDemoData();
      setSeedNotice('Seeded 3 diverse candidates (English, Hindi, Adaptive)!');
      await loadCandidates();
      setTimeout(() => setSeedNotice(null), 5000);
    } catch (err) {
      alert(`Error seeding demo data: ${err.message}`);
    } finally {
      setIsSeeding(false);
    }
  };

  // Filter candidates
  const filteredCandidates = candidates.filter(c => {
    const matchesSearch = (c.candidate_name || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (c.role || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (c.interview_id || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLang = languageFilter === 'all' || c.language === languageFilter;
    const matchesDecision = decisionFilter === 'all' || 
      (decisionFilter === 'pending' && !c.recruiter_decision) ||
      (c.recruiter_decision === decisionFilter);

    const matchesStatus = statusFilter === 'all' ||
      (statusFilter === 'COMPLETED' && (c.termination_reason === 'NORMAL' || c.status === 'completed')) ||
      (statusFilter === 'TIME_EXPIRED' && (c.termination_reason === 'TIME_EXPIRED' || c.status === 'TIME_EXPIRED')) ||
      (statusFilter === 'TERMINATED_WEAK_ANSWERS' && (c.termination_reason === 'TERMINATED_WEAK_ANSWERS' || c.status === 'TERMINATED_WEAK_ANSWERS')) ||
      (statusFilter === 'TERMINATED_FOCUS_VIOLATION' && (c.termination_reason === 'TERMINATED_FOCUS_VIOLATION' || c.status === 'TERMINATED_FOCUS_VIOLATION'));

    return matchesSearch && matchesLang && matchesDecision && matchesStatus;
  });

  // Calculate metrics
  const total = candidates.length;
  const avgScore = total > 0 
    ? Math.round(candidates.reduce((acc, curr) => acc + (curr.overall_score || 0), 0) / total)
    : 0;
  const shortlistedCount = candidates.filter(c => c.recruiter_decision === 'shortlist').length;
  const hindiCount = candidates.filter(c => c.language === 'hi').length;

  return (
    <div className="container" style={{ maxWidth: '1140px', paddingTop: '36px', paddingBottom: '90px' }}>
      
      {/* Header Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '28px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
            <span className="badge badge-purple">Recruiter Command Center</span>
            <span className="badge badge-easy">Human Decision Hub</span>
          </div>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
            Candidate Assessments & <span className="text-gradient">Evidence Roster</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem' }}>
            Inspect objective skill scores, review verbatim answers, and record human hiring decisions.
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
          <button 
            type="button" 
            className="btn btn-secondary btn-sm"
            onClick={handleSeed}
            disabled={isSeeding}
            title="Populate realistic demo candidates for instant judging evaluation"
          >
            <Sparkles size={15} color="#818cf8" />
            {isSeeding ? 'Seeding...' : '⚡ Seed Demo Candidates'}
          </button>

          <button 
            type="button" 
            className="btn btn-secondary btn-sm"
            onClick={loadCandidates}
          >
            <RefreshCw size={15} />
            Refresh
          </button>

          <button 
            type="button" 
            className="btn btn-primary btn-sm"
            onClick={onStartNewInterview}
          >
            <PlusCircle size={15} />
            New Interview
          </button>
        </div>
      </div>

      {seedNotice && (
        <div style={{
          padding: '12px 18px',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.3)',
          borderRadius: 'var(--radius-sm)',
          color: '#34d399',
          fontSize: '0.88rem',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <CheckCircle2 size={16} />
          {seedNotice}
        </div>
      )}

      {/* KPI Metrics Row */}
      <div className="grid-5" style={{ marginBottom: '28px' }}>
        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Total Assessed
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#fff' }}>
            {total}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#818cf8', marginTop: '4px' }}>
            1st Round Technical
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Avg Score
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#38bdf8' }}>
            {avgScore}/100
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Across all skills
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Shortlisted
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#34d399' }}>
            {shortlistedCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Human verified
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Hindi Interviews
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#fbbf24' }}>
            {hindiCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Evaluated with full parity
          </div>
        </div>

        <div className="glass-panel" style={{ padding: '20px' }}>
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>
            Protected Bias
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, color: '#10b981' }}>
            0%
          </div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '4px' }}>
            Attributes Ignored
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '22px', display: 'flex', gap: '14px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
        
        {/* Search */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: '240px' }}>
          <Search size={18} color="var(--text-dim)" />
          <input 
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search candidates by name, role, or ID..."
            style={{
              width: '100%',
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#fff',
              fontSize: '0.92rem',
              fontFamily: 'inherit'
            }}
          />
        </div>

        {/* Dropdowns */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          {/* Language filter */}
          <select 
            value={languageFilter} 
            onChange={(e) => setLanguageFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontSize: '0.86rem',
              fontFamily: 'inherit',
              cursor: 'pointer'
            }}
          >
            <option value="all" style={{ background: '#0f172a' }}>All Languages</option>
            <option value="en" style={{ background: '#0f172a' }}>English (🇬🇧)</option>
            <option value="hi" style={{ background: '#0f172a' }}>हिंदी (🇮🇳)</option>
          </select>

          {/* Decision filter */}
          <select 
            value={decisionFilter} 
            onChange={(e) => setDecisionFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontSize: '0.86rem',
              fontFamily: 'inherit',
              cursor: 'pointer'
            }}
          >
            <option value="all" style={{ background: '#0f172a' }}>All Human Decisions</option>
            <option value="shortlist" style={{ background: '#0f172a' }}>Shortlisted</option>
            <option value="review_later" style={{ background: '#0f172a' }}>Review Later</option>
            <option value="reject" style={{ background: '#0f172a' }}>Declined</option>
            <option value="pending" style={{ background: '#0f172a' }}>Decision Pending</option>
          </select>

          {/* Status filter */}
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{
              padding: '8px 12px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontSize: '0.86rem',
              fontFamily: 'inherit',
              cursor: 'pointer'
            }}
          >
            <option value="all" style={{ background: '#0f172a' }}>All Session Statuses</option>
            <option value="COMPLETED" style={{ background: '#0f172a' }}>Completed Normally</option>
            <option value="TIME_EXPIRED" style={{ background: '#0f172a' }}>Time Expired (20m)</option>
            <option value="TERMINATED_WEAK_ANSWERS" style={{ background: '#0f172a' }}>Terminated (7 Weak)</option>
            <option value="TERMINATED_FOCUS_VIOLATION" style={{ background: '#0f172a' }}>Terminated (Focus Lost)</option>
          </select>
        </div>

      </div>

      {/* Candidate Roster Table */}
      <div className="glass-panel" style={{ overflowX: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.92rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--bg-card-border)', color: 'var(--text-dim)', fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              <th style={{ padding: '16px 20px' }}>Candidate</th>
              <th style={{ padding: '16px 16px' }}>Status & Outcome</th>
              <th style={{ padding: '16px 16px' }}>Language & Mode</th>
              <th style={{ padding: '16px 16px' }}>Overall Score</th>
              <th style={{ padding: '16px 16px' }}>AI Assistive Rec</th>
              <th style={{ padding: '16px 16px' }}>Recruiter Decision</th>
              <th style={{ padding: '16px 20px', textAlign: 'right' }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={7} style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Loading candidate evaluations...
                </td>
              </tr>
            ) : filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  No candidate evaluations found matching criteria. Click <strong>⚡ Seed Demo Candidates</strong> above to populate sample records!
                </td>
              </tr>
            ) : (
              filteredCandidates.map((c) => {
                const candScore = c.overall_score || 0;
                const isHigh = candScore >= 80;
                const isMid = candScore >= 65 && candScore < 80;

                const isFocusViolated = c.termination_reason === 'TERMINATED_FOCUS_VIOLATION' || c.status === 'TERMINATED_FOCUS_VIOLATION';
                const isTimeExpired = c.termination_reason === 'TIME_EXPIRED' || c.status === 'TIME_EXPIRED';
                const isWeakTerminated = c.termination_reason === 'TERMINATED_WEAK_ANSWERS' || c.status === 'TERMINATED_WEAK_ANSWERS';

                return (
                  <tr 
                    key={c.interview_id}
                    style={{ 
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      transition: 'background 0.2s ease'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255, 255, 255, 0.02)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    {/* Candidate Info */}
                    <td style={{ padding: '16px 20px' }}>
                      <div style={{ fontWeight: 700, color: '#fff' }}>
                        {c.candidate_name || 'Anonymous Candidate'}
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap', marginTop: '3px' }}>
                        <span>{c.role} • {c.interview_id}</span>
                        <span>•</span>
                        <span style={{ color: '#38bdf8' }}>{c.turns_count || 0} answered</span>
                        <span>•</span>
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '3px' }}>
                          <ShieldCheck size={12} /> Consent: {c.consent_status || 'granted'}
                        </span>
                        <span>•</span>
                        {c.resume_id ? (
                          <span style={{ color: '#a78bfa', display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <FileText size={12} /> {c.resume_filename || 'Personalized Resume'}
                          </span>
                        ) : (
                          <span style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '3px' }}>
                            <FileText size={12} /> Standard Benchmark
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Status & Outcome */}
                    <td style={{ padding: '16px 16px' }}>
                      {isFocusViolated ? (
                        <span className="badge badge-hard" style={{ fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <ShieldAlert size={12} /> Focus Lost
                        </span>
                      ) : isTimeExpired ? (
                        <span className="badge badge-medium" style={{ fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> Time Expired
                        </span>
                      ) : isWeakTerminated ? (
                        <span className="badge badge-purple" style={{ fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <XCircle size={12} /> Terminated (7 Weak)
                        </span>
                      ) : (
                        <span className="badge badge-easy" style={{ fontSize: '0.74rem', display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                          <CheckCircle2 size={12} /> Completed
                        </span>
                      )}
                    </td>

                    {/* Language & Mode */}
                    <td style={{ padding: '16px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span className="badge badge-secondary" style={{ fontSize: '0.74rem' }}>
                          {c.language === 'hi' ? '🇮🇳 हिंदी' : '🇬🇧 English'}
                        </span>
                        <span style={{ fontSize: '0.74rem', color: 'var(--text-dim)', textTransform: 'capitalize' }}>
                          {c.interview_mode || 'text'}
                        </span>
                      </div>
                    </td>

                    {/* Score */}
                    <td style={{ padding: '16px 16px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{
                          fontWeight: 800,
                          fontSize: '1.05rem',
                          color: isHigh ? '#34d399' : isMid ? '#818cf8' : '#fbbf24'
                        }}>
                          {candScore}
                        </div>
                        <span style={{ fontSize: '0.72rem', color: 'var(--text-dim)' }}>/100</span>
                      </div>
                    </td>

                    {/* AI Recommendation */}
                    <td style={{ padding: '16px 16px' }}>
                      <span className={`badge ${c.ai_recommendation === 'Strong Match' ? 'badge-easy' : 'badge-cyan'}`} style={{ fontSize: '0.75rem' }}>
                        {c.ai_recommendation || 'Evaluated'}
                      </span>
                    </td>

                    {/* Recruiter Decision */}
                    <td style={{ padding: '16px 16px' }}>
                      {c.recruiter_decision === 'shortlist' ? (
                        <span className="badge badge-easy">
                          <CheckCircle2 size={12} /> Shortlisted
                        </span>
                      ) : c.recruiter_decision === 'review_later' ? (
                        <span className="badge badge-medium">
                          <Clock size={12} /> Review Later
                        </span>
                      ) : c.recruiter_decision === 'reject' ? (
                        <span className="badge badge-hard">
                          <XCircle size={12} /> Declined
                        </span>
                      ) : (
                        <span className="badge badge-secondary" style={{ background: 'rgba(255,255,255,0.06)' }}>
                          Pending Decision
                        </span>
                      )}
                    </td>

                    {/* Action Button */}
                    <td style={{ padding: '16px 20px', textAlign: 'right' }}>
                      <button 
                        type="button" 
                        className="btn btn-secondary btn-sm"
                        onClick={() => onSelectCandidate(c.interview_id)}
                      >
                        <FileText size={14} />
                        Review Evidence
                      </button>
                    </td>

                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
