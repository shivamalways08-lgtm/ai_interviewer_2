import React from 'react';
import { 
  Sparkles, 
  ShieldCheck, 
  Users, 
  PlayCircle, 
  Languages, 
  CheckCircle2, 
  Bot,
  Zap,
  Cpu
} from 'lucide-react';

export default function Navbar({ 
  activeTab, 
  setActiveTab, 
  onQuickDemo,
  aiSettings,
  onOpenAiSettings
}) {
  const isGeminiActive = aiSettings?.provider === 'gemini';

  return (
    <nav className="navbar">
      <div className="container navbar-inner">
        {/* Brand */}
        <div 
          style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}
          onClick={() => setActiveTab('landing')}
        >
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '12px',
            background: 'linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#fff',
            boxShadow: '0 4px 14px rgba(79, 70, 229, 0.4)'
          }}>
            <Bot size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em' }}>
                Intervue<span style={{ color: '#6366f1' }}>AI</span>
              </span>
              <span className="badge badge-cyan" style={{ fontSize: '0.68rem', padding: '2px 7px' }}>
                Multilingual MVP
              </span>
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Fair interviews in English & हिंदी
            </div>
          </div>
        </div>

        {/* Navigation Items */}
        <div className="nav-links">
          <button 
            className={`nav-btn ${activeTab === 'landing' ? 'active' : ''}`}
            onClick={() => setActiveTab('landing')}
          >
            Home
          </button>
          
          <button 
            className={`nav-btn ${activeTab === 'setup' || activeTab === 'interview' ? 'active' : ''}`}
            onClick={() => setActiveTab('setup')}
          >
            <PlayCircle size={16} />
            Start Interview
          </button>

          <button 
            className={`nav-btn ${activeTab === 'recruiter' || activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('recruiter')}
          >
            <Users size={16} />
            Recruiter Dashboard
          </button>

          <button 
            className={`nav-btn ${activeTab === 'fairness' ? 'active' : ''}`}
            onClick={() => setActiveTab('fairness')}
          >
            <ShieldCheck size={16} />
            Fairness System
          </button>

          {/* AI Engine Status Button */}
          <button 
            type="button"
            className="btn btn-secondary btn-sm"
            onClick={onOpenAiSettings}
            style={{ 
              display: 'flex', 
              alignItems: 'center', 
              gap: '6px',
              padding: '6px 12px',
              border: isGeminiActive ? '1px solid rgba(99, 102, 241, 0.6)' : '1px solid var(--bg-card-border)',
              background: isGeminiActive ? 'rgba(99, 102, 241, 0.15)' : 'rgba(255, 255, 255, 0.04)'
            }}
            title={isGeminiActive ? "Google Gemini AI is active. Click to view settings." : "Click to connect Google Gemini API key or view settings."}
          >
            {isGeminiActive ? (
              <>
                <Zap size={14} color="#818cf8" />
                <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#c7d2fe' }}>
                  ⚡ Gemini Active
                </span>
              </>
            ) : (
              <>
                <Cpu size={14} color="#38bdf8" />
                <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                  AI: Offline Rubric
                </span>
              </>
            )}
          </button>

          {/* Quick Demo Button */}
          <button 
            className="btn btn-primary btn-sm"
            onClick={onQuickDemo}
            style={{ marginLeft: '4px' }}
            title="Instantly launch sample candidate or interactive demo"
          >
            <Sparkles size={15} />
            Try 1-Click Demo
          </button>
        </div>
      </div>
    </nav>
  );
}
