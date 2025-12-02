'use client';

import React from 'react';
import { Volume2, VolumeX, Pause, Play } from 'lucide-react';

interface TextToSpeechButtonProps {
  isSpeaking: boolean;
  isPaused: boolean;
  isSupported: boolean;
  onSpeak: () => void;
  onStop: () => void;
  onPause: () => void;
  onResume: () => void;
  className?: string;
  size?: 'sm' | 'md';
}

export const TextToSpeechButton: React.FC<TextToSpeechButtonProps> = ({
  isSpeaking,
  isPaused,
  isSupported,
  onSpeak,
  onStop,
  onPause,
  onResume,
  className = '',
  size = 'sm'
}) => {
  if (!isSupported) {
    return null;
  }

  const iconSize = size === 'sm' ? 'w-3 h-3' : 'w-4 h-4';
  const buttonPadding = size === 'sm' ? 'px-2 py-1' : 'px-3 py-2';

  if (isSpeaking) {
    return (
      <div className={`flex items-center gap-1 ${className}`}>
        <button
          type="button"
          onClick={isPaused ? onResume : onPause}
          className={`flex items-center gap-1 ${buttonPadding} text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-all duration-200`}
          title={isPaused ? 'Tiếp tục' : 'Tạm dừng'}
        >
          {isPaused ? (
            <>
              <Play className={iconSize} />
              <span>Tiếp tục</span>
            </>
          ) : (
            <>
              <Pause className={iconSize} />
              <span>Tạm dừng</span>
            </>
          )}
        </button>
        <button
          type="button"
          onClick={onStop}
          className={`flex items-center gap-1 ${buttonPadding} text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded-md transition-all duration-200`}
          title="Dừng đọc"
        >
          <VolumeX className={iconSize} />
          <span>Dừng</span>
        </button>
      </div>
    );
  }

  return (
    <button
      type="button"
      onClick={onSpeak}
      className={`flex items-center gap-1 ${buttonPadding} text-xs bg-gray-200 hover:bg-gray-300 text-gray-600 rounded-md transition-all duration-200 ${className}`}
      title="Nghe câu trả lời"
    >
      <Volume2 className={iconSize} />
      <span>Nghe</span>
    </button>
  );
};

export default TextToSpeechButton;
