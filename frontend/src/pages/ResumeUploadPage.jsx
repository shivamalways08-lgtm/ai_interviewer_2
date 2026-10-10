import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  X, 
  ArrowRight, 
  SkipForward, 
  Sparkles, 
  Code, 
  FolderGit2, 
  Briefcase, 
  Check, 
  RefreshCw,
  Layers,
  Wrench
} from 'lucide-react';
import { uploadResumeFile } from '../services/api';

export default function ResumeUploadPage({ 
  candidateConfig, 
  onContinueWithResume, 
  onSkipResume, 
  onBackToConsent 
}) {
  const language = candidateConfig?.language || 'en';
  const isHi = language === 'hi';

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState('');
  const [analyzedData, setAnalyzedData] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [confirmed, setConfirmed] = useState(true);

  const fileInputRef = useRef(null);

  // Validate and handle file
  const handleFileProcess = async (file) => {
    if (!file) return;

    setErrorMessage(null);
    setAnalyzedData(null);

    const validExtensions = ['.pdf', '.docx'];
    const fileName = file.name.toLowerCase();
    const isValidExt = validExtensions.some(ext => fileName.endsWith(ext));

    if (!isValidExt) {
      setErrorMessage(
        isHi 
          ? 'अमान्य फ़ाइल प्रकार। केवल PDF और DOCX फ़ाइलें समर्थित हैं।' 
          : 'Invalid file format. Only PDF and DOCX files are supported.'
      );
      return;
    }

    const maxSize = 5 * 1024 * 1024; // 5 MB
    if (file.size > maxSize) {
      setErrorMessage(
        isHi 
          ? 'फ़ाइल का आकार 5MB की अधिकतम सीमा से अधिक है।' 
          : 'File exceeds maximum allowed size of 5MB.'
      );
      return;
    }

    if (file.size === 0) {
      setErrorMessage(
        isHi 
          ? 'अपलोड की गई फ़ाइल खाली है। कृपया एक मान्य बायोडाटा अपलोड करें।' 
          : 'The uploaded file is empty. Please upload a valid resume.'
      );
      return;
    }

    setSelectedFile(file);
    setIsAnalyzing(true);
    setUploadProgress(20);
    setAnalysisStage(isHi ? 'बायोडाटा अपलोड और टेक्स्ट निष्कर्षण हो रहा है...' : 'Uploading file & extracting document text...');

    try {
      // Simulate stepped progress during server roundtrip
      const pTimer = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 85) {
            clearInterval(pTimer);
            return 85;
          }
          if (prev === 40) {
            setAnalysisStage(isHi ? 'कौशल, उपकरण और प्रोजेक्ट्स का विश्लेषण जारी है...' : 'Analyzing technical skills, tools & project stacks...');
          } else if (prev === 70) {
            setAnalysisStage(isHi ? 'व्यक्तिगत इंटरव्यू प्रश्नों के लिए प्रोफ़ाइल तैयार हो रही है...' : 'Synthesizing personalized interview topics...');
          }
          return prev + 15;
        });
      }, 250);

      const result = await uploadResumeFile(file);
      clearInterval(pTimer);
      setUploadProgress(100);
      setAnalyzedData(result);
      setIsAnalyzing(false);
    } catch (err) {
      setIsAnalyzing(false);
      setUploadProgress(0);
      setSelectedFile(null);
      setErrorMessage(err.message || (isHi ? 'बायोडाटा विश्लेषण में विफल रहा। कृपया पुनः प्रयास करें।' : 'Resume analysis failed. Please try again with a valid PDF/DOCX file.'));
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileProcess(e.dataTransfer.files[0]);
    }
  };

  const handleBrowseClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
      fileInputRef.current.click();
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileProcess(e.target.files[0]);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setAnalyzedData(null);
    setUploadProgress(0);
    setErrorMessage(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  return (
    <div className="container" style={{ maxWidth: '880px', paddingTop: '40px', paddingBottom: '80px' }}>
      
      {/* Header Badge & Title */}
      <div style={{ textAlign: 'center', marginBottom: '32px' }}>
        <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '10px' }}>
          <span className="badge badge-purple" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sparkles size={14} />
            {isHi ? 'चरण 3: बायोडाटा निजीकरण' : 'Step 3: Resume Personalization'}
          </span>
          <span className="badge badge-emerald">
            {isHi ? 'गोपनीयता सुरक्षित' : 'Privacy Protected'}
          </span>
        </div>
        
        <h2 style={{ fontSize: '2.3rem', fontWeight: 800, marginBottom: '10px' }}>
          {isHi ? (
            <>आइए आपका <span className="text-gradient">इंटरव्यू व्यक्तिगत</span> बनाएं</>
          ) : (
            <>Let's Personalize Your <span className="text-gradient">Interview</span></>
          )}
        </h2>
        <p style={{ color: 'var(--text-muted)', fontSize: '1.02rem', maxWidth: '640px', margin: '0 auto' }}>
          {isHi 
            ? 'अपना बायोडाटा (Resume) अपलोड करें ताकि हमारा AI आपके वास्तविक प्रोजेक्ट्स, तकनीकी कौशल और अनुभव के आधार पर सवाल पूछ सके।' 
            : 'Upload your resume so our AI can ask questions based on your skills, experience, and projects.'}
        </p>
      </div>

      {/* Main Glass Panel */}
      <div className="glass-panel" style={{ padding: '36px', display: 'flex', flexDirection: 'column', gap: '26px' }}>
        
        {/* Upload Zone (shown when no analyzed data yet) */}
        {!analyzedData && (
          <div>
            <input 
              ref={fileInputRef}
              type="file" 
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
              id="resume-file-input"
            />

            <div 
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={handleBrowseClick}
              style={{
                border: `2px dashed ${dragActive ? 'var(--primary-light)' : 'rgba(99, 102, 241, 0.35)'}`,
                borderRadius: 'var(--radius-md)',
                padding: '48px 24px',
                textAlign: 'center',
                background: dragActive ? 'rgba(99, 102, 241, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                cursor: 'pointer',
                transition: 'all 0.25s ease',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '14px'
              }}
            >
              <div style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.15)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--primary-light)'
              }}>
                <UploadCloud size={32} />
              </div>

              <div>
                <div style={{ fontSize: '1.15rem', fontWeight: 700, color: '#fff', marginBottom: '4px' }}>
                  {isHi ? 'यहाँ अपना बायोडाटा खींचें और छोड़ें (Drag & Drop)' : 'Drag and drop your resume here'}
                </div>
                <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                  {isHi ? 'या अपने कंप्यूटर से फ़ाइल चुनने के लिए क्लिक करें' : 'or click to browse from your device'}
                </div>
              </div>

              <button 
                type="button"
                className="btn btn-secondary"
                style={{ marginTop: '8px', padding: '10px 24px' }}
                onClick={(e) => {
                  e.stopPropagation();
                  handleBrowseClick();
                }}
              >
                <FileText size={16} />
                {isHi ? 'फ़ाइलें ब्राउज़ करें (Browse Files)' : 'Browse Files'}
              </button>

              <div style={{ fontSize: '0.82rem', color: 'var(--text-dim)', marginTop: '8px' }}>
                {isHi ? 'समर्थित प्रारूप: PDF, DOCX • अधिकतम आकार: 5 MB' : 'Accepted file types: PDF, DOCX • Maximum file size: 5 MB'}
              </div>
            </div>
          </div>
        )}

        {/* Selected File Card & Progress Indicator */}
        {selectedFile && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid var(--bg-card-border)',
            borderRadius: 'var(--radius-sm)',
            padding: '18px 22px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <div style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(99, 102, 241, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--primary-light)'
                }}>
                  <FileText size={22} />
                </div>
                <div>
                  <div style={{ fontWeight: 700, color: '#fff', fontSize: '0.98rem' }}>
                    {selectedFile.name}
                  </div>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                    {formatFileSize(selectedFile.size)} • {selectedFile.name.endsWith('.pdf') ? 'PDF Document' : 'DOCX Document'}
                  </div>
                </div>
              </div>

              {!isAnalyzing && (
                <button 
                  onClick={handleRemoveFile}
                  title={isHi ? 'फ़ाइल हटाएं या बदलें' : 'Remove or replace file'}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-dim)',
                    cursor: 'pointer',
                    padding: '6px',
                    borderRadius: '4px',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                >
                  <X size={18} />
                </button>
              )}
            </div>

            {/* Progress Bar & Status Text */}
            {isAnalyzing && (
              <div>
                <div style={{
                  width: '100%',
                  height: '6px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  borderRadius: '3px',
                  overflow: 'hidden',
                  marginBottom: '8px'
                }}>
                  <div style={{
                    width: `${uploadProgress}%`,
                    height: '100%',
                    background: 'linear-gradient(90deg, var(--primary) 0%, var(--accent-cyan) 100%)',
                    borderRadius: '3px',
                    transition: 'width 0.3s ease'
                  }} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <RefreshCw size={12} className="spin" />
                    {analysisStage}
                  </span>
                  <span>{uploadProgress}%</span>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Error Alert */}
        {errorMessage && (
          <div style={{
            background: 'rgba(244, 63, 94, 0.12)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            borderRadius: 'var(--radius-sm)',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            color: '#fda4af',
            fontSize: '0.92rem'
          }}>
            <AlertCircle size={20} style={{ flexShrink: 0 }} />
            <div style={{ flex: 1 }}>{errorMessage}</div>
            <button 
              onClick={() => setErrorMessage(null)}
              style={{ background: 'transparent', border: 'none', color: '#fda4af', cursor: 'pointer' }}
            >
              <X size={16} />
            </button>
          </div>
        )}

        {/* Resume Analysis Preview Section */}
        {analyzedData && (
          <div style={{
            background: 'rgba(16, 185, 129, 0.04)',
            border: '1px solid rgba(16, 185, 129, 0.25)',
            borderRadius: 'var(--radius-md)',
            padding: '24px',
            display: 'flex',
            flexDirection: 'column',
            gap: '22px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <CheckCircle size={22} color="var(--accent-emerald)" />
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fff', margin: 0 }}>
                  {isHi ? 'बायोडाटा विश्लेषण पूर्वावलोकन' : 'Resume Analysis Preview'}
                </h3>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span className={`badge ${analyzedData.is_fallback ? 'badge-medium' : 'badge-purple'}`} style={{ fontSize: '0.75rem' }}>
                  {analyzedData.is_fallback ? (isHi ? 'ऑफ़लाइन कीवर्ड विश्लेषक' : 'Offline Keyword Parser') : '⚡ Gemini AI Parser'}
                </span>
                <button
                  onClick={handleRemoveFile}
                  className="btn btn-secondary"
                  style={{ padding: '5px 12px', fontSize: '0.8rem' }}
                >
                  <RefreshCw size={12} />
                  {isHi ? 'दूसरी फ़ाइल अपलोड करें' : 'Change Resume'}
                </button>
              </div>
            </div>

            {/* AI vs Fallback Transparency Banner */}
            {analyzedData.is_fallback ? (
              <div style={{
                background: 'rgba(245, 158, 11, 0.08)',
                border: '1px solid rgba(245, 158, 11, 0.25)',
                borderRadius: 'var(--radius-sm)',
                padding: '12px 16px',
                fontSize: '0.84rem',
                color: '#fcd34d',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <AlertCircle size={18} style={{ flexShrink: 0 }} />
                <div>
                  <strong>{isHi ? 'ऑफ़लाइन कीवर्ड निष्कर्षण (सीमित मोड):' : 'Offline Keyword Extraction (Limited Fallback):'}</strong>{' '}
                  {isHi 
                    ? 'स्थानीय कीवर्ड मिलान द्वारा विश्लेषण किया गया। व्यापक AI विश्लेषण और गहन प्रोजेक्ट विवरण के लिए AI सेटिंग्स में जेमिनी की जोड़ें।'
                    : 'Extracted using local keyword matching without external LLM. Deeper semantic analysis and nuanced project role context require an active Gemini API key in AI Engine settings.'}
                </div>
              </div>
            ) : (
              <div style={{
                background: 'rgba(99, 102, 241, 0.08)',
                border: '1px solid rgba(99, 102, 241, 0.25)',
                borderRadius: 'var(--radius-sm)',
                padding: '12px 16px',
                fontSize: '0.84rem',
                color: '#c7d2fe',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                <Sparkles size={18} style={{ flexShrink: 0, color: '#818cf8' }} />
                <div>
                  <strong>{isHi ? 'Google Gemini AI विश्लेषण:' : 'Google Gemini AI Analysis Active:'}</strong>{' '}
                  {isHi
                    ? 'आपके बायोडाटा के वास्तविक प्रोजेक्ट्स, आर्किटेक्चर और तकनीकों का सुरक्षित विश्लेषण संपन्न हुआ।'
                    : 'Your technical skills, project architectures, and explicit responsibilities were extracted directly from your document for personalized questioning.'}
                </div>
              </div>
            )}

            {/* Profile Summary if provided */}
            {analyzedData.summary && (
              <div style={{
                background: 'rgba(255, 255, 255, 0.03)',
                padding: '12px 16px',
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.9rem',
                color: 'var(--text-main)',
                fontStyle: 'italic',
                borderLeft: '3px solid var(--accent-cyan)'
              }}>
                "{analyzedData.summary}"
              </div>
            )}

            {/* Categorized Skills Section */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '14px' }}>
              
              {/* Programming Languages & Frameworks */}
              {analyzedData.languages_frameworks && analyzedData.languages_frameworks.length > 0 && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px 16px'
                }}>
                  <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Code size={14} color="#818cf8" />
                    {isHi ? 'भाषाएं और फ्रेमवर्क:' : 'Languages & Frameworks:'}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {analyzedData.languages_frameworks.map((lf, idx) => (
                      <span key={idx} className="badge badge-purple" style={{ fontSize: '0.78rem', padding: '3px 10px' }}>
                        {lf}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Tools & Technologies */}
              {analyzedData.tools_technologies && analyzedData.tools_technologies.length > 0 && (
                <div style={{
                  background: 'rgba(255, 255, 255, 0.02)',
                  border: '1px solid var(--bg-card-border)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '14px 16px'
                }}>
                  <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Wrench size={14} color="#06b6d4" />
                    {isHi ? 'उपकरण और डेटाबेस:' : 'Tools & Technologies:'}
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                    {analyzedData.tools_technologies.map((tt, idx) => (
                      <span key={idx} className="badge badge-cyan" style={{ fontSize: '0.78rem', padding: '3px 10px' }}>
                        {tt}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* All Technical Skills */}
              <div style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--bg-card-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '14px 16px'
              }}>
                <div style={{ fontSize: '0.84rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Layers size={14} color="#34d399" />
                  {isHi ? 'पहचाने गए मुख्य कौशल:' : 'Identified Competencies:'}
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                  {analyzedData.detected_skills && analyzedData.detected_skills.length > 0 ? (
                    analyzedData.detected_skills.map((s, idx) => (
                      <span key={idx} className="badge badge-emerald" style={{ fontSize: '0.78rem', padding: '3px 10px' }}>
                        {s}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                      {isHi ? 'सामान्य इंजीनियरिंग आधारभूत कौशल।' : 'General software engineering fundamentals.'}
                    </span>
                  )}
                </div>
              </div>

            </div>

            {/* Detected Projects */}
            {analyzedData.detected_projects && analyzedData.detected_projects.length > 0 && (
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <FolderGit2 size={16} />
                  {isHi ? 'पहचाने गए प्रोजेक्ट्स एवं ज़िम्मेदारियाँ (Projects & Contributions):' : 'Projects & Technical Contributions:'}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '12px' }}>
                  {analyzedData.detected_projects.map((proj, pIdx) => (
                    <div 
                      key={pIdx}
                      style={{
                        background: 'rgba(255, 255, 255, 0.03)',
                        border: '1px solid var(--bg-card-border)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '16px 20px'
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '6px', marginBottom: '6px' }}>
                        <div style={{ fontWeight: 700, fontSize: '1rem', color: '#fff' }}>
                          {proj.name}
                        </div>
                      </div>

                      {proj.description && (
                        <div style={{ fontSize: '0.88rem', color: 'var(--text-muted)', marginBottom: '10px', lineHeight: 1.5 }}>
                          {proj.description}
                        </div>
                      )}

                      {/* Explicit responsibilities if mentioned */}
                      {proj.responsibilities && (
                        <div style={{
                          fontSize: '0.82rem',
                          color: '#e0e7ff',
                          background: 'rgba(99, 102, 241, 0.1)',
                          borderLeft: '3px solid #818cf8',
                          padding: '6px 12px',
                          borderRadius: '0 4px 4px 0',
                          marginBottom: '10px'
                        }}>
                          <strong>{isHi ? 'उल्लिखित भूमिका:' : 'Candidate Contributions:'}</strong> {proj.responsibilities}
                        </div>
                      )}

                      {/* Stack Badges */}
                      {proj.technologies && proj.technologies.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.78rem', color: 'var(--text-dim)', marginRight: '4px' }}>
                            {isHi ? 'प्रयुक्त तकनीकें:' : 'Stack:'}
                          </span>
                          {proj.technologies.map((t, tIdx) => (
                            <span 
                              key={tIdx} 
                              className="badge badge-purple"
                              style={{ fontSize: '0.75rem', padding: '2px 8px' }}
                            >
                              {t}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Work Experience / Internships if present */}
            {analyzedData.experience && analyzedData.experience.length > 0 && (
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Briefcase size={16} />
                  {isHi ? 'कार्य अनुभव / इंटर्नशिप (Experience):' : 'Work Experience & Internships:'}
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {analyzedData.experience.map((exp, eIdx) => (
                    <div 
                      key={eIdx}
                      style={{
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--bg-card-border)',
                        borderRadius: 'var(--radius-sm)',
                        padding: '12px 16px',
                        fontSize: '0.88rem'
                      }}
                    >
                      <strong style={{ color: '#fff' }}>{exp.role}</strong>
                      {exp.company && <span style={{ color: 'var(--text-muted)' }}> • {exp.company}</span>}
                      {exp.description && (
                        <div style={{ color: 'var(--text-dim)', fontSize: '0.84rem', marginTop: '4px', lineHeight: 1.5 }}>
                          {exp.description}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Confirmation checkbox */}
            <div 
              onClick={() => setConfirmed(!confirmed)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                cursor: 'pointer',
                paddingTop: '6px'
              }}
            >
              <div style={{
                width: '20px',
                height: '20px',
                borderRadius: '4px',
                border: confirmed ? 'none' : '1px solid var(--text-dim)',
                background: confirmed ? 'var(--accent-emerald)' : 'rgba(255, 255, 255, 0.05)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff'
              }}>
                {confirmed && <Check size={14} />}
              </div>
              <span style={{ fontSize: '0.88rem', color: 'var(--text-main)', userSelect: 'none' }}>
                {isHi 
                  ? 'मैं पुष्टि करता हूँ कि ये विवरण मेरे अनुभव का सही प्रतिनिधित्व करते हैं।' 
                  : 'I confirm these details accurately represent my background for personalized questioning.'}
              </span>
            </div>

          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px', paddingTop: '10px' }}>
          
          {/* Skip Resume Option */}
          <button
            type="button"
            className="btn btn-secondary"
            onClick={onSkipResume}
            disabled={isAnalyzing}
            style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <SkipForward size={16} />
            {isHi ? 'बायोडाटा छोड़ें (Skip Resume)' : 'Skip Resume'}
          </button>

          {/* Continue to Interview Button */}
          <button
            type="button"
            className="btn btn-primary"
            disabled={!analyzedData || !confirmed || isAnalyzing}
            onClick={() => onContinueWithResume(analyzedData)}
            style={{
              padding: '12px 28px',
              fontSize: '1rem',
              fontWeight: 700,
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              opacity: (!analyzedData || !confirmed || isAnalyzing) ? 0.5 : 1,
              cursor: (!analyzedData || !confirmed || isAnalyzing) ? 'not-allowed' : 'pointer'
            }}
          >
            <span>{isHi ? 'इंटरव्यू शुरू करें' : 'Continue to Interview'}</span>
            <ArrowRight size={18} />
          </button>
        </div>

        {/* Skip Resume Explanation Notice */}
        <div style={{
          fontSize: '0.82rem',
          color: 'var(--text-dim)',
          textAlign: 'center',
          lineHeight: 1.5,
          borderTop: '1px solid var(--bg-card-border)',
          paddingTop: '16px'
        }}>
          💡 <strong>{isHi ? 'नोट:' : 'Note:'}</strong> {isHi 
            ? 'यदि आप "बायोडाटा छोड़ें" चुनते हैं, तो इंटरव्यू मानक भूमिका-आधारित तकनीकी प्रश्नों के साथ आगे बढ़ेगा।' 
            : 'If you choose "Skip Resume", the interview will use standard job-role-based questions rather than resume-personalized questions.'}
        </div>

      </div>

    </div>
  );
}
