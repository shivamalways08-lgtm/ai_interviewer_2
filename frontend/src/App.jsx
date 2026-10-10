import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import AiSettingsModal from './components/AiSettingsModal';
import LandingPage from './pages/LandingPage';
import CandidateSetupPage from './pages/CandidateSetupPage';
import InterviewPage from './pages/InterviewPage';
import InterviewCompletePage from './pages/InterviewCompletePage';
import CandidateReportPage from './pages/CandidateReportPage';
import RecruiterDashboardPage from './pages/RecruiterDashboardPage';
import FairnessPage from './pages/FairnessPage';
import ResumeUploadPage from './pages/ResumeUploadPage';

import { 
  startInterviewSession, 
  submitInterviewAnswer, 
  completeInterviewSession, 
  seedDemoData,
  fetchAiSettings,
  fetchSessionConsent
} from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('landing');
  const [interviewSession, setInterviewSession] = useState(null);
  const [pendingCandidateConfig, setPendingCandidateConfig] = useState(null);
  const [viewingInterviewId, setViewingInterviewId] = useState(null);
  const [demoNotice, setDemoNotice] = useState(null);
  const [aiSettings, setAiSettings] = useState(null);
  const [isAiModalOpen, setIsAiModalOpen] = useState(false);

  // Initialize and seed demo data, load AI settings & verify active session consent
  useEffect(() => {
    seedDemoData().catch(() => {});
    loadAiSettings();
    restoreSessionIfConsented();
  }, []);

  const restoreSessionIfConsented = async () => {
    try {
      const savedRaw = sessionStorage.getItem('intervueai_session');
      if (!savedRaw) return;
      const saved = JSON.parse(savedRaw);
      if (!saved?.interview_id) return;

      // Verify consent against backend to prevent unconsented resume
      const consentCheck = await fetchSessionConsent(saved.interview_id);
      if (consentCheck?.has_consent) {
        setInterviewSession(saved);
        setActiveTab('interview');
      } else {
        sessionStorage.removeItem('intervueai_session');
        setInterviewSession(null);
      }
    } catch (e) {
      console.warn('Session consent restoration check failed:', e);
      sessionStorage.removeItem('intervueai_session');
      setInterviewSession(null);
    }
  };

  const loadAiSettings = async () => {
    try {
      const data = await fetchAiSettings();
      setAiSettings(data);
    } catch (e) {
      console.warn('Could not load AI settings:', e);
    }
  };

  const handleAiSettingsUpdated = (newSettings) => {
    loadAiSettings();
    if (newSettings?.success) {
      setDemoNotice(`AI Engine Updated: ${newSettings.provider === 'gemini' ? '⚡ Google Gemini AI Active!' : 'Switched to Offline Rubric Mode'}`);
      setTimeout(() => setDemoNotice(null), 5000);
    }
  };

  const handleStartInterviewSession = async (config) => {
    const session = await startInterviewSession(config);
    if (session?.interview_id) {
      sessionStorage.setItem('intervueai_session', JSON.stringify(session));
    }
    setInterviewSession(session);
    setActiveTab('interview');
  };

  const handleSubmitAnswer = async (payload) => {
    const result = await submitInterviewAnswer(payload);
    return result;
  };

  const handleFinishInterview = async () => {
    sessionStorage.removeItem('intervueai_session');
    if (interviewSession?.interview_id) {
      await completeInterviewSession(interviewSession.interview_id).catch(() => {});
      setViewingInterviewId(interviewSession.interview_id);
      setActiveTab('complete');
    }
  };

  const handleQuickDemo = async () => {
    try {
      await seedDemoData();
      // Directly open Aarav Sharma (English) or Pooja Verma (Hindi) in report view
      setViewingInterviewId('intv_demo_001');
      setActiveTab('report');
      setDemoNotice('Demo Candidate Loaded: Aarav Sharma (Software Developer Intern). Inspect competency scores and evidence below!');
      setTimeout(() => setDemoNotice(null), 6000);
    } catch (e) {
      setActiveTab('setup');
    }
  };

  const handleSelectCandidate = (interviewId) => {
    setViewingInterviewId(interviewId);
    setActiveTab('report');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Navigation Header */}
      <Navbar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        onQuickDemo={handleQuickDemo} 
        aiSettings={aiSettings}
        onOpenAiSettings={() => setIsAiModalOpen(true)}
      />

      {/* AI Engine Settings Modal */}
      <AiSettingsModal 
        isOpen={isAiModalOpen}
        onClose={() => setIsAiModalOpen(false)}
        onSettingsUpdated={handleAiSettingsUpdated}
      />

      {/* Demo Notification Banner */}
      {demoNotice && (
        <div style={{
          background: 'linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%)',
          color: '#fff',
          padding: '10px 20px',
          textAlign: 'center',
          fontSize: '0.88rem',
          fontWeight: 600,
          boxShadow: '0 2px 10px rgba(0,0,0,0.3)'
        }}>
          ✨ {demoNotice}
        </div>
      )}

      {/* Main Page Routing */}
      <main style={{ flex: 1 }}>
        {activeTab === 'landing' && (
          <LandingPage 
            onStartInterview={() => setActiveTab('setup')}
            onOpenRecruiter={() => setActiveTab('recruiter')}
            onLaunchDemo={handleQuickDemo}
          />
        )}

        {activeTab === 'setup' && (
          <CandidateSetupPage 
            onProceedToResume={(config) => {
              setPendingCandidateConfig(config);
              setActiveTab('resume-upload');
            }}
            onStartInterviewSession={handleStartInterviewSession}
            onCancel={() => setActiveTab('landing')}
          />
        )}

        {activeTab === 'resume-upload' && pendingCandidateConfig && (
          <ResumeUploadPage 
            candidateConfig={pendingCandidateConfig}
            onContinueWithResume={async (analyzedResume) => {
              await handleStartInterviewSession({
                ...pendingCandidateConfig,
                resume_id: analyzedResume?.resume_id,
                resume_data: analyzedResume
              });
            }}
            onSkipResume={async () => {
              await handleStartInterviewSession({
                ...pendingCandidateConfig,
                resume_id: null,
                resume_data: null
              });
            }}
            onBackToConsent={() => setActiveTab('setup')}
          />
        )}

        {activeTab === 'interview' && interviewSession && (
          <InterviewPage 
            interviewSession={interviewSession}
            onSubmitAnswer={handleSubmitAnswer}
            onFinishInterview={handleFinishInterview}
          />
        )}

        {activeTab === 'complete' && (
          <InterviewCompletePage 
            interviewId={viewingInterviewId}
            onViewReport={() => setActiveTab('report')}
            onGoToDashboard={() => setActiveTab('recruiter')}
          />
        )}

        {activeTab === 'report' && (
          <CandidateReportPage 
            interviewId={viewingInterviewId || 'intv_demo_001'}
            onBackToDashboard={() => setActiveTab('recruiter')}
          />
        )}

        {activeTab === 'recruiter' && (
          <RecruiterDashboardPage 
            onSelectCandidate={handleSelectCandidate}
            onStartNewInterview={() => setActiveTab('setup')}
          />
        )}

        {activeTab === 'fairness' && (
          <FairnessPage 
            onStartInterview={() => setActiveTab('setup')}
          />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--bg-card-border)',
        padding: '24px 0',
        background: 'rgba(10, 14, 23, 0.95)',
        textAlign: 'center',
        fontSize: '0.84rem',
        color: 'var(--text-dim)'
      }}>
        <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <strong>IntervueAI</strong> • Adaptive AI Interviewer Platform (English & हिंदी)
          </div>
          <div style={{ display: 'flex', gap: '16px' }}>
            <span style={{ cursor: 'pointer', color: 'var(--text-muted)' }} onClick={() => setActiveTab('fairness')}>
              Fairness Manifesto
            </span>
            <span style={{ cursor: 'pointer', color: 'var(--text-muted)' }} onClick={() => setActiveTab('recruiter')}>
              Recruiter Dashboard
            </span>
            <span style={{ cursor: 'pointer', color: 'var(--text-muted)' }} onClick={handleQuickDemo}>
              1-Click Demo
            </span>
          </div>
        </div>
      </footer>

    </div>
  );
}
