'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
}

const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Listen for suggested questions
  useEffect(() => {
    const handleSuggestedQuestion = (e: CustomEvent<string>) => {
      setMessage(e.detail);
      textareaRef.current?.focus();
    };

    document.addEventListener('suggest-question' as any, handleSuggestedQuestion as any);

    return () => {
      document.removeEventListener('suggest-question' as any, handleSuggestedQuestion as any);
    };
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }
  }, [message]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <form onSubmit={handleSubmit} className="flex items-end gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Nhập câu hỏi của bạn..."
            className="w-full border border-gray-300 rounded-lg py-3 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            disabled={isLoading}
          />
          {message.length === 0 && (
            <div className="absolute bottom-2 right-3 text-xs text-gray-400">
              Nhấn Enter để gửi
            </div>
          )}
        </div>
        <button
          type="submit"
          className={`p-3 rounded-full ${
            message.trim() && !isLoading
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          } transition-colors`}
          disabled={!message.trim() || isLoading}
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatInput;