import React, { useState } from 'react';
import { 
  ShieldCheck, 
  ShieldAlert, 
  AlertCircle, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight, 
  ArrowLeft,
  Lock, 
  Eye, 
  Languages
} from 'lucide-react';

export default function CandidateConsentScreen({
  candidateConfig,
  onConsentGranted,
  onConsentDeclined,
  onBackToSetup,
  onLanguageChange
}) {
  const currentLang = candidateConfig?.language || 'en';
  const isHi = currentLang === 'hi';

  // Explicit consent checkboxes - MUST BE UNCHECKED BY DEFAULT
  const [readUnderstood, setReadUnderstood] = useState(false);
  const [assessmentAgreed, setAssessmentAgreed] = useState(false);

  // Expandable disclosure accordions
  const [showPrivacyDetails, setShowPrivacyDetails] = useState(false);
  const [showDataUsageDetails, setShowDataUsageDetails] = useState(false);

  // State for declined view
  const [isDeclined, setIsDeclined] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const canProceed = readUnderstood && assessmentAgreed;

  const handleAgree = async () => {
    if (!canProceed) {
      setErrorMessage(
        isHi 
          ? 'कृपया आगे बढ़ने से पहले दोनों चेकबॉक्स पर टिक करके सहमति दें।' 
          : 'Please check both consent acknowledgements before proceeding.'
      );
      return;
    }
    setErrorMessage(null);
    setIsSubmitting(true);

    try {
      await onConsentGranted({
        agreed: true,
        read_understood: true,
        skill_assessment_agreed: true,
        policy_version: 'v1.2',
        categories_disclosed: [
          'ai_question_generation',
          'response_text_analysis',
          'skill_rubric_scoring',
          'voice_transcription',
          'assistive_recruiter_reporting'
        ]
      });
    } catch (err) {
      setErrorMessage(err.message || 'Failed to record consent and start session. Please try again.');
      setIsSubmitting(false);
    }
  };

  const handleDecline = async () => {
    setIsSubmitting(true);
    try {
      if (onConsentDeclined) {
        await onConsentDeclined();
      }
    } catch (err) {
      console.warn('Decline tracking notification failed:', err);
    } finally {
      setIsSubmitting(false);
      setIsDeclined(true);
    }
  };

  // If candidate explicitly declined consent, show respectful declined state
  if (isDeclined) {
    return (
      <div className="container" style={{ maxWidth: '680px', paddingTop: '60px', paddingBottom: '80px' }}>
        <div className="glass-panel" style={{ padding: '44px 36px', textAlign: 'center', border: '1px solid rgba(244, 63, 94, 0.3)' }}>
          <div style={{
            width: '64px',
            height: '64px',
            borderRadius: '50%',
            background: 'rgba(244, 63, 94, 0.12)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            color: '#f43f5e'
          }}>
            <ShieldAlert size={36} />
          </div>

          <span className="badge badge-hard" style={{ marginBottom: '14px' }}>
            {isHi ? 'सहमति अस्वीकृत' : 'Consent Declined'}
          </span>

          <h2 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '16px', color: '#fff' }}>
            {isHi ? 'सहमति नहीं दी गई' : 'Participation Declined'}
          </h2>

          <div style={{
            padding: '16px 20px',
            background: 'rgba(255, 255, 255, 0.03)',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--bg-card-border)',
            marginBottom: '24px',
            textAlign: 'left'
          }}>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, color: '#fca5a5', marginBottom: '8px' }}>
              {isHi 
                ? 'आपने सहमति अस्वीकार कर दी है। कोई इंटरव्यू शुरू नहीं किया जाएगा।' 
                : 'You have declined consent. No interview will be started.'}
            </p>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>
              {isHi
                ? 'आपकी पसंद का पूरा सम्मान किया जाता है। कोई प्रश्न जनरेट नहीं हुआ, कोई ऑडियो रिकॉर्ड नहीं किया गया, और कोई डेटा AI सेवाओं को नहीं भेजा गया।'
                : 'Your choice is completely voluntary and respected. No interview questions were generated, no audio was recorded, and no responses were sent to AI services.'}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '14px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={() => setIsDeclined(false)}
            >
              <ArrowLeft size={16} />
              {isHi ? 'सहमति शर्तें दोबारा देखें' : 'Review Consent Again'}
            </button>

            <button 
              type="button" 
              className="btn btn-primary"
              onClick={onBackToSetup}
            >
              {isHi ? 'मुख्य पृष्ठ पर वापस जाएँ' : 'Return to Welcome Screen'}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ maxWidth: '840px', paddingTop: '36px', paddingBottom: '70px' }}>
      
      {/* Step Indicator & Language Bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <span className="badge badge-cyan" style={{ fontSize: '0.82rem' }}>
          {isHi ? 'चरण 2 ऑफ 2: उम्मीदवार सहमति एवं सुरक्षा' : 'Step 2 of 2: Candidate Consent & Transparency'}
        </span>

        {/* Live Language Switcher for Candidate Convenience */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Languages size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
            {isHi ? 'सहमति भाषा:' : 'Consent Language:'}
          </span>
          <div style={{ display: 'inline-flex', borderRadius: '6px', overflow: 'hidden', border: '1px solid var(--bg-card-border)' }}>
            <button
              type="button"
              onClick={() => onLanguageChange && onLanguageChange('en')}
              style={{
                padding: '4px 10px',
                fontSize: '0.8rem',
                fontWeight: currentLang === 'en' ? 700 : 500,
                background: currentLang === 'en' ? 'rgba(99, 102, 241, 0.25)' : 'rgba(255,255,255,0.02)',
                color: currentLang === 'en' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              🇬🇧 English
            </button>
            <button
              type="button"
              onClick={() => onLanguageChange && onLanguageChange('hi')}
              style={{
                padding: '4px 10px',
                fontSize: '0.8rem',
                fontWeight: currentLang === 'hi' ? 700 : 500,
                background: currentLang === 'hi' ? 'rgba(6, 182, 212, 0.25)' : 'rgba(255,255,255,0.02)',
                color: currentLang === 'hi' ? '#fff' : 'var(--text-muted)',
                border: 'none',
                cursor: 'pointer'
              }}
            >
              🇮🇳 हिंदी
            </button>
          </div>
        </div>
      </div>

      {/* Main Consent Card */}
      <div className="glass-panel" style={{ padding: '36px 32px' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{
            width: '54px',
            height: '54px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            color: '#fff',
            boxShadow: '0 8px 20px rgba(79, 70, 229, 0.35)'
          }}>
            <ShieldCheck size={30} />
          </div>

          <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '10px' }}>
            {isHi ? (
              <>शुरू करने से पहले — <span className="text-gradient">आपकी सहमति महत्वपूर्ण है</span></>
            ) : (
              <>Before We Begin — <span className="text-gradient">Your Consent Matters</span></>
            )}
          </h2>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.96rem', maxWidth: '640px', margin: '0 auto', lineHeight: 1.55 }}>
            {isHi ? (
              'हमारा प्लेटफ़ॉर्म AI की मदद से शुरुआती इंटरव्यू लेता है, आपके उत्तरों का विश्लेषण करता है और चुनी गई नौकरी से संबंधित कौशल का मूल्यांकन करता है।'
            ) : (
              'Welcome to the Adaptive AI Interviewer. This platform uses artificial intelligence to conduct an initial job interview, ask follow-up questions, and evaluate job-related skills against a predefined scoring rubric.'
            )}
          </p>
        </div>

        {/* Selected Session Pill Summary */}
        <div style={{
          padding: '12px 18px',
          background: 'rgba(255, 255, 255, 0.03)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--bg-card-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '10px',
          marginBottom: '26px',
          fontSize: '0.85rem'
        }}>
          <div>
            <span style={{ color: 'var(--text-dim)' }}>{isHi ? 'पद (Role): ' : 'Role: '}</span>
            <strong style={{ color: '#fff' }}>{candidateConfig?.role || 'Software Developer Intern'}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-dim)' }}>{isHi ? 'मोड (Mode): ' : 'Mode: '}</span>
            <strong style={{ color: '#38bdf8' }}>{candidateConfig?.interviewMode === 'voice' ? (isHi ? 'आवाज़ (Voice)' : 'Voice Mode') : (isHi ? 'टेक्स्ट (Text)' : 'Text Mode')}</strong>
          </div>
          <div>
            <span style={{ color: 'var(--text-dim)' }}>{isHi ? 'भाषा (Language): ' : 'Language: '}</span>
            <strong style={{ color: '#a5b4fc' }}>{isHi ? 'हिंदी (Hindi)' : 'English'}</strong>
          </div>
        </div>

        {/* Section 1: 8 Clear Consent Points */}
        <div style={{ marginBottom: '28px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '14px', color: '#e2e8f0' }}>
            {isHi ? 'कृपया आगे बढ़ने से पहले निम्नलिखित बातें समझें:' : 'Before proceeding, please understand the following:'}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            
            {/* Point 1: AI Interview */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                1
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'AI इंटरव्यू: ' : 'AI Interview: '}</strong>
                {isHi 
                  ? 'AI आपसे प्रश्न पूछेगा और आपके उत्तरों का विश्लेषण करेगा।' 
                  : 'An AI system will ask questions and analyze your answers.'}
              </div>
            </div>

            {/* Point 2: Data Processing */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                2
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'डेटा प्रोसेसिंग: ' : 'Data Processing: '}</strong>
                {isHi 
                  ? 'आपके उत्तरों और संबंधित ट्रांसक्रिप्ट को AI सेवाओं द्वारा प्रोसेस किया जा सकता है ताकि कौशल मूल्यांकन और रिपोर्ट तैयार की जा सके।' 
                  : 'Your interview responses and relevant transcripts may be processed by AI services to generate skill assessments and an interview report.'}
              </div>
            </div>

            {/* Point 3: Purpose */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                3
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'उद्देश्य: ' : 'Purpose: '}</strong>
                {isHi 
                  ? 'आपके उत्तरों का उपयोग चुनी गई नौकरी से संबंधित कौशल का मूल्यांकन करने के लिए किया जाएगा।' 
                  : 'Your responses will be used to evaluate skills relevant to the selected job role.'}
              </div>
            </div>

            {/* Point 4: Fair Evaluation */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                4
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#34d399' }}>{isHi ? 'निष्पक्ष मूल्यांकन: ' : 'Fair Evaluation: '}</strong>
                {isHi 
                  ? 'सिस्टम का उद्देश्य लिंग, धर्म, जाति, उम्र या दिखावट जैसी व्यक्तिगत विशेषताओं के बजाय नौकरी से संबंधित कौशल का मूल्यांकन करना है।' 
                  : 'The system is designed to evaluate job-related skills rather than personal characteristics such as gender, religion, caste, age, or appearance.'}
              </div>
            </div>

            {/* Point 5: Human Oversight */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                5
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'मानवीय निगरानी: ' : 'Human Oversight: '}</strong>
                {isHi 
                  ? 'AI द्वारा दिए गए स्कोर केवल सहायक मूल्यांकन हैं। अंतिम भर्ती का निर्णय मानव रिक्रूटर करेगा।' 
                  : 'AI-generated scores are assistive assessments, not final hiring decisions. A human recruiter is responsible for the final hiring decision.'}
              </div>
            </div>

            {/* Point 6: Voice Recording & Processing (Accurate grounded disclosure) */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                6
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'आवाज़ और डेटा: ' : 'Voice Recording: '}</strong>
                {isHi ? (
                  <>
                    यदि आप आवाज़ मोड से उत्तर देते हैं, तो ब्राउज़र के Web Speech API द्वारा आपकी आवाज़ को रियल-टाइम में टेक्स्ट में बदला जाता है। हमारा बैकएंड सर्वर कच्ची ऑडियो फाइलें (.mp3/.wav) स्टोर नहीं करता; केवल टेक्स्ट ट्रांसक्रिप्ट ही मूल्यांकन के लिए प्रोसेस होता है। ऑडियो प्रोसेसिंग आपके ब्राउज़र के स्पीच इंजन द्वारा की जाती है।
                  </>
                ) : (
                  <>
                    If voice input is enabled, audio is transcribed to text in real time using your browser's Web Speech API. The backend server does not record or store raw audio files; only the resulting text transcripts are transmitted and saved for assessment. Speech recognition is processed through browser speech services according to your browser vendor's terms.
                  </>
                )}
              </div>
            </div>

            {/* Point 7: Data Retention & Policy (Accurate grounded disclosure) */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(99, 102, 241, 0.2)', color: '#818cf8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                7
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'डेटा की अवधि: ' : 'Data Retention: '}</strong>
                {isHi ? (
                  <>
                    आपके उत्तर, ट्रांसक्रिप्ट और स्कोर स्थानीय डेटाबेस (intervueai.db) में सुरक्षित रहते हैं। वर्तमान वातावरण में कोई स्वचालित विलोपन (auto-deletion) नीति लागू नहीं है; डेटा प्रतिधारण नीति को संस्थागत मानकों के अनुसार व्यवस्थापक द्वारा कॉन्फ़िगर किया जाना है।
                  </>
                ) : (
                  <>
                    Your responses, transcripts, and evaluation scores are currently stored in a local SQLite application database (<code style={{ color: '#38bdf8' }}>intervueai.db</code>). An automated retention and deletion schedule is not currently configured for this deployment and needs to be configured by system administrators according to organizational requirements.
                  </>
                )}
              </div>
            </div>

            {/* Point 8: Your Choice */}
            <div style={{
              padding: '14px 18px',
              background: 'rgba(255, 255, 255, 0.02)',
              borderRadius: '8px',
              border: '1px solid var(--bg-card-border)',
              display: 'flex',
              gap: '14px',
              alignItems: 'flex-start'
            }}>
              <div style={{ minWidth: '28px', height: '28px', borderRadius: '50%', background: 'rgba(16, 185, 129, 0.2)', color: '#34d399', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '0.85rem' }}>
                8
              </div>
              <div style={{ fontSize: '0.92rem', lineHeight: 1.5, color: '#cbd5e1' }}>
                <strong style={{ color: '#fff' }}>{isHi ? 'आपकी पसंद: ' : 'Your Choice: '}</strong>
                {isHi 
                  ? 'सहमति देना स्वैच्छिक है। आप सहमति देने से मना कर सकते हैं और इंटरव्यू शुरू नहीं होगा।' 
                  : 'Participation is voluntary. You can decline consent and leave the interview without being forced to continue.'}
              </div>
            </div>

          </div>
        </div>

        {/* Expandable Technical Disclosures */}
        <div style={{ marginBottom: '28px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          
          {/* Privacy Information Accordion */}
          <div style={{
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <button
              type="button"
              onClick={() => setShowPrivacyDetails(!showPrivacyDetails)}
              style={{
                width: '100%',
                padding: '12px 18px',
                background: 'none',
                border: 'none',
                color: '#e2e8f0',
                fontSize: '0.9rem',
                fontWeight: 600,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Lock size={16} color="#818cf8" />
                {isHi ? '📋 गोपनीयता जानकारी और डेटा प्रोसेसिंग श्रेणियाँ' : '📋 Privacy Information & Disclosed Processing Categories'}
              </span>
              {showPrivacyDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showPrivacyDetails && (
              <div style={{ padding: '16px 20px', borderTop: '1px solid var(--bg-card-border)', fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.6 }}>
                <p style={{ margin: '0 0 10px 0', color: '#cbd5e1' }}>
                  {isHi ? 'इस इंटरव्यू में निम्नलिखित 5 श्रेणियों के अंतर्गत डेटा प्रोसेस किया जाता है:' : 'The following 5 categories of data processing are disclosed and applied:'}
                </p>
                <ul style={{ margin: '0 0 10px 20px', padding: 0 }}>
                  <li><strong style={{ color: '#fff' }}>AI Question Generation:</strong> {isHi ? 'कौशल के आधार पर प्रश्नों का चयन' : 'Selecting questions dynamically from calibrated difficulty tiers.'}</li>
                  <li><strong style={{ color: '#fff' }}>Response Text Analysis:</strong> {isHi ? 'उत्तरों में तकनीकी अवधारणाओं की जाँच' : 'Analyzing technical reasoning, concepts, and structure.'}</li>
                  <li><strong style={{ color: '#fff' }}>Skill Rubric Scoring:</strong> {isHi ? '5 प्रमुख कौशलों पर 0-100 का पारदर्शी स्कोर' : 'Deterministic score calculation against job competency rubrics.'}</li>
                  <li><strong style={{ color: '#fff' }}>Voice Transcription:</strong> {isHi ? 'क्लाइंट-साइड स्पीच-टू-टेक्स्ट रूपांतरण' : 'Browser-based transcription; no raw audio files stored.'}</li>
                  <li><strong style={{ color: '#fff' }}>Assistive Recruiter Reporting:</strong> {isHi ? 'मानव रिक्रूटर के लिए साक्ष्य-आधारित उद्धरण' : 'Verbatim evidence citations highlighted for recruiter review.'}</li>
                </ul>
                <p style={{ margin: 0, fontSize: '0.8rem', color: '#64748b' }}>
                  Policy Version: v1.2 • Regulatory Alignment: Assistive AI & Equal Employment Principles.
                </p>
              </div>
            )}
          </div>

          {/* Data Usage & Safeguards Accordion */}
          <div style={{
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.02)'
          }}>
            <button
              type="button"
              onClick={() => setShowDataUsageDetails(!showDataUsageDetails)}
              style={{
                width: '100%',
                padding: '12px 18px',
                background: 'none',
                border: 'none',
                color: '#e2e8f0',
                fontSize: '0.9rem',
                fontWeight: 600,
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer'
              }}
            >
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Eye size={16} color="#06b6d4" />
                {isHi ? '🛡️ डेटा सुरक्षा और भेदभाव-रोधी सुरक्षा उपाय' : '🛡️ Data Usage Safeguards & Anti-Bias Measures'}
              </span>
              {showDataUsageDetails ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
            </button>

            {showDataUsageDetails && (
              <div style={{ padding: '16px 20px', borderTop: '1px solid var(--bg-card-border)', fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.6 }}>
                <p style={{ margin: '0 0 8px 0', color: '#cbd5e1' }}>
                  {isHi 
                    ? 'असंबंधित व्यक्तिगत जानकारी (जैसे लिंग, धर्म, जाति, क्षेत्र) स्वचालित रूप से मूल्यांकन से बाहर रखी जाती है।' 
                    : 'Non-job-related personal characteristics (gender, religion, caste, region, age) are filtered and prevented from influencing scores.'}
                </p>
                <p style={{ margin: 0 }}>
                  {isHi 
                    ? 'हिंदी और अंग्रेज़ी दोनों भाषाओं के उत्तरों का मूल्यांकन समान तकनीकी मानकों पर किया जाता है। किसी भाषा के लिए कोई नकारात्मक अंक नहीं काटा जाता।' 
                    : 'Both Hindi and English responses are evaluated on identical technical criteria. There is zero score penalty for choosing Hindi.'}
                </p>
              </div>
            )}
          </div>

        </div>

        {/* Anti-Cheating & Active Focus Policy Notice */}
        <div style={{
          padding: '16px 20px',
          background: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.35)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '24px',
          display: 'flex',
          gap: '14px',
          alignItems: 'flex-start'
        }}>
          <ShieldAlert size={22} color="#f87171" style={{ flexShrink: 0, marginTop: '2px' }} />
          <div style={{ fontSize: '0.88rem', lineHeight: 1.5, color: '#fca5a5' }}>
            <strong style={{ color: '#fef2f2', display: 'block', marginBottom: '4px', fontSize: '0.92rem' }}>
              {isHi ? '⚠️ महत्वपूर्ण: सक्रिय पृष्ठ और एंटी-चीटिंग फ़ोकस नीति' : '⚠️ Important: Active Tab & Anti-Cheating Focus Policy'}
            </strong>
            <p style={{ margin: '0 0 4px 0' }}>
              {isHi
                ? 'During this interview, leaving or switching away from the interview page may end your session. Please close unrelated tabs and keep this page active. (साक्षात्कार के दौरान, साक्षात्कार पृष्ठ से बाहर जाने या टैब बदलने से आपका सत्र समाप्त हो जाएगा। कृपया अन्य सभी टैब बंद रखें।)'
                : 'During this interview, leaving or switching away from the interview page may end your session. Please close unrelated tabs and keep this page active.'}
            </p>
            <span style={{ fontSize: '0.8rem', color: '#cbd5e1', display: 'block' }}>
              {isHi
                ? 'सत्र केवल सक्रिय टैब में रहकर ही पूरा किया जा सकता है। एक बार फ़ोकस उल्लंघन दर्ज होने पर इंटरव्यू फिर से शुरू नहीं होगा।'
                : 'Session requires maintaining active page focus. Once terminated due to a confirmed focus violation, the session cannot be resumed.'}
            </span>
          </div>
        </div>

        {/* Section 2: Explicit Consent Controls (Unchecked by Default) */}
        <fieldset style={{
          padding: '24px',
          background: 'rgba(99, 102, 241, 0.08)',
          border: '1px solid rgba(99, 102, 241, 0.35)',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '24px'
        }}>
          <legend style={{
            fontSize: '0.88rem',
            fontWeight: 700,
            color: '#a5b4fc',
            padding: '0 8px',
            textTransform: 'uppercase',
            letterSpacing: '0.04em'
          }}>
            {isHi ? 'अनिवार्य सहमति घोषणा (Mandatory Consent)' : 'Mandatory Candidate Declaration'}
          </legend>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            
            {/* Checkbox 1 */}
            <label 
              htmlFor="consent-checkbox-understand"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                cursor: 'pointer',
                userSelect: 'none'
              }}
            >
              <input 
                id="consent-checkbox-understand"
                type="checkbox"
                checked={readUnderstood}
                onChange={(e) => setReadUnderstood(e.target.checked)}
                style={{
                  width: '19px',
                  height: '19px',
                  marginTop: '2px',
                  accentColor: '#4f46e5',
                  cursor: 'pointer'
                }}
              />
              <span style={{ fontSize: '0.94rem', color: '#f1f5f9', fontWeight: 600, lineHeight: 1.5 }}>
                {isHi 
                  ? 'मैंने पढ़ लिया है और समझ लिया है कि मेरे इंटरव्यू के उत्तरों को कैसे प्रोसेस किया जाएगा।' 
                  : 'I have read and understood how my interview responses will be processed.'}
              </span>
            </label>

            {/* Checkbox 2 */}
            <label 
              htmlFor="consent-checkbox-assessment"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: '12px',
                cursor: 'pointer',
                userSelect: 'none'
              }}
            >
              <input 
                id="consent-checkbox-assessment"
                type="checkbox"
                checked={assessmentAgreed}
                onChange={(e) => setAssessmentAgreed(e.target.checked)}
                style={{
                  width: '19px',
                  height: '19px',
                  marginTop: '2px',
                  accentColor: '#4f46e5',
                  cursor: 'pointer'
                }}
              />
              <span style={{ fontSize: '0.94rem', color: '#f1f5f9', fontWeight: 600, lineHeight: 1.5 }}>
                {isHi 
                  ? 'मैं AI की सहायता से नौकरी से संबंधित कौशल के मूल्यांकन के लिए अपने इंटरव्यू के उत्तरों को प्रोसेस करने की सहमति देता/देती हूँ।' 
                  : 'I consent to the processing of my interview responses for AI-assisted, job-related skill assessment.'}
              </span>
            </label>

          </div>

          <div style={{ marginTop: '12px', fontSize: '0.78rem', color: '#94a3b8' }}>
            ℹ️ {isHi ? 'आगे बढ़ने के लिए दोनों चेकबॉक्स को चुनना अनिवार्य है।' : 'Both checkboxes must be selected before starting the interview.'}
          </div>
        </fieldset>

        {/* Error notification if any */}
        {errorMessage && (
          <div style={{
            padding: '12px 16px',
            background: 'rgba(244, 63, 94, 0.1)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            borderRadius: 'var(--radius-sm)',
            color: '#fca5a5',
            fontSize: '0.88rem',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <AlertCircle size={18} />
            {errorMessage}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '14px',
          paddingTop: '8px'
        }}>
          {/* Decline & Exit Button */}
          <button
            type="button"
            className="btn btn-secondary"
            onClick={handleDecline}
            disabled={isSubmitting}
            style={{
              borderColor: 'rgba(244, 63, 94, 0.4)',
              color: '#fca5a5',
              padding: '12px 20px'
            }}
          >
            {isHi ? 'सहमति नहीं दें — बाहर निकलें' : 'Decline & Exit'}
          </button>

          {/* Agree & Start Interview Button */}
          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleAgree}
            disabled={!canProceed || isSubmitting}
            style={{
              opacity: canProceed && !isSubmitting ? 1 : 0.5,
              cursor: canProceed && !isSubmitting ? 'pointer' : 'not-allowed',
              padding: '14px 28px'
            }}
          >
            {isSubmitting ? (
              isHi ? 'सहमति सत्यापित हो रही है...' : 'Verifying Consent & Starting...'
            ) : (
              <>
                {isHi ? 'मैं सहमत हूँ — बायोडाटा अपलोड पर जाएं' : 'I Agree — Proceed to Resume Upload'}
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </div>

      </div>

    </div>
  );
}
