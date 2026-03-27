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
      {/* Floating Chat Button — 3D beveled style */}
      <button
        type="button"
        onClick={handleChatClick}
        title="Chat với tư vấn viên"
        className="group fixed bottom-6 right-6 z-40 flex h-14 w-14 items-center justify-center rounded-full border border-white/25 bg-gradient-to-b from-red-500 via-red-600 to-red-800 text-white shadow-[0_5px_0_0_rgb(69,10,10),0_10px_28px_rgba(185,28,28,0.55),inset_0_1px_0_rgba(255,255,255,0.45),inset_0_-2px_6px_rgba(0,0,0,0.12)] transition-[transform,box-shadow,filter] duration-200 ease-out hover:-translate-y-0.5 hover:shadow-[0_6px_0_0_rgb(69,10,10),0_14px_34px_rgba(220,38,38,0.5),inset_0_1px_0_rgba(255,255,255,0.5),inset_0_-2px_6px_rgba(0,0,0,0.1)] hover:brightness-105 active:translate-y-[3px] active:shadow-[0_2px_0_0_rgb(69,10,10),0_6px_16px_rgba(127,29,29,0.45),inset_0_3px_8px_rgba(0,0,0,0.22),inset_0_1px_0_rgba(255,255,255,0.25)] focus:outline-none focus-visible:ring-2 focus-visible:ring-amber-300/90 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-100"
      >
        <MessageCircle
          className="relative z-[1] h-7 w-7 drop-shadow-[0_1px_1px_rgba(0,0,0,0.35)] transition-transform duration-200 group-hover:scale-105"
          strokeWidth={2.25}
        />
        <span
          className="absolute -top-0.5 -right-0.5 flex h-[18px] min-w-[18px] items-center justify-center rounded-full border border-amber-200/80 bg-gradient-to-b from-amber-300 to-amber-500 px-0.5 text-[10px] font-black leading-none text-red-900 shadow-[0_2px_0_0_rgb(146,64,14),0_3px_8px_rgba(245,158,11,0.55),inset_0_1px_0_rgba(255,255,255,0.65)] ring-1 ring-white/40 transition-transform duration-200 group-hover:scale-110"
          aria-hidden
        >
          !
        </span>
      </button>
    </>
  );
};

export default ChatBot;
