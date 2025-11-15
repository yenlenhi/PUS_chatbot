'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import type { Message } from '@/types';
import type { Source } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Image from 'next/image';
import FileAttachment from '@/components/FileAttachment';

const ChatBotPage = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Xin chào! Tôi là PSU ChatBot của Trường Đại học An ninh Nhân dân. Tôi có thể giúp bạn tìm hiểu các quy định về tuyển sinh; quy chế đào tạo; quy định thi, kiểm tra, đánh giá; quy định về quản lý, giáo dục học viên và hệ thống bảo đảm chất lượng giáo dục, đào tạo của Nhà trường. Bạn cần tôi hỗ trợ gì?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: inputMessage, conversation_id: 'web-chat' })
      });

      if (response.ok) {
        const data = await response.json();

        // Convert string sources to Source objects
        const sources: Source[] = (data.sources || []).map((source: string) => ({
          title: source,
          filename: source,
          confidence: data.confidence
        }));

        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          content: data.response || data.answer || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
          sender: 'bot',
          timestamp: new Date(),
          sources: sources,
          confidence: data.confidence
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('API call failed');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const suggestedQuestions = [
    "Các ngành đào tạo của trường có gì?",
    "Điều kiện tuyển sinh năm 2025?",
    "Học phí của trường như thế nào?",
    "Thông tin về ký túc xá?",
    "Cơ hội việc làm sau khi tốt nghiệp?"
  ];



  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-blue-50">
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-red-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <Image
                src="/assests/logo-main.png"
                alt="Logo Trường Đại học An ninh Nhân dân"
                width={60}
                height={60}
                className="object-contain"
              />
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  Chatbot của trường Đại học An Ninh Nhân Dân
                </h1>
                <p className="text-sm text-gray-600">PSU ChatBot - Hỗ trợ tư vấn 24/7</p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="w-full">
          {/* Chat Interface */}
          <div className="w-full">
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 h-[700px] flex flex-col">
              {/* Chat Header */}
              <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-6 rounded-t-xl">
                <div className="flex items-center space-x-3">
                  <div className="relative">
                    <Image
                      src="/assests/chatbot_avatar.png"
                      alt="PSU ChatBot Avatar"
                      width={48}
                      height={48}
                      className="rounded-full border-2 border-white"
                    />
                    <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"></div>
                  </div>
                  <div>
                    <h2 className="text-lg font-semibold">PSU ChatBot</h2>
                    <p className="text-red-100 text-sm">Đang hoạt động</p>
                  </div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.map((message) => (
                  <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[85%] ${message.sender === 'user' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-800'} rounded-2xl p-4 shadow-sm`}>
                      <div className="flex items-start space-x-3">
                        {message.sender === 'bot' && (
                          <Image
                            src="/assests/chatbot_avatar.png"
                            alt="PSU ChatBot"
                            width={32}
                            height={32}
                            className="rounded-full flex-shrink-0 mt-1"
                          />
                        )}
                        {message.sender === 'user' && <User className="w-6 h-6 mt-1 flex-shrink-0" />}
                        <div className="flex-1 min-w-0">
                          <div className="text-sm markdown-body leading-relaxed">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          </div>

                          {/* File attachments for bot messages */}
                          {message.sender === 'bot' && message.sources && message.sources.length > 0 && (
                            <FileAttachment sources={message.sources} />
                          )}

                          <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-red-200' : 'text-gray-500'}`}>
                            {message.timestamp.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}

                {isTyping && (
                  <div className="flex justify-start">
                    <div className="bg-gray-100 text-gray-800 rounded-2xl p-4 max-w-[85%] shadow-sm">
                      <div className="flex items-center space-x-3">
                        <Image
                          src="/assests/chatbot_avatar.png"
                          alt="PSU ChatBot"
                          width={32}
                          height={32}
                          className="rounded-full"
                        />
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {messages.length === 1 && (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600 font-medium">Câu hỏi gợi ý:</p>
                    <div className="grid grid-cols-1 gap-2">
                      {suggestedQuestions.map((question, index) => (
                        <button
                          key={index}
                          onClick={() => setInputMessage(question)}
                          className="text-left p-3 text-sm bg-white hover:bg-red-50 rounded-lg border border-gray-200 hover:border-red-300 text-gray-700 transition-all duration-200 shadow-sm hover:shadow-md"
                        >
                          {question}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input */}
              <div className="p-6 border-t border-gray-200 bg-gray-50 rounded-b-xl">
                <div className="flex space-x-3">
                  <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Nhập câu hỏi của bạn..."
                    className="flex-1 p-4 border border-gray-300 rounded-xl resize-none focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm leading-relaxed"
                    rows={2}
                    disabled={isTyping}
                  />
                  <button
                    onClick={handleSendMessage}
                    disabled={!inputMessage.trim() || isTyping}
                    className="px-6 py-4 bg-red-600 text-white rounded-xl hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center shadow-sm hover:shadow-md"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBotPage;
