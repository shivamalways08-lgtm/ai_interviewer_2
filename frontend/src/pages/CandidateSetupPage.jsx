import React, { useState } from 'react';
import { 
  Languages, 
  Mic, 
  FileText, 
  ShieldCheck, 
  ArrowRight, 
  User, 
  Briefcase 
} from 'lucide-react';
import CandidateConsentScreen from '../components/CandidateConsentScreen';
import { recordConsentDecline } from '../services/api';

export default function CandidateSetupPage({ onStartInterviewSession, onProceedToResume, onCancel }) {
  const [step, setStep] = useState('config'); // 'config' | 'consent'
  const [role] = useState('Software Developer Intern');
  const [language, setLanguage] = useState('en'); // 'en' or 'hi'
  const [interviewMode, setInterviewMode] = useState('text'); // 'text' or 'voice'
  const [candidateName, setCandidateName] = useState('Anonymous Candidate #042');
  const [isLoading, setIsLoading] = useState(false);
  const [_error, setError] = useState(null);

  const handleConsentGranted = async (consentData) => {
    setIsLoading(true);
    setError(null);
    const candidateData = {
      name: candidateName,
      role: role,
      language: language,
      interview_mode: interviewMode,
      consent: consentData,
      consent_agreed: true
    };

    if (onProceedToResume) {
      setIsLoading(false);
      onProceedToResume(candidateData);
      return;
    }

    try {
      await onStartInterviewSession(candidateData);
    } catch (err) {
      setError(err.message || 'Failed to start interview session. Ensure backend is running.');
      setIsLoading(false);
      throw err;
    }
  };

  const handleConsentDeclined = async () => {
    try {
      await recordConsentDecline({
        candidate_name: candidateName,
        role: role,
        language: language,
        policy_version: 'v1.2',
        reason: 'candidate_declined'
      });
    } catch (err) {
      console.warn('Could not record consent decline audit:', err);
    }
  };

  // Step 2: Render full Candidate Consent Screen
  if (step === 'consent') {
    return (
      <CandidateConsentScreen 
        candidateConfig={{
          name: candidateName,
          role: role,
          language: language,
          interviewMode: interviewMode
        }}
        onConsentGranted={handleConsentGranted}
        onConsentDeclined={handleConsentDeclined}
        onBackToSetup={() => setStep('config')}
        onLanguageChange={(newLang) => setLanguage(newLang)}
      />
    );
  }

  // Step 1: Render Candidate Configuration (Role, Language, Mode, Profile Name)
  return (
    <div className="container" style={{ maxWidth: '780px', paddingTop: '40px', paddingBottom: '70px' }}>
      
      {/* Step Header */}
      <div style={{ textAlign: 'center', marginBottom: '36px' }}>
        <span className="badge badge-purple" style={{ marginBottom: '8px' }}>
          {language === 'hi' ? 'चरण 1: उम्मीदवार कॉन्फ़िगरेशन' : 'Step 1: Candidate Setup'}
        </span>
        <h2 style={{ fontSize: '2.2rem', fontWeight: 800 }}>
          Setup Your <span className="text-gradient">Interview Session</span>
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.98rem' }}>
          {language === 'hi' 
            ? 'अपनी पसंदीदा भाषा, बातचीत का तरीका चुनें और अगले चरण में सहमति की समीक्षा करें।' 
            : 'Configure your preferred assessment language, interaction mode, and proceed to consent verification.'}
        </p>
      </div>

      <div className="glass-panel" style={{ padding: '36px', display: 'flex', flexDirection: 'column', gap: '28px' }}>
        
        {/* Role Selection */}
        <div>
          <label style={{ display: 'block', fontSize: '0.92rem', fontWeight: 700, marginBottom: '10px' }}>
            <Briefcase size={16} style={{ display: 'inline', marginRight: '6px' }} />
            Target Job Role
          </label>
          <div style={{
            padding: '14px 18px',
            background: 'rgba(255, 255, 255, 0.04)',
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#fff' }}>
                Software Developer Intern
              </div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                5 core skill categories: Fundamentals, Problem Solving, DSA, Technical, Communication
              </div>
            </div>
            <span className="badge badge-easy">Active Role</span>
          </div>
        </div>

        {/* Candidate Identifier (Privacy-First) */}
        <div>
          <label style={{ display: 'block', fontSize: '0.92rem', fontWeight: 700, marginBottom: '10px' }}>
            <User size={16} style={{ display: 'inline', marginRight: '6px' }} />
            Candidate Profile (Privacy Protected)
          </label>
          <input 
            type="text"
            value={candidateName}
            onChange={(e) => setCandidateName(e.target.value)}
            style={{
              width: '100%',
              padding: '12px 16px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: 'var(--radius-sm)',
              color: '#fff',
              fontFamily: 'inherit',
              fontSize: '0.95rem'
            }}
            placeholder="e.g. Anonymous Candidate #042"
          />
          <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginTop: '6px' }}>
            Notice: No personal, demographic, or identifying attributes are stored or evaluated.
          </div>
        </div>

        {/* Language Selection (Mandatory English & Hindi) */}
        <div>
          <label style={{ display: 'block', fontSize: '0.92rem', fontWeight: 700, marginBottom: '10px' }}>
            <Languages size={16} style={{ display: 'inline', marginRight: '6px' }} />
            Interview Language (चुनी गई भाषा)
          </label>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            {/* English Card */}
            <div 
              onClick={() => setLanguage('en')}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: language === 'en' ? '2px solid #6366f1' : '1px solid var(--bg-card-border)',
                background: language === 'en' ? 'rgba(99, 102, 241, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}
            >
              <div style={{ fontSize: '1.8rem' }}>🇬🇧</div>
              <div>
                <div style={{ fontWeight: 700, color: language === 'en' ? '#fff' : 'var(--text-muted)' }}>
                  English
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  Questions & answers in English
                </div>
              </div>
            </div>

            {/* Hindi Card */}
            <div 
              onClick={() => setLanguage('hi')}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: language === 'hi' ? '2px solid #06b6d4' : '1px solid var(--bg-card-border)',
                background: language === 'hi' ? 'rgba(6, 182, 212, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}
            >
              <div style={{ fontSize: '1.8rem' }}>🇮🇳</div>
              <div>
                <div style={{ fontWeight: 700, color: language === 'hi' ? '#fff' : 'var(--text-muted)' }}>
                  हिंदी (Hindi)
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  सवाल और जवाब हिंदी में
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Interaction Mode Selection (Text vs Voice) */}
        <div>
          <label style={{ display: 'block', fontSize: '0.92rem', fontWeight: 700, marginBottom: '10px' }}>
            Interview Mode (Interaction Style)
          </label>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
            <div 
              onClick={() => setInterviewMode('text')}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: interviewMode === 'text' ? '2px solid #818cf8' : '1px solid var(--bg-card-border)',
                background: interviewMode === 'text' ? 'rgba(99, 102, 241, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}
            >
              <FileText size={24} color={interviewMode === 'text' ? '#818cf8' : '#94a3b8'} />
              <div>
                <div style={{ fontWeight: 700, color: interviewMode === 'text' ? '#fff' : 'var(--text-muted)' }}>
                  Text Mode
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  Type answers in markdown/text
                </div>
              </div>
            </div>

            <div 
              onClick={() => setInterviewMode('voice')}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                border: interviewMode === 'voice' ? '2px solid #10b981' : '1px solid var(--bg-card-border)',
                background: interviewMode === 'voice' ? 'rgba(16, 185, 129, 0.12)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '12px'
              }}
            >
              <Mic size={24} color={interviewMode === 'voice' ? '#34d399' : '#94a3b8'} />
              <div>
                <div style={{ fontWeight: 700, color: interviewMode === 'voice' ? '#fff' : 'var(--text-muted)' }}>
                  Voice Mode
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>
                  Microphone speech-to-text
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Step Transition Information Banner */}
        <div style={{
          padding: '20px 22px',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          borderRadius: 'var(--radius-sm)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <ShieldCheck size={20} color="#818cf8" />
            <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#e0e7ff', margin: 0 }}>
              {language === 'hi' ? 'अगला चरण: उम्मीदवार सहमति एवं प्रकटीकरण' : 'Next Step: Candidate Consent & Transparency Disclosures'}
            </h4>
          </div>

          <p style={{ fontSize: '0.86rem', color: 'var(--text-muted)', lineHeight: 1.55, margin: 0 }}>
            {language === 'hi'
              ? 'इंटरव्यू प्रारंभ करने से पहले आपको AI मूल्यांकन, आवाज़ ट्रांसक्रिप्शन तथा डेटा उपयोग से संबंधित विस्तृत सहमति शर्तें दिखाई जाएँगी।'
              : 'Before any AI questions are generated, you will review the candidate consent terms explaining AI assessment, speech transcription, and data privacy safeguards.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px' }}>
          <button 
            type="button" 
            className="btn btn-secondary"
            onClick={onCancel}
            disabled={isLoading}
          >
            {language === 'hi' ? 'रद्द करें' : 'Cancel'}
          </button>

          <button 
            type="button" 
            className="btn btn-primary btn-lg"
            onClick={() => setStep('consent')}
            disabled={isLoading}
          >
            {language === 'hi' ? 'सहमति शर्तें देखें और आगे बढ़ें' : 'Proceed to Candidate Consent'}
            <ArrowRight size={18} />
          </button>
        </div>

      </div>

    </div>
  );
}
