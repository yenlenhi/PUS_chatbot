'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseSpeechSynthesisOptions {
  lang?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
  voiceName?: string;
}

interface UseSpeechSynthesisReturn {
  speak: (text: string) => void;
  stop: () => void;
  pause: () => void;
  resume: () => void;
  isSpeaking: boolean;
  isPaused: boolean;
  isSupported: boolean;
  voices: SpeechSynthesisVoice[];
  currentVoice: SpeechSynthesisVoice | null;
  setVoice: (voice: SpeechSynthesisVoice) => void;
  error: string | null;
}

export const useSpeechSynthesis = (
  options: UseSpeechSynthesisOptions = {}
): UseSpeechSynthesisReturn => {
  const {
    lang = 'vi-VN',
    rate = 1,
    pitch = 1,
    volume = 1,
    voiceName
  } = options;

  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);
  const [currentVoice, setCurrentVoice] = useState<SpeechSynthesisVoice | null>(null);
  const [error, setError] = useState<string | null>(null);

  const utteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  // Check browser support and load voices
  useEffect(() => {
    if (typeof window === 'undefined' || !window.speechSynthesis) {
      setIsSupported(false);
      return;
    }

    setIsSupported(true);

    const loadVoices = () => {
      const availableVoices = window.speechSynthesis.getVoices();
      setVoices(availableVoices);

      // Try to find Vietnamese voice or use specified voice
      if (availableVoices.length > 0 && !currentVoice) {
        let selectedVoice: SpeechSynthesisVoice | undefined;

        // If voiceName is specified, try to find it
        if (voiceName) {
          selectedVoice = availableVoices.find(v => v.name === voiceName);
        }

        // Try to find Vietnamese voice
        if (!selectedVoice) {
          selectedVoice = availableVoices.find(v => v.lang.includes('vi'));
        }

        // Try to find Google Vietnamese voice (usually better quality)
        if (!selectedVoice) {
          selectedVoice = availableVoices.find(v => 
            v.name.toLowerCase().includes('google') && v.lang.includes('vi')
          );
        }

        // Fallback to any voice that supports the language
        if (!selectedVoice) {
          selectedVoice = availableVoices.find(v => v.lang.startsWith(lang.split('-')[0]));
        }

        // Final fallback to first available voice
        if (!selectedVoice && availableVoices.length > 0) {
          selectedVoice = availableVoices[0];
        }

        if (selectedVoice) {
          setCurrentVoice(selectedVoice);
        }
      }
    };

    // Load voices initially
    loadVoices();

    // Chrome loads voices asynchronously
    if (window.speechSynthesis.onvoiceschanged !== undefined) {
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      window.speechSynthesis.cancel();
    };
  }, [lang, voiceName, currentVoice]);

  const speak = useCallback((text: string) => {
    if (!isSupported || !window.speechSynthesis) {
      setError('Trình duyệt không hỗ trợ đọc văn bản');
      return;
    }

    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    setError(null);

    if (!text.trim()) {
      return;
    }

    // Clean the text - remove markdown and special characters
    const cleanText = text
      .replace(/\*\*/g, '') // Bold
      .replace(/\*/g, '')   // Italic
      .replace(/#{1,6}\s/g, '') // Headers
      .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // Links
      .replace(/`{1,3}[^`]*`{1,3}/g, '') // Code blocks
      .replace(/[-•]\s/g, '') // Bullet points
      .replace(/\n+/g, '. ') // New lines to pauses
      .trim();

    if (!cleanText) {
      return;
    }

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = lang;
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = volume;

    if (currentVoice) {
      utterance.voice = currentVoice;
    }

    utterance.onstart = () => {
      setIsSpeaking(true);
      setIsPaused(false);
    };

    utterance.onend = () => {
      setIsSpeaking(false);
      setIsPaused(false);
    };

    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
      setIsPaused(false);
      
      if (event.error !== 'canceled' && event.error !== 'interrupted') {
        setError('Lỗi khi đọc văn bản');
      }
    };

    utterance.onpause = () => {
      setIsPaused(true);
    };

    utterance.onresume = () => {
      setIsPaused(false);
    };

    utteranceRef.current = utterance;
    window.speechSynthesis.speak(utterance);
  }, [isSupported, lang, rate, pitch, volume, currentVoice]);

  const stop = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      setIsPaused(false);
    }
  }, []);

  const pause = useCallback(() => {
    if (window.speechSynthesis && isSpeaking) {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  }, [isSpeaking]);

  const resume = useCallback(() => {
    if (window.speechSynthesis && isPaused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    }
  }, [isPaused]);

  const setVoice = useCallback((voice: SpeechSynthesisVoice) => {
    setCurrentVoice(voice);
  }, []);

  return {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    isPaused,
    isSupported,
    voices,
    currentVoice,
    setVoice,
    error
  };
};

export default useSpeechSynthesis;
