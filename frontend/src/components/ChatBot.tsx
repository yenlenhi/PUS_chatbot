'use client';

import React, { useState } from 'react';
import { MessageCircle, X } from 'lucide-react';
import ChatInterface from './ChatInterface';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-6 right-6 w-14 h-14 bg-red-600 hover:bg-red-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-40 flex items-center justify-center animate-pulse hover:animate-none ${
          isOpen ? 'hidden' : 'block'
        }`}
        title="Chat với tư vấn viên"
      >
        <MessageCircle className="w-6 h-6" />
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
          <span className="text-xs font-bold text-red-800">!</span>
        </div>
      </button>

      {/* Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-3rem)] rounded-lg shadow-2xl z-50 flex flex-col md:w-96 md:h-[500px]">
           <button
              onClick={() => setIsOpen(false)}
              className="absolute top-2 right-2 bg-red-700 text-white hover:bg-red-800 p-1 rounded-full z-10"
            >
              <X className="w-4 h-4" />
            </button>
          <ChatInterface />
        </div>
      )}
    </>
  );
};


export default ChatBot;
