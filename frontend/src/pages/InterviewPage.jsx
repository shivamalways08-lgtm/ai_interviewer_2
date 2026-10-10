import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  Volume2, 
  VolumeX, 
  Mic, 
  Square, 
  Send, 
  Sparkles, 
  CheckCircle2, 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  ArrowRight, 
  Layers, 
  FileText,
  AlertCircle,
  HelpCircle,
  Clock,
  AlertTriangle,
  Hourglass,
  Lock,
  ShieldAlert,
  RotateCcw
} from 'lucide-react';
import { useSpeech } from '../hooks/useSpeech';
import { expireInterviewSession, fetchInterviewState, recordFocusViolation } from '../services/api';

const SKILLS_LIST = [
  "Programming Fundamentals",
  "Problem Solving",
  "Data Structures & Algorithms",
  "Technical Understanding",
  "Communication"
];

export default function InterviewPage({ 
  interviewSession, 
  onSubmitAnswer, 
  onFinishInterview 
}) {
  const { candidate_id, interview_id, language, interview_mode, first_question } = interviewSession;

  const [currentQuestion, setCurrentQuestion] = useState(first_question);
  const [candidateAnswer, setCandidateAnswer] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [evaluationFeedback, setEvaluationFeedback] = useState(null);
  const [showFeedbackModal, setShowFeedbackModal] = useState(false);
  const [difficultyHistory, setDifficultyHistory] = useState([first_question?.difficulty || 'MEDIUM']);
  const [errorMessage, setErrorMessage] = useState(null);

  // Authoritative 20-Minute Timer and Termination State
  const getInitialSeconds = () => {
    if (interviewSession?.deadline_at) {
      const deadlineMs = new Date(interviewSession.deadline_at).getTime();
      const diff = Math.floor((deadlineMs - Date.now()) / 1000);
      return Math.max(0, diff);
    }
    return interviewSession?.remaining_seconds != null ? Math.floor(interviewSession.remaining_seconds) : 1200;
  };

  const getInitialTerminated = () => {
    const status = interviewSession?.status;
    return status === 'TIME_EXPIRED' || status === 'TERMINATED_WEAK_ANSWERS' || status === 'TERMINATED_FOCUS_VIOLATION' || status === 'completed';
  };

  const [secondsLeft, setSecondsLeft] = useState(getInitialSeconds);
  const [isTerminated, setIsTerminated] = useState(getInitialTerminated);
  const [terminationType, setTerminationType] = useState(interviewSession?.status || null);
  const [terminationTimestamp, setTerminationTimestamp] = useState(
    interviewSession?.focus_violation_at || interviewSession?.completed_at || null
  );
  const [violationNetworkError, setViolationNetworkError] = useState(null);
  const [isRetryingViolation, setIsRetryingViolation] = useState(false);
  const [consecutiveWeakCount, setConsecutiveWeakCount] = useState(interviewSession?.consecutive_weak_answers || 0);
  const [questionElapsedSeconds, setQuestionElapsedSeconds] = useState(0);

  const isTerminatedRef = useRef(isTerminated);
  const hasTriggeredViolationRef = useRef(isTerminated);

  // Per-question timer resets on each new question
  useEffect(() => {
    setQuestionElapsedSeconds(0);
  }, [currentQuestion?.question_id]);

  useEffect(() => {
    if (isTerminated || showFeedbackModal || isSubmitting) return;
    const interval = setInterval(() => {
      setQuestionElapsedSeconds(prev => prev + 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isTerminated, showFeedbackModal, isSubmitting]);

  useEffect(() => {
    isTerminatedRef.current = isTerminated;
    if (isTerminated) {
      hasTriggeredViolationRef.current = true;
    }
  }, [isTerminated]);

  // Sync state with server on mount to restore remaining time and prevent refresh bypass
  useEffect(() => {
    let isMounted = true;
    async function syncBackendState() {
      try {
        const state = await fetchInterviewState(interview_id);
        if (!isMounted) return;
        const intv = state?.interview;
        if (intv) {
          if (intv.deadline_at) {
            const dlMs = new Date(intv.deadline_at).getTime();
            const rem = Math.max(0, Math.floor((dlMs - Date.now()) / 1000));
            setSecondsLeft(rem);
            if (rem <= 0) {
              setIsTerminated(true);
              setTerminationType('TIME_EXPIRED');
            }
          }
          if (intv.consecutive_weak_answers != null) {
            setConsecutiveWeakCount(intv.consecutive_weak_answers);
          }
          if (intv.status === 'TIME_EXPIRED') {
            setIsTerminated(true);
            setTerminationType('TIME_EXPIRED');
            setTerminationTimestamp(intv.completed_at || new Date().toISOString());
          } else if (intv.status === 'TERMINATED_WEAK_ANSWERS') {
            setIsTerminated(true);
            setTerminationType('TERMINATED_WEAK_ANSWERS');
            setTerminationTimestamp(intv.completed_at || new Date().toISOString());
          } else if (intv.status === 'TERMINATED_FOCUS_VIOLATION') {
            setIsTerminated(true);
            setTerminationType('TERMINATED_FOCUS_VIOLATION');
            setTerminationTimestamp(intv.focus_violation_at || intv.completed_at || new Date().toISOString());
          } else if (intv.status === 'completed') {
            setIsTerminated(true);
            setTerminationType('NORMAL');
            setTerminationTimestamp(intv.completed_at || new Date().toISOString());
          }
        }
      } catch (err) {
        console.warn('Sync interview state failed:', err);
      }
    }
    if (interview_id) syncBackendState();
    return () => { isMounted = false; };
  }, [interview_id]);

  // Handler to trigger focus violation and notify backend
  const triggerFocusViolation = async (signalDetail) => {
    if (isTerminatedRef.current || hasTriggeredViolationRef.current) return;
    hasTriggeredViolationRef.current = true;
    isTerminatedRef.current = true;

    const violationTime = new Date().toISOString();
    setIsTerminated(true);
    setTerminationType('TERMINATED_FOCUS_VIOLATION');
    setTerminationTimestamp(violationTime);
    stopSpeaking();
    if (isListening) stopListening();

    try {
      const res = await recordFocusViolation(interview_id, {
        details: `Focus violation detected: ${signalDetail} at ${violationTime}`
      });
      if (res?.completed_at) {
        setTerminationTimestamp(res.completed_at);
      }
      setViolationNetworkError(null);
    } catch (err) {
      console.error('Focus violation recording failed:', err);
      setViolationNetworkError(
        language === 'hi'
          ? 'सर्वर पर उल्लंघन दर्ज करने में नेटवर्क त्रुटि। अनधिकृत निरंतरता को रोकने के लिए आपका साक्षात्कार लॉक कर दिया गया है।'
          : 'Network error confirming termination with server. Your interview interface remains locked to prevent continuation.'
      );
    }
  };

  const handleRetryViolation = async () => {
    setIsRetryingViolation(true);
    try {
      const res = await recordFocusViolation(interview_id, {
        details: 'Manual retry after network interruption'
      });
      if (res?.completed_at) {
        setTerminationTimestamp(res.completed_at);
      }
      setViolationNetworkError(null);
    } catch (err) {
      setViolationNetworkError(err.message || 'Retry failed. Server still unreachable.');
    } finally {
      setIsRetryingViolation(false);
    }
  };

  // Browser Focus & Visibility Monitoring (active interview only)
  useEffect(() => {
    if (isTerminated) return;

    // Primary detection: document visibilitychange (hidden state)
    const handleVisibilityChange = () => {
      if (isTerminatedRef.current || hasTriggeredViolationRef.current) return;
      if (document.visibilityState === 'hidden') {
        triggerFocusViolation('document.visibilityState is hidden (tab switch, browser minimized, or application switch)');
      }
    };

    // Additional lifecycle signal: pagehide
    const handlePageHide = () => {
      if (isTerminatedRef.current || hasTriggeredViolationRef.current) return;
      triggerFocusViolation('pagehide event (page navigating away or tab closing)');
    };

    // Supplementary signal: blur (only if hidden, never terminate solely on blur)
    const handleWindowBlur = () => {
      if (document.visibilityState === 'hidden') {
        if (!isTerminatedRef.current && !hasTriggeredViolationRef.current) {
          triggerFocusViolation('window.blur with hidden visibilityState');
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('pagehide', handlePageHide);
    window.addEventListener('blur', handleWindowBlur);

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('pagehide', handlePageHide);
      window.removeEventListener('blur', handleWindowBlur);
    };
  }, [interview_id, isTerminated, language]);

  // Tick countdown timer every second
  useEffect(() => {
    if (isTerminated) return;

    const tick = () => {
      if (interviewSession?.deadline_at) {
        const dlMs = new Date(interviewSession.deadline_at).getTime();
        const rem = Math.max(0, Math.floor((dlMs - Date.now()) / 1000));
        setSecondsLeft(rem);
        if (rem <= 0) {
          handleTimeExpired();
        }
      } else {
        setSecondsLeft(prev => {
          if (prev <= 1) {
            handleTimeExpired();
            return 0;
          }
          return prev - 1;
        });
      }
    };

    const timerId = setInterval(tick, 1000);
    return () => clearInterval(timerId);
  }, [interviewSession?.deadline_at, isTerminated]);

  const handleTimeExpired = async () => {
    setIsTerminated(true);
    setTerminationType('TIME_EXPIRED');
    stopSpeaking();
    if (isListening) stopListening();
    try {
      await expireInterviewSession(interview_id);
    } catch (e) {
      console.warn('Expire call failed:', e);
    }
  };

  const formatTimer = (totalSecs) => {
    const s = Math.max(0, Math.floor(totalSecs));
    const m = Math.floor(s / 60);
    const sec = s % 60;
    return `${m.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
  };

  // Web Speech hook
  const { 
    isListening, 
    transcript, 
    setTranscript, 
    speechError, 
    isRecognitionSupported, 
    startListening, 
    stopListening, 
    resetTranscript, 
    isSpeaking, 
    speak, 
    stopSpeaking 
  } = useSpeech(language);

  // Sync speech transcript into candidate answer in voice mode
  useEffect(() => {
    if (transcript) {
      setCandidateAnswer(transcript);
    }
  }, [transcript]);

  // Read question aloud when question loads if voice mode
  useEffect(() => {
    if (currentQuestion && interview_mode === 'voice' && !isTerminated) {
      speak(currentQuestion.question_text, language);
    }
    return () => stopSpeaking();
  }, [currentQuestion, isTerminated]);

  const handleSpeakToggle = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      speak(currentQuestion?.question_text, language);
    }
  };

  const handleMicToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      resetTranscript();
      startListening();
    }
  };

  const fillSampleAnswer = (type) => {
    const isHi = language === 'hi';
    const qSkill = (currentQuestion?.skill || '').toLowerCase();
    const qText = (currentQuestion?.question_text || '').toLowerCase();

    if (qSkill.includes('react') || qText.includes('react') || qText.includes('props')) {
      if (type === 'strong') {
        setCandidateAnswer(
          isHi 
            ? "React में Props पैरेंट कॉम्पोनेंट द्वारा चाइल्ड को पास किए जाने वाले read-only और immutable इनपुट होते हैं, जबकि State कॉम्पोनेंट का आंतरिक mutable डेटा है। जब State बदलती है तो React virtual DOM reconciliation के ज़रिये UI को कुशलतापूर्वक re-render करता है।"
            : "In React, props are immutable read-only inputs passed from parent to child components, maintaining unidirectional data flow. State is local, mutable component data. Updating state triggers React's virtual DOM reconciliation and schedule-based re-rendering."
        );
      } else if (type === 'average') {
        setCandidateAnswer(
          isHi
            ? "Props बाहर से कॉम्पोनेंट में आते हैं और State अंदर बनती है। State बदलने पर पेज अपडेट होता है।"
            : "Props are passed into components from parents and state is created inside the component. State makes components interactive and updates the UI."
        );
      } else {
        setCandidateAnswer(
          isHi
            ? "React में कॉम्पोनेंट होते हैं और वो वेबसाइट बनाते हैं।"
            : "React has components and buttons for websites."
        );
      }
    } else if (qSkill.includes('project') || qText.includes('architecture') || qText.includes('project')) {
      if (type === 'strong') {
        setCandidateAnswer(
          isHi
            ? "इस प्रोजेक्ट का आर्किटेक्चर क्लाइंट-सर्वर मॉडल पर आधारित है जहाँ फ्रंटएंड स्टेट मैनेजमेंट और RESTful API कॉल्स को अलग-अलग मॉड्यूल में संभाला गया है। हमने JWT ऑथेंटिकेशन, एरर बाउंड्रीज और डेटाबेस में इंडेक्सिंग का उपयोग करके लेटेंसी और सुरक्षा सुनिश्चित की।"
            : "The architecture follows a decoupled client-server structure where presentation logic is separated from state management and asynchronous REST API communication. We implemented JWT authentication, client-side error boundaries, and optimized database queries with appropriate indexes."
        );
      } else if (type === 'average') {
        setCandidateAnswer(
          isHi
            ? "मैंने फ्रंटएंड में UI बनाया और बैकएंड API से डेटा लाकर डेटाबेस में स्टोर किया।"
            : "I built the frontend with UI components and connected it to a backend API that saves and queries data from a database."
        );
      } else {
        setCandidateAnswer(
          isHi
            ? "यह एक सामान्य कॉलेज प्रोजेक्ट है जो मैंने बनाया था।"
            : "It is a standard web application project with some features."
        );
      }
    } else if (qSkill.includes('python') || qText.includes('python') || qText.includes('tuple')) {
      if (type === 'strong') {
        setCandidateAnswer(
          isHi
            ? "Python में Lists mutable होती हैं जिन्हें इन-प्लेस बदला जा सकता है, जबकि Tuples immutable होते हैं। Tuples मेमोरी-कुशल होते हैं और hashable होने के कारण dictionary keys के रूप में उपयोग किए जा सकते हैं।"
            : "In Python, lists are mutable sequence types supporting in-place modification, while tuples are immutable once created. Tuples have lower memory overhead and are hashable, meaning they can serve as dictionary keys."
        );
      } else if (type === 'average') {
        setCandidateAnswer(
          isHi
            ? "List को बदल सकते हैं लेकिन Tuple को नहीं बदल सकते।"
            : "Lists can be modified and tuples cannot be changed."
        );
      } else {
        setCandidateAnswer(
          isHi
            ? "Python में डेटा स्टोर करने के लिए ये होते हैं।"
            : "Python uses them to store data."
        );
      }
    } else {
      // Default: Programming Fundamentals / Memory
      if (type === 'strong') {
        setCandidateAnswer(
          isHi 
            ? "Stack मेमोरी LIFO सिद्धांत पर काम करती है और लोकल वेरिएबल्स के लिए होती है जो बहुत तेज़ है। Heap मेमोरी डायनेमिक ऑब्जेक्ट्स के लिए होती है और इसे गारबेज कलेक्टर से फ्री किया जाता है।"
            : "Stack memory is organized as a Last-In-First-Out structure for local variables and function calls, which is extremely fast. Heap memory is used for dynamic memory allocation for objects that live beyond single scopes and requires garbage collection."
        );
      } else if (type === 'average') {
        setCandidateAnswer(
          isHi 
            ? "Stack फ़ंक्शन के अंदर के वेरिएबल्स के लिए होता है और Heap ऑब्जेक्ट्स के लिए। Stack तेज़ होता है।"
            : "Stack is fast memory used for local function variables. Heap is larger memory used when you create new objects with the new keyword."
        );
      } else {
        setCandidateAnswer(
          isHi 
            ? "मेमोरी दो तरह की होती है बस।"
            : "Stack is for data and heap is a pile of memory."
        );
      }
    }
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    if (isTerminated) return;
    if (!candidateAnswer.trim()) {
      setErrorMessage('Please type or speak an answer before submitting.');
      return;
    }
    setErrorMessage(null);
    setIsSubmitting(true);
    stopSpeaking();
    if (isListening) stopListening();

    try {
      const result = await onSubmitAnswer({
        interview_id: interview_id,
        question_id: currentQuestion.question_id,
        candidate_answer: candidateAnswer.trim(),
        response_time_seconds: questionElapsedSeconds
      });

      if (result.consecutive_weak_answers != null) {
        setConsecutiveWeakCount(result.consecutive_weak_answers);
      }

      if (result.termination_reason === 'TERMINATED_WEAK_ANSWERS' || result.status === 'TERMINATED_WEAK_ANSWERS') {
        setIsTerminated(true);
        setTerminationType('TERMINATED_WEAK_ANSWERS');
      } else if (result.termination_reason === 'TIME_EXPIRED' || result.status === 'TIME_EXPIRED') {
        setIsTerminated(true);
        setTerminationType('TIME_EXPIRED');
      } else if (result.termination_reason === 'TERMINATED_FOCUS_VIOLATION' || result.status === 'TERMINATED_FOCUS_VIOLATION') {
        setIsTerminated(true);
        setTerminationType('TERMINATED_FOCUS_VIOLATION');
      }

      setEvaluationFeedback(result);
      setShowFeedbackModal(true);
      setCandidateAnswer('');
      resetTranscript();
    } catch (err) {
      setErrorMessage(err.message || 'Error evaluating answer.');
      if (err.message?.includes('focus violation') || err.message?.includes('tabs') || err.message?.includes('violat')) {
        setIsTerminated(true);
        setTerminationType('TERMINATED_FOCUS_VIOLATION');
      } else if (err.message?.includes('expired') || err.message?.includes('closed')) {
        setIsTerminated(true);
        setTerminationType('TIME_EXPIRED');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleProceedNext = () => {
    setShowFeedbackModal(false);
    setQuestionElapsedSeconds(0);
    if (evaluationFeedback?.termination_reason === 'TERMINATED_WEAK_ANSWERS' || 
        evaluationFeedback?.termination_reason === 'TIME_EXPIRED' ||
        evaluationFeedback?.termination_reason === 'TERMINATED_FOCUS_VIOLATION' ||
        evaluationFeedback?.is_completed || 
        !evaluationFeedback?.next_question) {
      onFinishInterview();
    } else {
      setCurrentQuestion(evaluationFeedback.next_question);
      setDifficultyHistory(prev => [...prev, evaluationFeedback.next_question.difficulty]);
      setEvaluationFeedback(null);
    }
  };

  const currentDiff = currentQuestion?.difficulty || 'MEDIUM';
  const currentIndex = currentQuestion?.question_index || 1;
  const totalQuestions = currentQuestion?.total_questions || null;

  return (
    <div className="container" style={{ maxWidth: '980px', paddingTop: '28px', paddingBottom: '70px' }}>
      
      {/* Top Bar: Progress & Competency Tracker */}
      <div className="glass-panel" style={{ padding: '16px 24px', marginBottom: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px' }}>
          
          {/* Progress Counter */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'rgba(99, 102, 241, 0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#818cf8',
              fontWeight: 700
            }}>
              {currentIndex}
            </div>
            <div>
              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                {totalQuestions 
                  ? `Question ${currentIndex} of ${totalQuestions}` 
                  : (language === 'hi' ? `प्रश्न ${currentIndex} • गतिशील 20-मिनट सत्र` : `Question ${currentIndex} • Dynamic 20-Min Session`)}
              </div>
              <div style={{ fontWeight: 700, fontSize: '0.98rem' }}>
                {currentQuestion?.skill}
              </div>
            </div>
          </div>

          {/* Center/Right: Timer & Badges */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            
            {/* Per-Question Stopwatch Timer Badge */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: '8px',
              background: 'rgba(99, 102, 241, 0.12)',
              border: '1px solid rgba(99, 102, 241, 0.35)',
              color: '#818cf8',
              transition: 'all 0.3s ease'
            }}>
              <Hourglass size={16} />
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.64rem', textTransform: 'uppercase', letterSpacing: '0.04em', lineHeight: 1, opacity: 0.85 }}>
                  {language === 'hi' ? 'प्रश्न समय' : 'Question Time'}
                </span>
                <span style={{
                  fontFamily: 'monospace',
                  fontWeight: 800,
                  fontSize: '1.08rem',
                  lineHeight: 1.2
                }}>
                  {formatTimer(questionElapsedSeconds)}
                </span>
              </div>
            </div>

            {/* Authoritative 20-Minute Timer Badge */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '6px 14px',
              borderRadius: '8px',
              background: secondsLeft <= 30
                ? 'rgba(239, 68, 68, 0.22)'
                : secondsLeft <= 60
                ? 'rgba(251, 146, 60, 0.2)'
                : secondsLeft <= 300
                ? 'rgba(245, 158, 11, 0.16)'
                : 'rgba(6, 182, 212, 0.12)',
              border: secondsLeft <= 30
                ? '1px solid #ef4444'
                : secondsLeft <= 60
                ? '1px solid #fb923c'
                : secondsLeft <= 300
                ? '1px solid #f59e0b'
                : '1px solid #06b6d4',
              color: secondsLeft <= 30
                ? '#f87171'
                : secondsLeft <= 60
                ? '#fb923c'
                : secondsLeft <= 300
                ? '#fbbf24'
                : '#38bdf8',
              boxShadow: secondsLeft <= 30 ? '0 0 12px rgba(239, 68, 68, 0.4)' : 'none',
              transition: 'all 0.3s ease'
            }}>
              <Clock size={16} />
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.64rem', textTransform: 'uppercase', letterSpacing: '0.04em', lineHeight: 1, opacity: 0.85 }}>
                  {language === 'hi' ? 'समय शेष' : 'Time Remaining'}
                </span>
                <span style={{
                  fontFamily: 'monospace',
                  fontWeight: 800,
                  fontSize: '1.08rem',
                  lineHeight: 1.2
                }}>
                  {formatTimer(secondsLeft)}
                </span>
              </div>
            </div>

            {/* Difficulty Badge with dynamic coloring */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Difficulty:</span>
              <span className={`badge ${currentDiff === 'HARD' ? 'badge-hard' : currentDiff === 'EASY' ? 'badge-easy' : 'badge-medium'}`}
                style={{ fontSize: '0.85rem', padding: '5px 12px' }}>
                {currentDiff}
              </span>

              <span className="badge badge-cyan" style={{ fontSize: '0.78rem' }}>
                {language === 'hi' ? 'हिंदी (Hindi)' : 'English'}
              </span>

              {/* Resume Personalization Status Indicator */}
              {interviewSession?.resume_id ? (
                <span 
                  id="resume-personalization-badge"
                  className="badge badge-purple" 
                  style={{ fontSize: '0.78rem', display: 'flex', alignItems: 'center', gap: '5px' }}
                  title="Questions are personalized based on your uploaded resume projects and technical stack."
                >
                  <Sparkles size={12} />
                  {language === 'hi' ? 'बायोडाटा निजीकरण: सक्रिय' : 'Resume Personalization: Active'}
                </span>
              ) : (
                <span 
                  id="resume-personalization-badge"
                  className="badge" 
                  style={{ 
                    fontSize: '0.78rem', 
                    display: 'flex', 
                    alignItems: 'center', 
                    gap: '5px',
                    background: 'rgba(148, 163, 184, 0.1)',
                    border: '1px solid rgba(148, 163, 184, 0.3)',
                    color: '#94a3b8'
                  }}
                  title="Resume skipped. Standard role benchmark questions are being used."
                >
                  <FileText size={12} />
                  {language === 'hi' ? 'मानक भूमिका (निजीकरण अक्षम)' : 'Standard Benchmark (Personalization: Disabled)'}
                </span>
              )}

              {/* Focus Monitoring Active Indicator */}
              {!isTerminated && (
                <div 
                  id="focus-monitoring-indicator"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '5px 12px',
                    borderRadius: '8px',
                    background: 'rgba(16, 185, 129, 0.12)',
                    border: '1px solid rgba(16, 185, 129, 0.35)',
                    color: '#34d399',
                    fontSize: '0.76rem',
                    fontWeight: 600,
                    letterSpacing: '0.02em'
                  }}
                  title={language === 'hi' ? 'सक्रिय पृष्ठ फोकस निगरानी चालू है। टैब बदलने पर सत्र समाप्त हो जाएगा।' : 'Active tab monitoring is enabled. Leaving this page will end the session.'}
                >
                  <div style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#10b981',
                    boxShadow: '0 0 8px #10b981'
                  }} />
                  <span>{language === 'hi' ? 'फोकस निगरानी सक्रिय' : 'Focus monitoring active'}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Competencies Progress Tracker */}
        <div style={{ display: 'flex', gap: '8px', marginTop: '16px', overflowX: 'auto', paddingBottom: '4px' }}>
          {SKILLS_LIST.map((skillName) => {
            const isCurrent = currentQuestion?.skill === skillName;
            return (
              <div 
                key={skillName}
                style={{
                  flex: 1,
                  padding: '8px 10px',
                  borderRadius: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 600,
                  whiteSpace: 'nowrap',
                  background: isCurrent ? 'rgba(99, 102, 241, 0.22)' : 'rgba(255, 255, 255, 0.03)',
                  color: isCurrent ? '#a5b4fc' : 'var(--text-dim)',
                  border: isCurrent ? '1px solid #6366f1' : '1px solid transparent',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                {isCurrent ? <Clock size={13} color="#a5b4fc" /> : <Layers size={13} />}
                {skillName}
              </div>
            );
          })}
        </div>

        {/* Elapsed Session Progress Bar (Authoritative 20-Minute Timeline) */}
        <div style={{ marginTop: '14px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-dim)', marginBottom: '5px' }}>
            <span>{language === 'hi' ? `सत्र प्रगति: ${currentIndex - 1} उत्तर पूर्ण` : `Session Progress: ${currentIndex - 1} answered`}</span>
            <span>{language === 'hi' ? `बीता समय: ${Math.min(100, Math.round(((1200 - secondsLeft) / 1200) * 100))}%` : `Elapsed: ${Math.min(100, Math.round(((1200 - secondsLeft) / 1200) * 100))}%`}</span>
          </div>
          <div style={{ width: '100%', height: '5px', background: 'rgba(255, 255, 255, 0.08)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{
              width: `${Math.min(100, Math.max(0, ((1200 - secondsLeft) / 1200) * 100))}%`,
              height: '100%',
              background: secondsLeft <= 60 
                ? 'linear-gradient(90deg, #f59e0b, #ef4444)' 
                : 'linear-gradient(90deg, #6366f1, #06b6d4)',
              transition: 'width 1s linear'
            }} />
          </div>
        </div>
      </div>

      {/* ======================================================== */}
      {/* 20-MINUTE TIMER WARNING BANNERS (Active Interview Only)  */}
      {/* ======================================================== */}
      {!isTerminated && secondsLeft <= 30 && secondsLeft > 0 && (
        <div style={{
          padding: '12px 18px',
          background: 'rgba(239, 68, 68, 0.2)',
          border: '1px solid #ef4444',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#f87171',
          fontSize: '0.92rem',
          fontWeight: 700,
          boxShadow: '0 0 16px rgba(239, 68, 68, 0.35)'
        }}>
          <AlertTriangle size={20} color="#ef4444" />
          <span>
            {language === 'hi' 
              ? '⚠️ अत्यंत महत्वपूर्ण: केवल 30 सेकंड शेष हैं! साक्षात्कार समाप्त होने से पहले कृपया तुरंत अपना उत्तर सबमिट करें।'
              : '⚠️ Urgent Warning: Less than 30 seconds remaining! Please submit your response immediately before the 20-minute session closes.'}
          </span>
        </div>
      )}

      {!isTerminated && secondsLeft <= 60 && secondsLeft > 30 && (
        <div style={{
          padding: '12px 18px',
          background: 'rgba(251, 146, 60, 0.16)',
          border: '1px solid #fb923c',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#fb923c',
          fontSize: '0.9rem',
          fontWeight: 600
        }}>
          <Clock size={18} color="#fb923c" />
          <span>
            {language === 'hi'
              ? '⏱️ चेतावनी: साक्षात्कार स्वतः समाप्त होने में 1 मिनट शेष है।'
              : '⏱️ Warning: 1 minute remaining before the interview closes automatically.'}
          </span>
        </div>
      )}

      {!isTerminated && secondsLeft <= 300 && secondsLeft > 60 && (
        <div style={{
          padding: '10px 18px',
          background: 'rgba(245, 158, 11, 0.12)',
          border: '1px solid #f59e0b',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '20px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          color: '#fbbf24',
          fontSize: '0.88rem',
          fontWeight: 600
        }}>
          <Hourglass size={18} color="#f59e0b" />
          <span>
            {language === 'hi'
              ? '⏳ सूचना: इस 20 मिनट के साक्षात्कार सत्र में 5 मिनट शेष हैं।'
              : '⏳ Notice: 5 minutes remaining in this 20-minute interview session.'}
          </span>
        </div>
      )}

      {/* Discreet progress indicator when consecutive weak answers > 0 (Neutral, non-discouraging) */}
      {!isTerminated && consecutiveWeakCount > 0 && (
        <div style={{
          padding: '8px 14px',
          background: 'rgba(255, 255, 255, 0.03)',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          borderRadius: '6px',
          marginBottom: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '0.82rem',
          color: 'var(--text-muted)'
        }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#818cf8' }} />
          <span>
            {language === 'hi' 
              ? 'सत्र प्रगति: गतिशील स्तर अनुकूलन सक्रिय है।' 
              : 'Interview Progress: Dynamic competency calibration active.'}
          </span>
        </div>
      )}

      {/* ======================================================== */}
      {/* INTERVIEW TERMINATION SCREEN VS ACTIVE QUESTION/ANSWER   */}
      {/* ======================================================== */}
      {isTerminated ? (
        <div className="glass-panel" style={{
          padding: '48px 36px',
          textAlign: 'center',
          border: terminationType === 'TERMINATED_FOCUS_VIOLATION'
            ? '1px solid rgba(239, 68, 68, 0.6)'
            : terminationType === 'TIME_EXPIRED'
            ? '1px solid rgba(245, 158, 11, 0.5)'
            : terminationType === 'TERMINATED_WEAK_ANSWERS'
            ? '1px solid rgba(168, 85, 247, 0.5)'
            : '1px solid rgba(16, 185, 129, 0.5)',
          background: 'rgba(15, 23, 42, 0.85)',
          boxShadow: terminationType === 'TERMINATED_FOCUS_VIOLATION'
            ? '0 20px 40px rgba(239, 68, 68, 0.15)'
            : '0 20px 40px rgba(0, 0, 0, 0.6)',
          marginBottom: '28px'
        }}>
          {/* Status Icon */}
          <div style={{
            width: '72px',
            height: '72px',
            borderRadius: '50%',
            background: terminationType === 'TERMINATED_FOCUS_VIOLATION'
              ? 'rgba(239, 68, 68, 0.15)'
              : terminationType === 'TIME_EXPIRED'
              ? 'rgba(245, 158, 11, 0.15)'
              : terminationType === 'TERMINATED_WEAK_ANSWERS'
              ? 'rgba(168, 85, 247, 0.15)'
              : 'rgba(16, 185, 129, 0.15)',
            border: terminationType === 'TERMINATED_FOCUS_VIOLATION'
              ? '2px solid #ef4444'
              : terminationType === 'TIME_EXPIRED'
              ? '2px solid #f59e0b'
              : terminationType === 'TERMINATED_WEAK_ANSWERS'
              ? '2px solid #a855f7'
              : '2px solid #10b981',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 20px',
            color: terminationType === 'TERMINATED_FOCUS_VIOLATION'
              ? '#f87171'
              : terminationType === 'TIME_EXPIRED'
              ? '#fbbf24'
              : terminationType === 'TERMINATED_WEAK_ANSWERS'
              ? '#c084fc'
              : '#34d399'
          }}>
            {terminationType === 'TERMINATED_FOCUS_VIOLATION' ? (
              <ShieldAlert size={38} />
            ) : terminationType === 'TIME_EXPIRED' ? (
              <Clock size={38} />
            ) : terminationType === 'TERMINATED_WEAK_ANSWERS' ? (
              <ShieldAlert size={38} />
            ) : (
              <CheckCircle2 size={38} />
            )}
          </div>

          <div style={{ marginBottom: '14px' }}>
            <span className={`badge ${
              terminationType === 'TERMINATED_FOCUS_VIOLATION'
                ? 'badge-hard'
                : terminationType === 'TIME_EXPIRED'
                ? 'badge-medium'
                : terminationType === 'TERMINATED_WEAK_ANSWERS'
                ? 'badge-purple'
                : 'badge-easy'
            }`} style={{ padding: '6px 14px', fontSize: '0.86rem' }}>
              {terminationType === 'TERMINATED_FOCUS_VIOLATION'
                ? 'TERMINATED_FOCUS_VIOLATION'
                : terminationType === 'TIME_EXPIRED' 
                ? 'TIME_EXPIRED' 
                : terminationType === 'TERMINATED_WEAK_ANSWERS' 
                ? 'TERMINATED_WEAK_ANSWERS' 
                : 'COMPLETED'}
            </span>
          </div>

          <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '16px', color: '#fff' }}>
            {terminationType === 'TERMINATED_FOCUS_VIOLATION' ? (
              language === 'hi' ? 'साक्षात्कार समाप्त: साक्षात्कार पृष्ठ से ध्यान हटा' : 'Interview Terminated: Focus Lost'
            ) : terminationType === 'TIME_EXPIRED' ? (
              language === 'hi' ? '20 मिनट की समय सीमा समाप्त' : '20-Minute Time Limit Reached'
            ) : terminationType === 'TERMINATED_WEAK_ANSWERS' ? (
              language === 'hi' ? 'साक्षात्कार समाप्त' : 'Interview Concluded'
            ) : (
              language === 'hi' ? 'साक्षात्कार संपन्न' : 'Interview Completed'
            )}
          </h2>

          {/* Exact prompt messages verbatim */}
          <div style={{
            maxWidth: '680px',
            margin: '0 auto 20px',
            padding: '20px 26px',
            borderRadius: '10px',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--bg-card-border)',
            fontSize: '1.04rem',
            lineHeight: 1.6,
            color: '#e2e8f0'
          }}>
            {terminationType === 'TERMINATED_FOCUS_VIOLATION' ? (
              <div>
                <div style={{ fontSize: '1.16rem', fontWeight: 700, color: '#f87171', marginBottom: '8px' }}>
                  {language === 'hi'
                    ? 'साक्षात्कार समाप्त: साक्षात्कार पृष्ठ से ध्यान हटा।'
                    : 'Interview terminated: interview page lost focus.'}
                </div>
                <p style={{ margin: 0, fontSize: '0.94rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                  {language === 'hi'
                    ? 'साक्षात्कार सत्र के दौरान टैब बदलने, ब्राउज़र मिनिमाइज़ करने या किसी अन्य ऐप पर जाने के कारण एंटी-चीटिंग नीति के तहत यह साक्षात्कार समाप्त कर दिया गया है। आपके द्वारा पहले दिए गए सभी उत्तर और मूल्यांकन सुरक्षित हैं।'
                    : 'This interview was automatically ended in accordance with the anti-cheating policy because the interview page became hidden or lost focus (tab switch, window minimized, or application switch). All previously completed answers, evaluations, and scores have been preserved.'}
                </p>
              </div>
            ) : terminationType === 'TIME_EXPIRED' ? (
              language === 'hi' ? (
                "आपका 20 मिनट का साक्षात्कार समय समाप्त हो गया है। आपका साक्षात्कार अब बंद हो गया है। आप अपनी साक्षात्कार रिपोर्ट देख सकते हैं।"
              ) : (
                "Your 20-minute interview time has ended. Your interview is now closed. You can view your interview report."
              )
            ) : terminationType === 'TERMINATED_WEAK_ANSWERS' ? (
              language === 'hi' ? (
                "आपका साक्षात्कार समाप्त हो गया है क्योंकि लगातार 7 उत्तर 40/100 के आवश्यक थ्रेशोल्ड से नीचे रहे। आपके उत्तर सुरक्षित कर लिए गए हैं, और आपकी साक्षात्कार रिपोर्ट उपलब्ध है।"
              ) : (
                "Your interview has ended because 7 consecutive answers scored below the required threshold of 40/100. Your responses have been saved, and your interview report is available."
              )
            ) : (
              language === 'hi' ? (
                "आपका साक्षात्कार पूरा हो गया है। सभी उत्तरों का मूल्यांकन कर लिया गया है।"
              ) : (
                "Your interview is complete. All responses have been evaluated."
              )
            )}
          </div>

          {/* Recorded Termination Timestamp */}
          {terminationTimestamp && (
            <div style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 18px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--bg-card-border)',
              borderRadius: '6px',
              fontSize: '0.86rem',
              color: '#94a3b8',
              marginBottom: '24px'
            }}>
              <Clock size={15} color="#94a3b8" />
              <span>
                {language === 'hi' ? 'दर्ज समाप्ति समय: ' : 'Recorded Termination Time: '}
                <strong style={{ color: '#f1f5f9' }}>
                  {new Date(terminationTimestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                </strong>
              </span>
            </div>
          )}

          {/* Network Failure / Retry Alert */}
          {violationNetworkError && (
            <div style={{
              maxWidth: '680px',
              margin: '0 auto 20px',
              padding: '12px 18px',
              background: 'rgba(239, 68, 68, 0.14)',
              border: '1px solid #ef4444',
              borderRadius: '8px',
              color: '#fca5a5',
              fontSize: '0.88rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '12px'
            }}>
              <span>{violationNetworkError}</span>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleRetryViolation}
                disabled={isRetryingViolation}
                style={{ padding: '6px 14px', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <RotateCcw size={14} />
                {isRetryingViolation ? (language === 'hi' ? 'पुनः प्रयास...' : 'Retrying...') : (language === 'hi' ? 'पुनः प्रयास करें' : 'Retry')}
              </button>
            </div>
          )}

          {/* Safeguard Indicators */}
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            gap: '24px',
            flexWrap: 'wrap',
            marginBottom: '32px',
            fontSize: '0.86rem',
            color: 'var(--text-muted)'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} color="#34d399" />
              <span>All completed answers and scores saved</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <CheckCircle2 size={16} color="#34d399" />
              <span>Verbatim evidence preserved</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <Lock size={16} color="#818cf8" />
              <span>Submission controls locked</span>
            </div>
          </div>

          {/* View Report Button */}
          <div>
            <button 
              type="button" 
              className="btn btn-primary btn-lg"
              onClick={onFinishInterview}
              style={{ padding: '14px 40px', fontSize: '1.05rem' }}
            >
              <FileText size={18} />
              {language === 'hi' ? 'साक्षात्कार रिपोर्ट देखें' : 'View Interview Report'}
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      ) : (
        <>
          {/* Center Stage: AI Interviewer & Question Card */}
          <div className="glass-panel" style={{ padding: '32px', marginBottom: '24px', borderLeft: '4px solid #6366f1' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '16px', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <div style={{
                  width: '44px',
                  height: '44px',
                  borderRadius: '12px',
                  background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  boxShadow: '0 4px 14px rgba(79, 70, 229, 0.3)'
                }}>
                  <Bot size={24} />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: '#fff' }}>
                    IntervueAI Interviewer
                  </div>
                  <div style={{ fontSize: '0.78rem', color: '#38bdf8' }}>
                    Assessing {currentQuestion?.skill} • {currentDiff} Tier
                  </div>
                </div>
              </div>

              {/* Audio TTS Button */}
              <button 
                type="button" 
                className={`btn btn-secondary btn-sm ${isSpeaking ? 'pulse-glow' : ''}`}
                onClick={handleSpeakToggle}
                title="Read Question Aloud"
              >
                {isSpeaking ? (
                  <>
                    <VolumeX size={15} color="#f43f5e" /> Stop Audio
                  </>
                ) : (
                  <>
                    <Volume2 size={15} color="#38bdf8" /> 🔊 Listen to Question
                  </>
                )}
              </button>
            </div>

            {/* Question Text */}
            <div style={{ 
              fontSize: '1.28rem', 
              fontWeight: 600, 
              lineHeight: 1.5, 
              color: '#f8fafc',
              padding: '12px 0'
            }}>
              {currentQuestion?.question_text}
            </div>
          </div>

          {/* Answer Area */}
          <div className="glass-panel" style={{ padding: '28px' }}>
            
            {/* Answer Header & Mode indicator */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontWeight: 700, fontSize: '0.96rem' }}>Your Answer:</span>
                {interview_mode === 'voice' && (
                  <span className="badge badge-purple" style={{ fontSize: '0.75rem' }}>
                    <Mic size={12} /> Voice Mode Active
                  </span>
                )}
              </div>

              {/* Interactive Demo Fill Buttons for Judges */}
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)' }}>Demo Quick-Fill:</span>
                <button 
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => fillSampleAnswer('strong')}
                  title="Fills a high-quality answer to demonstrate difficulty increase"
                >
                  💡 Strong Answer (Score &gt;75)
                </button>
                <button 
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => fillSampleAnswer('average')}
                  title="Fills an average answer to maintain difficulty"
                >
                  📝 Average Answer
                </button>
                <button 
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => fillSampleAnswer('weak')}
                  title="Fills a weak answer to demonstrate difficulty decrease"
                >
                  ⚠️ Weak Answer (Score &lt;40)
                </button>
              </div>
            </div>

            {/* Voice Input Control (If Voice Mode) */}
            {interview_mode === 'voice' && (
              <div style={{
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--bg-card-border)',
                borderRadius: 'var(--radius-sm)',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '12px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <button 
                    type="button"
                    className={`btn ${isListening ? 'btn-danger pulse-recording' : 'btn-success'}`}
                    onClick={handleMicToggle}
                  >
                    {isListening ? (
                      <>
                        <Square size={16} /> Stop Recording
                      </>
                    ) : (
                      <>
                        <Mic size={16} /> Start Speaking
                      </>
                    )}
                  </button>
                  
                  <div style={{ fontSize: '0.85rem', color: isListening ? '#34d399' : 'var(--text-muted)' }}>
                    {isListening ? '🎙️ Listening... Speak your technical explanation in English or Hindi.' : 'Click to speak or edit transcript below.'}
                  </div>
                </div>

                {speechError && (
                  <div style={{ fontSize: '0.8rem', color: '#fca5a5' }}>
                    {speechError}
                  </div>
                )}
              </div>
            )}

            {/* Text Area */}
            <textarea 
              rows={6}
              value={candidateAnswer}
              onChange={(e) => setCandidateAnswer(e.target.value)}
              placeholder={language === 'hi' 
                ? "अपना उत्तर यहाँ टाइप करें या ऊपर माइक्रोफोन से बोलें..." 
                : "Type your answer here or record using microphone above..."}
              style={{
                width: '100%',
                padding: '16px',
                background: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid var(--bg-card-border)',
                borderRadius: 'var(--radius-sm)',
                color: '#fff',
                fontFamily: 'inherit',
                fontSize: '1rem',
                lineHeight: 1.6,
                resize: 'vertical',
                marginBottom: '14px'
              }}
            />

            {errorMessage && (
              <div style={{ 
                padding: '10px 14px', 
                background: 'rgba(244, 63, 94, 0.1)', 
                border: '1px solid rgba(244, 63, 94, 0.3)',
                borderRadius: '6px',
                color: '#fca5a5',
                fontSize: '0.85rem',
                marginBottom: '14px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <AlertCircle size={16} />
                {errorMessage}
              </div>
            )}

            {/* Submit Button */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                Word count: {candidateAnswer.trim() ? candidateAnswer.trim().split(/\s+/).length : 0}
              </span>

              <button 
                type="button"
                className="btn btn-primary btn-lg"
                onClick={handleSubmit}
                disabled={isSubmitting || !candidateAnswer.trim()}
                style={{ opacity: candidateAnswer.trim() ? 1 : 0.6 }}
              >
                {isSubmitting ? 'Evaluating with Evidence...' : (
                  <>
                    Submit Answer
                    <Send size={18} />
                  </>
                )}
              </button>
            </div>

          </div>
        </>
      )}

      {/* ======================================================== */}
      {/* SECTION 7, 8, & 5: LIVE ADAPTIVE EVALUATION MODAL */}
      {/* ======================================================== */}
      {showFeedbackModal && evaluationFeedback && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 100,
          padding: '20px'
        }}>
          <div className="glass-panel" style={{ 
            maxWidth: '680px', 
            width: '100%', 
            padding: '32px', 
            border: '1px solid rgba(99, 102, 241, 0.35)',
            boxShadow: '0 20px 50px rgba(0, 0, 0, 0.7)'
          }}>
            
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
                  <span className="badge badge-cyan">
                    AI Competency Evaluation
                  </span>
                  {evaluationFeedback.evaluator?.includes('gemini') ? (
                    <span className="badge badge-purple" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                      <Sparkles size={11} /> Gemini 2.5 Flash
                    </span>
                  ) : (
                    <span className="badge" style={{ background: 'rgba(255, 255, 255, 0.08)', color: 'var(--text-muted)' }}>
                      Rubric Engine
                    </span>
                  )}
                </div>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800 }}>
                  {evaluationFeedback.skill}
                </h3>
              </div>

              {/* Score Dial */}
              <div style={{
                background: 'rgba(99, 102, 241, 0.15)',
                border: '1px solid #6366f1',
                borderRadius: '12px',
                padding: '10px 18px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '1.6rem', fontWeight: 800, color: '#a5b4fc', lineHeight: 1 }}>
                  {evaluationFeedback.score}
                </div>
                <div style={{ fontSize: '0.68rem', color: 'var(--text-dim)', marginTop: '4px' }}>
                  OUT OF 100
                </div>
              </div>
            </div>

            {/* Evidence Callout (Core Hackathon Feature) */}
            <div style={{
              padding: '16px 20px',
              background: 'rgba(16, 185, 129, 0.08)',
              borderLeft: '4px solid #10b981',
              borderRadius: '8px',
              marginBottom: '16px'
            }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 700, color: '#34d399', textTransform: 'uppercase', marginBottom: '4px' }}>
                Verbatim Evidence from Candidate Answer:
              </div>
              <div style={{ fontSize: '0.92rem', color: '#e2e8f0', fontStyle: 'italic', lineHeight: 1.5 }}>
                {evaluationFeedback.evidence}
              </div>
            </div>

            {/* Evaluator Rationale */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '4px' }}>
                Evaluator Rationale:
              </div>
              <div style={{ fontSize: '0.9rem', color: '#cbd5e1', lineHeight: 1.5 }}>
                {evaluationFeedback.reason}
              </div>
            </div>

            {/* AI Analytical Insight (from Gemini) */}
            {evaluationFeedback.ai_insight && (
              <div style={{
                padding: '10px 14px',
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: '6px',
                marginBottom: '14px',
                fontSize: '0.86rem',
                color: '#c7d2fe',
                lineHeight: 1.4
              }}>
                <strong style={{ color: '#a5b4fc' }}>💡 AI Insight:</strong> {evaluationFeedback.ai_insight}
              </div>
            )}

            {/* Dynamic Follow-Up Question (from Gemini) */}
            {evaluationFeedback.contextual_follow_up && (
              <div style={{
                padding: '10px 14px',
                background: 'rgba(6, 182, 212, 0.08)',
                border: '1px solid rgba(6, 182, 212, 0.25)',
                borderRadius: '6px',
                marginBottom: '14px',
                fontSize: '0.86rem',
                color: '#bae6fd',
                lineHeight: 1.4
              }}>
                <strong style={{ color: '#38bdf8' }}>🎯 Adaptive Follow-Up Suggested:</strong> "{evaluationFeedback.contextual_follow_up}"
              </div>
            )}

            {/* Termination Alert inside Modal (if interview terminated on this turn) */}
            {evaluationFeedback?.termination_reason ? (
              <div style={{
                padding: '16px 20px',
                borderRadius: '8px',
                background: evaluationFeedback.termination_reason === 'TIME_EXPIRED'
                  ? 'rgba(245, 158, 11, 0.12)'
                  : 'rgba(168, 85, 247, 0.12)',
                border: evaluationFeedback.termination_reason === 'TIME_EXPIRED'
                  ? '1px solid #f59e0b'
                  : '1px solid #a855f7',
                marginBottom: '20px',
                color: '#fff',
                fontSize: '0.94rem',
                lineHeight: 1.55
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 700, marginBottom: '6px', color: evaluationFeedback.termination_reason === 'TIME_EXPIRED' ? '#fbbf24' : '#c084fc' }}>
                  {evaluationFeedback.termination_reason === 'TIME_EXPIRED' ? <Clock size={16} /> : <AlertTriangle size={16} />}
                  <span>
                    {evaluationFeedback.termination_reason === 'TIME_EXPIRED'
                      ? (language === 'hi' ? 'समय सीमा समाप्त (20 मिनट)' : '20-Minute Time Limit Reached')
                      : (language === 'hi' ? 'साक्षात्कार समाप्त (7 उत्तर 40/100 से कम)' : 'Interview Terminated (7 Consecutive Weak Answers <40/100)')}
                  </span>
                </div>
                <div>
                  {evaluationFeedback.termination_reason === 'TIME_EXPIRED' ? (
                    language === 'hi' 
                      ? "आपका 20 मिनट का साक्षात्कार समय समाप्त हो गया है। आपका साक्षात्कार अब बंद हो गया है। आप अपनी साक्षात्कार रिपोर्ट देख सकते हैं।"
                      : "Your 20-minute interview time has ended. Your interview is now closed. You can view your interview report."
                  ) : (
                    language === 'hi'
                      ? "आपका साक्षात्कार समाप्त हो गया है क्योंकि लगातार 7 उत्तर 40/100 के आवश्यक थ्रेशोल्ड से नीचे रहे। आपके उत्तर सुरक्षित कर लिए गए हैं, और आपकी साक्षात्कार रिपोर्ट उपलब्ध है।"
                      : "Your interview has ended because 7 consecutive answers scored below the required threshold of 40/100. Your responses have been saved, and your interview report is available."
                  )}
                </div>
              </div>
            ) : (
              /* Adaptive Next Step Callout (only when continuing) */
              <div style={{
                padding: '14px 18px',
                background: 'rgba(99, 102, 241, 0.1)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: '8px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '24px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  {evaluationFeedback.next_difficulty === 'HARD' ? (
                    <TrendingUp size={20} color="#f43f5e" />
                  ) : evaluationFeedback.next_difficulty === 'EASY' ? (
                    <TrendingDown size={20} color="#10b981" />
                  ) : (
                    <Minus size={20} color="#f59e0b" />
                  )}
                  <div>
                    <div style={{ fontSize: '0.84rem', fontWeight: 700, color: '#fff' }}>
                      Adaptive Difficulty Transition
                    </div>
                    <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                      {evaluationFeedback.score > 70 
                        ? 'Strong performance: Next question scaled up to HARD'
                        : evaluationFeedback.score < 40
                        ? 'Supportive pacing: Next question adjusted to EASY'
                        : 'Consistent performance: Next question maintained at MEDIUM'}
                    </div>
                  </div>
                </div>

                <span className={`badge ${evaluationFeedback.next_difficulty === 'HARD' ? 'badge-hard' : evaluationFeedback.next_difficulty === 'EASY' ? 'badge-easy' : 'badge-medium'}`}>
                  Next: {evaluationFeedback.next_difficulty}
                </span>
              </div>
            )}

            {/* Proceed CTA */}
            <button 
              type="button" 
              className="btn btn-primary btn-lg" 
              onClick={handleProceedNext}
              style={{ width: '100%', justifyContent: 'center' }}
            >
              {(isTerminated || evaluationFeedback.termination_reason || evaluationFeedback.is_completed) ? (
                <>
                  {language === 'hi' ? 'साक्षात्कार रिपोर्ट देखें' : 'View Interview Report'}
                  <ArrowRight size={18} />
                </>
              ) : (
                <>
                  {language === 'hi' ? 'अगले प्रश्न पर आगे बढ़ें' : 'Proceed to Next Question'}
                  <ArrowRight size={18} />
                </>
              )}
            </button>

          </div>
        </div>
      )}

    </div>
  );
}
