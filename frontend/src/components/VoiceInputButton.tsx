'use client';

import React from 'react';
import { Mic, MicOff, Square } from 'lucide-react';

interface VoiceInputButtonProps {
  isListening: boolean;
  isSupported: boolean;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
  className?: string;
}

export const VoiceInputButton: React.FC<VoiceInputButtonProps> = ({
  isListening,
  isSupported,
  onStart,
  onStop,
  disabled = false,
  className = ''
}) => {
  if (!isSupported) {
    return null;
  }

  return (
    <button
      type="button"
      onClick={isListening ? onStop : onStart}
      disabled={disabled}
      className={`p-3 rounded-xl transition-all duration-200 flex items-center justify-center ${
        isListening
          ? 'bg-red-500 text-white animate-pulse hover:bg-red-600'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      } ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
      title={isListening ? 'Dừng ghi âm' : 'Nhấn để nói'}
    >
      {isListening ? (
        <Square className="w-5 h-5" />
      ) : (
        <Mic className="w-5 h-5" />
      )}
    </button>
  );
};

export default VoiceInputButton;
