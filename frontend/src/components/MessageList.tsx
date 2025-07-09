import React, { useEffect, useRef } from 'react';
import { Message } from '../types/chat';
import { formatTimestamp } from '../utils/helpers';

interface MessageListProps {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

const MessageList: React.FC<MessageListProps> = ({ messages, isLoading, error }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Hiệu ứng typing cursor và xử lý nội dung
  const renderContent = (message: Message) => {
    // Kiểm tra nếu nội dung rỗng
    if (!message.content && !message.isStreaming) {
      return <span className="text-gray-500 italic">Không có nội dung</span>;
    }
    
    if (message.isStreaming) {
      return (
        <div>
          {message.content || ''}
          <span className="typing-cursor">|</span>
        </div>
      );
    }
    
    return message.content || '';
  };

  // Fallback nếu formatTimestamp gặp lỗi
  const safeFormatTimestamp = (timestamp: string) => {
    try {
      return formatTimestamp(timestamp);
    } catch (error) {
      console.error('Error formatting timestamp:', error);
      return new Date(timestamp).toLocaleTimeString();
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-gray-500">
          <p className="text-lg mb-4">Chào mừng bạn đến với Chatbot Tư vấn Tuyển sinh!</p>
          <p className="mb-2">Bạn có thể hỏi về:</p>
          <ul className="space-y-2 mb-4">
            <li className="cursor-pointer hover:text-blue-600" 
                onClick={() => document.dispatchEvent(new CustomEvent('suggest-question', { detail: 'Điểm chuẩn năm ngoái là bao nhiêu?' }))}>
              • Điểm chuẩn năm ngoái là bao nhiêu?
            </li>
            <li className="cursor-pointer hover:text-blue-600"
                onClick={() => document.dispatchEvent(new CustomEvent('suggest-question', { detail: 'Các ngành đào tạo của trường?' }))}>
              • Các ngành đào tạo của trường?
            </li>
            <li className="cursor-pointer hover:text-blue-600"
                onClick={() => document.dispatchEvent(new CustomEvent('suggest-question', { detail: 'Học phí năm nay là bao nhiêu?' }))}>
              • Học phí năm nay là bao nhiêu?
            </li>
          </ul>
        </div>
      ) : (
        messages.map((message) => (
          <div key={message.id} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`rounded-lg p-4 max-w-[80%] ${
              message.role === 'user' 
                ? 'bg-blue-600 text-white' 
                : message.error 
                  ? 'bg-red-50 text-red-800 border border-red-200' 
                  : 'bg-gray-100 text-gray-800'
            }`}>
              <div className="flex items-center mb-2">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                  message.role === 'user' ? 'bg-blue-700' : 'bg-gray-300'
                }`}>
                  {message.role === 'user' ? 'U' : 'B'}
                </div>
                <div className="text-xs opacity-70">{safeFormatTimestamp(message.timestamp)}</div>
                {message.role === 'assistant' && message.confidence !== undefined && (
                  <div className="ml-auto text-xs">
                    Độ tin cậy: {Math.round(message.confidence * 100)}%
                  </div>
                )}
              </div>
              
              <div className="whitespace-pre-wrap">
                {renderContent(message)}
                {message.role === 'assistant' && !message.content && !message.isStreaming && (
                  <div className="text-red-500 mt-2">
                    <p>Không nhận được câu trả lời từ server. Vui lòng thử lại.</p>
                  </div>
                )}
              </div>
              
              {message.sources && message.sources.length > 0 && !message.isStreaming && (
                <div className="mt-3 pt-3 border-t border-gray-200 text-sm">
                  <div className="font-medium mb-1">Nguồn tham khảo:</div>
                  <ul className="space-y-1">
                    {message.sources.map((source, index) => (
                      <li key={index} className="text-blue-600">
                        {typeof source === 'string' ? (
                          <span>{source}</span>
                        ) : source.url ? (
                          <a href={source.url} target="_blank" rel="noopener noreferrer" className="hover:underline">
                            {source.title}
                          </a>
                        ) : (
                          <span>{source.title}</span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))
      )}
      
      {isLoading && !messages.some(m => m.isStreaming) && (
        <div className="flex justify-start">
          <div className="bg-gray-100 rounded-lg p-4 max-w-[80%]">
            <div className="flex items-center">
              <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center mr-2">
                B
              </div>
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>{error}</p>
        </div>
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;



