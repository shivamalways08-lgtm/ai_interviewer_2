import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Key, 
  CheckCircle2, 
  AlertCircle, 
  X, 
  ShieldCheck, 
  Zap, 
  ExternalLink,
  RefreshCw,
  Eye,
  EyeOff
} from 'lucide-react';
import { fetchAiSettings, updateGeminiKey, testGeminiKey } from '../services/api';

export default function AiSettingsModal({ isOpen, onClose, onSettingsUpdated }) {
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [saveResult, setSaveResult] = useState(null);
  const [settings, setSettings] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadSettings();
      setTestResult(null);
      setSaveResult(null);
    }
  }, [isOpen]);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await fetchAiSettings();
      setSettings(data);
    } catch (err) {
      console.error('Failed to load AI settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTestKey = async () => {
    if (!apiKey.trim()) {
      setTestResult({ valid: false, error: 'Please enter a Gemini API key to test.' });
      return;
    }
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testGeminiKey(apiKey.trim());
      setTestResult(res);
    } catch (err) {
      setTestResult({ valid: false, error: err.message || 'Verification failed.' });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveKey = async () => {
    if (!apiKey.trim()) {
      setSaveResult({ success: false, error: 'Please enter an API key.' });
      return;
    }
    setLoading(true);
    setSaveResult(null);
    try {
      const res = await updateGeminiKey(apiKey.trim());
      setSaveResult(res);
      if (res.success) {
        await loadSettings();
        setApiKey('');
        if (onSettingsUpdated) onSettingsUpdated(res);
      }
    } catch (err) {
      setSaveResult({ success: false, error: err.message || 'Failed to save key.' });
    } finally {
      setLoading(false);
    }
  };

  const handleResetToOffline = async () => {
    setLoading(true);
    try {
      const res = await updateGeminiKey('reset');
      setSaveResult(res);
      await loadSettings();
      setApiKey('');
      if (onSettingsUpdated) onSettingsUpdated(res);
    } catch (err) {
      setSaveResult({ success: false, error: err.message || 'Failed to reset settings.' });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  const isGeminiActive = settings?.provider === 'gemini';

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(5, 8, 16, 0.82)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 200,
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '580px',
        width: '100%',
        padding: '30px',
        position: 'relative',
        boxShadow: '0 24px 60px rgba(0, 0, 0, 0.8)',
        border: '1px solid rgba(99, 102, 241, 0.35)'
      }}>
        
        {/* Close Button */}
        <button 
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '20px',
            right: '20px',
            background: 'none',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer',
            padding: '4px'
          }}
          title="Close Modal"
        >
          <X size={20} />
        </button>

        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '20px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 16px rgba(79, 70, 229, 0.4)'
          }}>
            <Sparkles size={24} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 800, margin: 0 }}>
              AI Engine & Gemini Settings
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)', margin: '3px 0 0' }}>
              Connect Google Gemini for live adaptive evaluation & bilingual reasoning
            </p>
          </div>
        </div>

        {/* Current Active Status Card */}
        <div style={{
          padding: '16px 20px',
          background: isGeminiActive ? 'rgba(99, 102, 241, 0.12)' : 'rgba(255, 255, 255, 0.03)',
          border: isGeminiActive ? '1px solid rgba(99, 102, 241, 0.4)' : '1px solid var(--bg-card-border)',
          borderRadius: '10px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)', textTransform: 'uppercase', fontWeight: 700 }}>
                Active Evaluation Engine:
              </span>
            </div>
            <span className={`badge ${isGeminiActive ? 'badge-hard' : 'badge-cyan'}`} style={{ fontSize: '0.78rem' }}>
              {isGeminiActive ? '⚡ Gemini 2.5 Flash' : '🛡️ Deterministic Rubric'}
            </span>
          </div>
          <div style={{ fontSize: '0.88rem', color: '#e2e8f0', lineHeight: 1.4 }}>
            {settings?.status_message || 'Checking status...'}
          </div>
          {settings?.masked_key && (
            <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '6px' }}>
              Configured Key: <code style={{ color: '#818cf8', background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }}>{settings.masked_key}</code>
            </div>
          )}
        </div>

        {/* API Key Input Section */}
        <div style={{ marginBottom: '18px' }}>
          <label style={{ display: 'block', fontSize: '0.86rem', fontWeight: 600, marginBottom: '8px', color: '#f1f5f9' }}>
            Google Gemini API Key:
          </label>
          <div style={{ position: 'relative' }}>
            <input 
              type={showKey ? 'text' : 'password'}
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder="Paste your Gemini API key (e.g. AIzaSy...)"
              style={{
                width: '100%',
                padding: '12px 44px 12px 14px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--bg-card-border)',
                borderRadius: '8px',
                color: '#fff',
                fontSize: '0.92rem',
                fontFamily: showKey ? 'monospace' : 'inherit'
              }}
            />
            <button 
              type="button"
              onClick={() => setShowKey(!showKey)}
              style={{
                position: 'absolute',
                right: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                background: 'none',
                border: 'none',
                color: 'var(--text-dim)',
                cursor: 'pointer'
              }}
              title={showKey ? 'Hide key' : 'Show key'}
            >
              {showKey ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
        </div>

        {/* Feedback / Alerts */}
        {testResult && (
          <div style={{
            padding: '10px 14px',
            borderRadius: '6px',
            marginBottom: '14px',
            fontSize: '0.84rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: testResult.valid ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
            border: testResult.valid ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
            color: testResult.valid ? '#34d399' : '#fca5a5'
          }}>
            {testResult.valid ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
            {testResult.message || testResult.error}
          </div>
        )}

        {saveResult && (
          <div style={{
            padding: '10px 14px',
            borderRadius: '6px',
            marginBottom: '14px',
            fontSize: '0.84rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: saveResult.success ? 'rgba(16, 185, 129, 0.12)' : 'rgba(244, 63, 94, 0.12)',
            border: saveResult.success ? '1px solid rgba(16, 185, 129, 0.3)' : '1px solid rgba(244, 63, 94, 0.3)',
            color: saveResult.success ? '#34d399' : '#fca5a5'
          }}>
            {saveResult.success ? <CheckCircle2 size={16} /> : <AlertCircle size={16} />}
            {saveResult.message || saveResult.error}
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', marginBottom: '20px' }}>
          <button 
            type="button" 
            className="btn btn-secondary btn-sm"
            onClick={handleTestKey}
            disabled={testing || !apiKey.trim()}
            style={{ flex: 1, minWidth: '120px' }}
          >
            {testing ? 'Testing...' : 'Test Connection'}
          </button>

          <button 
            type="button" 
            className="btn btn-primary btn-sm"
            onClick={handleSaveKey}
            disabled={loading || !apiKey.trim()}
            style={{ flex: 1, minWidth: '140px' }}
          >
            {loading ? 'Saving...' : 'Save & Activate'}
          </button>

          {isGeminiActive && (
            <button 
              type="button" 
              className="btn btn-danger btn-sm"
              onClick={handleResetToOffline}
              disabled={loading}
              title="Switch back to offline rubric mode without API key"
            >
              Reset to Offline
            </button>
          )}
        </div>

        {/* Free API Key Guide Note */}
        <div style={{
          padding: '12px 16px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--bg-card-border)',
          borderRadius: '8px',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
          display: 'flex',
          flexDirection: 'column',
          gap: '6px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <span style={{ fontWeight: 700, color: '#93c5fd' }}>
              💡 Don't have a Gemini key?
            </span>
            <a 
              href="https://aistudio.google.com/app/apikey" 
              target="_blank" 
              rel="noreferrer"
              style={{ color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none', fontWeight: 600 }}
            >
              Get Free Key at Google AI Studio <ExternalLink size={12} />
            </a>
          </div>
          <div>
            • IntervueAI uses <strong>gemini-2.5-flash</strong> for zero-latency multilingual scoring.
          </div>
          <div>
            • Offline Fallback: If no key is entered, the app continues running with our deterministic rubric engine.
          </div>
        </div>

      </div>
    </div>
  );
}
