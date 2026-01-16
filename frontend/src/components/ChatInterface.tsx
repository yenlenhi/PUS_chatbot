'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import type { Message } from '@/types/chat';
import type { Source } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import SourceSection from './SourceSection';
import FeedbackButtons from './FeedbackButtons';
import { SSEParser } from '@/utils/sseUtils';

const ChatInterface = () => {
  const [conversationId] = useState(() => `web-chat-${Date.now()}`);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Xin chào! Tôi là chatbot tư vấn tuyển sinh của Trường Đại học An ninh Nhân dân. Tôi có thể giúp bạn tìm hiểu về các ngành đào tạo, điều kiện tuyển sinh, học phí và nhiều thông tin khác. Bạn cần hỗ trợ gì?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<string | null>(null);
  const [currentStreamingContent, setCurrentStreamingContent] = useState('');
  const [streamingStatus, setStreamingStatus] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const currentQuery = inputMessage; // Store query before clearing

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputMessage,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Create bot message for streaming
    const botMessageId = (Date.now() + 1).toString();
    setStreamingMessageId(botMessageId);
    setCurrentStreamingContent('');

    const initialBotMessage: Message = {
      id: botMessageId,
      content: '',
      sender: 'bot',
      timestamp: new Date(),
      isStreaming: true
    };

    setMessages(prev => [...prev, initialBotMessage]);

    try {
      const response = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream'
        },
        body: JSON.stringify({ 
          message: currentQuery, 
          conversation_id: conversationId,
          language: 'vi' // You can make this dynamic
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      const parser = new SSEParser();
      let fullContent = '';
      let sources: Source[] = [];
      let confidence = 0;
      let chunkIds: number[] = [];
      let sourceReferences: any[] = [];

      if (reader) {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value, { stream: true });
          const events = parser.addData(chunk);

          for (const event of events) {
            if (event.type === 'answer_chunk' && event.content) {
              fullContent += event.content;
              setCurrentStreamingContent(fullContent);
              
              // Update the streaming message
              setMessages(prev => 
                prev.map(msg => 
                  msg.id === botMessageId 
                    ? { ...msg, content: fullContent }
                    : msg
                )
              );
            } else if (event.type === 'sources') {
            } else if (event.type === 'sources') {
              sources = (event.sources || []).map((source: string) => ({
                title: source,
                filename: source,
                confidence: event.confidence || 0
              }));
              confidence = event.confidence || 0;
              sourceReferences = event.source_references || [];
              
              // Extract chunk IDs
              chunkIds = sourceReferences
                .map((ref: { chunk_id: string }) => parseInt(ref.chunk_id, 10))
                .filter((id: number) => !isNaN(id));
            } else if (event.type === 'complete') {
              // Streaming completed
              break;
            } else if (event.type === 'error') {
              throw new Error(event.message || 'Streaming error');
            } else if (event.type === 'status') {
              // Show status messages to user
              setStreamingStatus(event.message || '');
              console.log('Status:', event.message);
            }
          }
        }
        
        // Process any remaining buffered data
        const finalEvents = parser.flush();
        for (const event of finalEvents) {
          if (event.type === 'answer_chunk' && event.content) {
            fullContent += event.content;
          }
        }
      }

      // Final update with all metadata
      setMessages(prev => 
        prev.map(msg => 
          msg.id === botMessageId 
            ? { 
                ...msg, 
                content: fullContent || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
                isStreaming: false,
                sources,
                confidence,
                userQuery: currentQuery,
                chunkIds
              }
            : msg
        )
      );

    } catch (error) {
      console.error('Error sending streaming message:', error);
      
      // Update with error message
      setMessages(prev => 
        prev.map(msg => 
          msg.id === botMessageId 
            ? { 
                ...msg, 
                content: 'Xin lỗi, có lỗi xảy ra khi xử lý yêu cầu. Vui lòng thử lại sau.',
                isStreaming: false
              }
            : msg
        )
      );
    } finally {
      setIsTyping(false);
      setStreamingMessageId(null);
      setCurrentStreamingContent('');
      setStreamingStatus('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleDownloadSource = async (source: Source) => {
    try {
      // Create a download link for the PDF file
      // In a real implementation, this would call an API to get the file
      console.log('Downloading source:', source.filename);

      // For now, show a message that this feature is coming soon
      alert(`Tính năng tải xuống "${source.filename}" sẽ được cập nhật sớm. Vui lòng liên hệ phòng tuyển sinh để nhận tài liệu.`);
    } catch (error) {
      console.error('Error downloading source:', error);
      alert('Có lỗi xảy ra khi tải xuống tài liệu. Vui lòng thử lại sau.');
    }
  };

  const handleViewSourceDetails = (source: Source) => {
    try {
      // Show detailed information about the source
      const details = `
Thông tin chi tiết về nguồn tham khảo:

📄 Tên tài liệu: ${source.title}
📁 File: ${source.filename}
${source.page ? `[object Object]source.page}` : ''}
${source.confidence ? `⭐ Độ tin cậy: ${Math.round(source.confidence * 100)}%` : ''}

${source.content ? `📝 Nội dung liên quan:\n${source.content.substring(0, 300)}...` : ''}

Để có thông tin đầy đủ, vui lòng liên hệ phòng tuyển sinh của trường.
      `.trim();

      alert(details);
    } catch (error) {
      console.error('Error viewing source details:', error);
      alert('Có lỗi xảy ra khi xem chi tiết. Vui lòng thử lại sau.');
    }
  };

  const suggestedQuestions = [
    "Các ngành đào tạo của trường có gì?",
    "Điều kiện tuyển sinh năm 2025?",
    "Học phí của trường như thế nào?",
  ];

  return (
    <div className="w-full h-full bg-white rounded-lg shadow-lg flex flex-col border border-gray-200">
      {/* Header */}
      <div className="bg-red-600 text-white p-4 rounded-t-lg flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Bot className="w-5 h-5" />
          <span className="font-semibold">Chatbot Tư Vấn</span>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[85%] p-4 rounded-lg shadow-sm ${message.sender === 'user' ? 'bg-red-600 text-white' : 'bg-gray-100 text-gray-800'}`}>
              <div className="flex items-start space-x-3">
                {message.sender === 'bot' && (
                  <div className="flex-shrink-0">
                    {message.isStreaming ? (
                      <Loader2 className="w-5 h-5 mt-0.5 text-red-600 animate-spin" />
                    ) : (
                      <Bot className="w-5 h-5 mt-0.5" />
                    )}
                  </div>
                )}
                {message.sender === 'user' && <User className="w-5 h-5 mt-0.5 flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <div className="text-sm markdown-body leading-relaxed">
                    {message.content ? (
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {message.content}
                      </ReactMarkdown>
                    ) : message.isStreaming ? (
                      <div className="flex items-center space-x-2 text-gray-500 italic">
                        <span>{message.id === streamingMessageId && streamingStatus ? streamingStatus : 'Đang soạn câu trả lời'}</span>
                        <div className="flex space-x-1">
                          <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-1 h-1 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    ) : null}
                  </div>

                  {/* Sources Section - only for bot messages and not streaming */}
                  {message.sender === 'bot' && message.sources && message.sources.length > 0 && !message.isStreaming && (
                    <SourceSection
                      sources={message.sources}
                      confidence={message.confidence}
                      onDownloadSource={handleDownloadSource}
                      onViewSourceDetails={handleViewSourceDetails}
                      className="mt-3"
                    />
                  )}

                  <p className={`text-xs mt-2 ${message.sender === 'user' ? 'text-red-200' : 'text-gray-500'}`}>
                    {message.timestamp.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                  </p>

                  {/* Feedback Buttons - only for bot messages (except welcome message) and not streaming */}
                  {message.sender === 'bot' && message.id !== '1' && !message.isStreaming && (
                    <FeedbackButtons
                      conversationId={conversationId}
                      messageId={message.id}
                      query={message.userQuery || ''}
                      answer={message.content}
                      chunkIds={message.chunkIds}
                      className="mt-3 pt-3 border-t border-gray-200"
                    />
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-800 p-4 rounded-lg max-w-[85%] shadow-sm">
              <div className="flex items-center space-x-3">
                <Bot className="w-5 h-5" />
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
          <div className="space-y-3 px-2">
            <p className="text-sm text-gray-600 font-medium">Câu hỏi gợi ý:</p>
            {suggestedQuestions.map((question, index) => (
              <button key={index} onClick={() => setInputMessage(question)} className="block w-full text-left p-3 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg border text-gray-700 transition-colors duration-200 shadow-sm">
                {question}
              </button>
            ))}
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        <div className="flex space-x-3">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Nhập câu hỏi của bạn..."
            className="flex-1 p-3 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm leading-relaxed"
            rows={3}
            disabled={isTyping}
          />
          <button onClick={handleSendMessage} disabled={!inputMessage.trim() || isTyping} className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center shadow-sm">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

