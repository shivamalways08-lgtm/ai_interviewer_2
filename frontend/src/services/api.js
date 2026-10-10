/**
 * API Service for IntervueAI
 * Communicates with the FastAPI backend
 */

const BASE_URL = '/api';

export async function fetchRoles() {
  const res = await fetch(`${BASE_URL}/roles`);
  if (!res.ok) throw new Error('Failed to fetch job roles');
  return res.json();
}

export async function startInterviewSession(payload) {
  const res = await fetch(`${BASE_URL}/interview/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to start interview' }));
    throw new Error(err.detail || 'Failed to start interview');
  }
  return res.json();
}

export async function submitInterviewAnswer(payload) {
  const res = await fetch(`${BASE_URL}/interview/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to submit answer' }));
    throw new Error(err.detail || 'Failed to submit answer');
  }
  return res.json();
}

export async function completeInterviewSession(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/complete?interview_id=${interviewId}`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to complete interview');
  return res.json();
}

export async function expireInterviewSession(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/${interviewId}/expire`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to expire interview');
  return res.json();
}

export async function fetchInterviewState(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/${interviewId}`);
  if (!res.ok) throw new Error('Failed to fetch interview state');
  return res.json();
}

export async function fetchCandidateReport(interviewId) {
  const res = await fetch(`${BASE_URL}/report/${interviewId}`);
  if (!res.ok) throw new Error('Failed to fetch candidate report');
  return res.json();
}

export async function recordRecruiterDecision(payload) {
  const res = await fetch(`${BASE_URL}/recruiter/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to save decision' }));
    throw new Error(err.detail || 'Failed to save decision');
  }
  return res.json();
}

export async function fetchRecruiterCandidates() {
  const res = await fetch(`${BASE_URL}/recruiter/candidates`);
  if (!res.ok) throw new Error('Failed to fetch candidates');
  return res.json();
}

export async function seedDemoData() {
  const res = await fetch(`${BASE_URL}/demo/seed`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to seed demo candidates');
  return res.json();
}

export async function checkBackendHealth() {
  const res = await fetch(`${BASE_URL}/health`);
  if (!res.ok) throw new Error('Backend health check failed');
  return res.json();
}

export async function fetchAiSettings() {
  const res = await fetch(`${BASE_URL}/settings/ai`);
  if (!res.ok) throw new Error('Failed to fetch AI settings');
  return res.json();
}

export async function updateGeminiKey(apiKey) {
  const res = await fetch(`${BASE_URL}/settings/ai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gemini_api_key: apiKey })
  });
  if (!res.ok) throw new Error('Failed to update Gemini settings');
  return res.json();
}

export async function testGeminiKey(apiKey) {
  const res = await fetch(`${BASE_URL}/settings/test-key`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ gemini_api_key: apiKey })
  });
  if (!res.ok) throw new Error('Failed to test Gemini key');
  return res.json();
}

export async function recordConsentDecline(payload) {
  const res = await fetch(`${BASE_URL}/consent/decline`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to record consent decline' }));
    throw new Error(err.detail || 'Failed to record consent decline');
  }
  return res.json();
}

export async function fetchSessionConsent(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/${interviewId}/consent`);
  if (!res.ok) throw new Error('Failed to fetch session consent verification');
  return res.json();
}

export async function recordFocusViolation(interviewId, details = {}) {
  const maxRetries = 3;
  let lastError = null;

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      const res = await fetch(`${BASE_URL}/interview/${interviewId}/violation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          interview_id: interviewId,
          reason: 'TERMINATED_FOCUS_VIOLATION',
          details: details.details || 'Interview page lost focus (tab switch, window minimized, or navigated away).'
        })
      });
      if (res.ok) {
        return await res.json();
      }
      const err = await res.json().catch(() => ({ detail: 'Failed to record focus violation' }));
      throw new Error(err.detail || 'Failed to record focus violation');
    } catch (err) {
      lastError = err;
      if (attempt < maxRetries) {
        await new Promise(r => setTimeout(r, attempt * 500));
      }
    }
  }

  throw lastError || new Error('Failed to record focus violation after retries');
}

export async function uploadResumeFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${BASE_URL}/resume/upload`, {
    method: 'POST',
    body: formData
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to upload and analyze resume' }));
    throw new Error(err.detail || 'Failed to upload and analyze resume');
  }

  return res.json();
}

export async function fetchResume(resumeId) {
  const res = await fetch(`${BASE_URL}/resume/${resumeId}`);
  if (!res.ok) throw new Error('Failed to fetch resume information');
  return res.json();
}

export async function fetchInterviewHistory(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/${interviewId}/history`);
  if (!res.ok) throw new Error('Failed to fetch interview history');
  return res.json();
}

export async function fetchNextQuestion(interviewId) {
  const res = await fetch(`${BASE_URL}/interview/${interviewId}/next-question`, {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to fetch next question');
  return res.json();
}

