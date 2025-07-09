'use client';

import React from 'react';

const TypingIndicator: React.FC = () => {
  return (
    <div className="flex justify-start">
      <div className="flex space-x-3 max-w-3xl">
        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
          <span className="text-sm">🤖</span>
        </div>
        <div className="bg-white rounded-lg px-4 py-3 shadow-sm border">
          <div className="flex items-center space-x-1">
            <span className="text-gray-500 text-sm">Đang trả lời</span>
            <div className="flex space-x-1 ml-2">
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
              <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TypingIndicator;
