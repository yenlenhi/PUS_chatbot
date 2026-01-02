'use client';

import React from 'react';
import { MessageCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

const ChatBot = () => {
  const router = useRouter();

  const handleChatClick = () => {
    router.push('/chat-bot');
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        onClick={handleChatClick}
        className="fixed bottom-6 right-6 w-14 h-14 bg-red-600 hover:bg-red-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 z-40 flex items-center justify-center animate-pulse hover:animate-none block"
        title="Chat với tư vấn viên"
      >
        <MessageCircle className="w-6 h-6" />
        <div className="absolute -top-1 -right-1 w-4 h-4 bg-yellow-400 rounded-full flex items-center justify-center">
          <span className="text-xs font-bold text-red-800">!</span>
        </div>
      </button>
    </>
  );
};

export default ChatBot;
