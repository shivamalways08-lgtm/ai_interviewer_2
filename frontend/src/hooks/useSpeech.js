import { useState, useEffect, useRef, useCallback } from 'react';

/**
 * Custom hook for Web Speech API
 * Provides Speech Recognition (Speech-to-Text) and Speech Synthesis (Text-to-Speech)
 * Supports English (en-US) and Hindi (hi-IN)
 */
export function useSpeech(language = 'en') {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [speechError, setSpeechError] = useState(null);
  const [isSpeaking, setIsSpeaking] = useState(false);

  const recognitionRef = useRef(null);

  // Check if speech recognition is supported in browser
  const isRecognitionSupported = typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window);

  const isSynthesisSupported = typeof window !== 'undefined' &&
    'speechSynthesis' in window;

  const langCode = language === 'hi' ? 'hi-IN' : 'en-US';

  useEffect(() => {
    if (!isRecognitionSupported) return;

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = langCode;

    recognition.onstart = () => {
      setIsListening(true);
      setSpeechError(null);
    };

    recognition.onresult = (event) => {
      let currentTranscript = '';
      for (let i = 0; i < event.results.length; i++) {
        currentTranscript += event.results[i][0].transcript;
      }
      setTranscript(currentTranscript);
    };

    recognition.onerror = (event) => {
      console.warn('Speech recognition event error:', event.error);
      if (event.error === 'not-allowed') {
        setSpeechError('Microphone access was denied. Please allow microphone permissions or switch to text mode.');
      } else if (event.error === 'no-speech') {
        // Not a fatal error
      } else {
        setSpeechError(`Speech recognition issue: ${event.error}. You can edit your answer in the text box below.`);
      }
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      try {
        recognition.stop();
      } catch (e) {
        // cleanup
      }
    };
  }, [isRecognitionSupported, langCode]);

  const startListening = useCallback(() => {
    setSpeechError(null);
    if (!recognitionRef.current) {
      setSpeechError('Speech recognition is not supported in this browser. Please use text mode.');
      return;
    }
    try {
      recognitionRef.current.lang = langCode;
      recognitionRef.current.start();
    } catch (err) {
      console.warn('Recognition start error:', err);
    }
  }, [langCode]);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop();
      } catch (err) {
        // ignore
      }
    }
    setIsListening(false);
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setSpeechError(null);
  }, []);

  // Text to Speech
  const speak = useCallback((text, lang = language) => {
    if (!isSynthesisSupported || !text) return;

    window.speechSynthesis.cancel(); // Stop any currently playing audio

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = lang === 'hi' ? 'hi-IN' : 'en-US';
    utterance.rate = 0.95; // Slightly measured pace for clarity

    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    window.speechSynthesis.speak(utterance);
  }, [isSynthesisSupported, language]);

  const stopSpeaking = useCallback(() => {
    if (isSynthesisSupported) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, [isSynthesisSupported]);

  return {
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
    stopSpeaking,
    isSynthesisSupported
  };
}
