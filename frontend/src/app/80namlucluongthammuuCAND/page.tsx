'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, ExternalLink, Volume2, VolumeX, Pause, Play, ImagePlus, X, ZoomIn } from 'lucide-react';
import type { Message, UploadedImage } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import Image from 'next/image';
import FeedbackButtons from '@/components/FeedbackButtons';
import VoiceInputButton from '@/components/VoiceInputButton';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';

export default function ThamMuuCAND80Nam() {
  const [conversationId] = useState(() => `thammuu-chat-${Date.now()}`);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Tôi là trợ lý AI của cuộc thi **Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân (18/4/1946 – 18/4/2026)**. Tôi có thể giúp bạn tìm hiểu về lịch sử, truyền thống và những đóng góp của lực lượng Tham mưu CAND trong 80 năm qua. Bạn cần tôi hỗ trợ gì?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [previewImage, setPreviewImage] = useState<string | null>(null);
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Speech Recognition (Voice to Text)
  const {
    transcript,
    isListening,
    isSupported: speechRecognitionSupported,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition({ lang: 'vi-VN' });

  // Speech Synthesis (Text to Voice)
  const {
    speak,
    stop: stopSpeaking,
    pause: pauseSpeaking,
    resume: resumeSpeaking,
    isSpeaking,
    isPaused,
    isSupported: speechSynthesisSupported
  } = useSpeechSynthesis({ lang: 'vi-VN', rate: 1 });

  // Update input when speech recognition completes
  useEffect(() => {
    if (transcript && !isListening) {
      setInputMessage(prev => prev + (prev ? ' ' : '') + transcript);
      resetTranscript();
    }
  }, [transcript, isListening, resetTranscript]);

  // Reset speaking message id when speech ends
  useEffect(() => {
    if (!isSpeaking) {
      setSpeakingMessageId(null);
    }
  }, [isSpeaking]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle text-to-speech
  const handleSpeak = useCallback((content: string, messageId: string) => {
    setSpeakingMessageId(messageId);
    speak(content);
  }, [speak]);

  const handleStopSpeaking = useCallback(() => {
    stopSpeaking();
    setSpeakingMessageId(null);
  }, [stopSpeaking]);

  // Image upload handling
  const handleImageSelect = useCallback(async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0) return;

    const maxImages = 4;
    const maxSizeMB = 10;
    const remainingSlots = maxImages - uploadedImages.length;

    if (remainingSlots <= 0) {
      alert(`Chỉ được tải tối đa ${maxImages} ảnh`);
      return;
    }

    const filesToProcess = Array.from(files).slice(0, remainingSlots);
    const newImages: UploadedImage[] = [];

    for (const file of filesToProcess) {
      if (!file.type.startsWith('image/')) continue;
      const sizeMB = file.size / (1024 * 1024);
      if (sizeMB > maxSizeMB) continue;

      try {
        const base64 = await new Promise<string>((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          reader.onload = () => resolve(reader.result as string);
          reader.onerror = error => reject(error);
        });

        newImages.push({
          id: `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
          name: file.name,
          mimeType: file.type,
          file,
          preview: URL.createObjectURL(file),
          base64
        });
      } catch (err) {
        console.error('Error processing image:', err);
      }
    }

    if (newImages.length > 0) {
      setUploadedImages(prev => [...prev, ...newImages]);
    }

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [uploadedImages.length]);

  const handleRemoveImage = useCallback((id: string) => {
    const imageToRemove = uploadedImages.find(img => img.id === id);
    if (imageToRemove) {
      URL.revokeObjectURL(imageToRemove.preview);
    }
    setUploadedImages(prev => prev.filter(img => img.id !== id));
  }, [uploadedImages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() && uploadedImages.length === 0) return;

    const currentQuery = inputMessage;
    const currentImages = [...uploadedImages];

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      sender: 'user',
      timestamp: new Date(),
      uploadedImages: currentImages.length > 0 ? currentImages : undefined
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setUploadedImages([]);
    setIsTyping(true);

    try {
      const response = await fetch('/api/thammuu', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: currentQuery, 
          conversation_id: conversationId,
          images: currentImages.map(img => ({
            base64: img.base64,
            mimeType: img.mimeType,
            name: img.name
          }))
        })
      });

      if (response.ok) {
        const data = await response.json();
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: data.response || data.answer || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
          sender: 'bot',
          timestamp: new Date(),
          userQuery: currentQuery
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        throw new Error('API call failed');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
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
    "Lịch sử hình thành lực lượng Tham mưu CAND?",
    "Ngày truyền thống của lực lượng Tham mưu CAND?",
    "Những đóng góp nổi bật của lực lượng Tham mưu CAND?",
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Background */}
      <div 
        className="absolute inset-0 z-0"
        style={{
          background: 'linear-gradient(135deg, #8B0000 0%, #DC143C 50%, #FF6347 100%)',
        }}
      >
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-0 left-0 w-full h-full bg-gradient-to-r from-yellow-400/30 to-transparent"></div>
        </div>
        <div className="absolute top-20 right-20 text-yellow-400 text-9xl opacity-80">★</div>
        <div className="absolute bottom-40 right-40 text-yellow-400 text-6xl opacity-60">★</div>
        <div className="absolute left-0 bottom-0 w-1/3 h-full bg-gradient-to-r from-red-900/80 to-transparent"></div>
        <div className="absolute right-0 top-0 w-1/2 h-full">
          <div className="absolute inset-0 bg-gradient-to-l from-red-800/90 to-transparent"></div>
          <div className="absolute right-10 top-1/2 -translate-y-1/2 text-right">
            <div className="text-yellow-400 text-8xl font-bold opacity-90">80</div>
            <div className="text-yellow-400 text-3xl font-bold opacity-80">NĂM</div>
            <div className="text-white text-2xl font-semibold mt-2 opacity-90">TRUYỀN THỐNG</div>
            <div className="text-yellow-400 text-xl font-semibold opacity-80">THAM MƯU CAND</div>
            <div className="text-white text-lg mt-4 opacity-70">18/4/1946 - 18/4/2026</div>
          </div>
        </div>
      </div>

      {/* Header */}
      <header className="relative z-10 bg-white/95 shadow-lg">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-full bg-red-600 flex items-center justify-center">
              <span className="text-yellow-400 text-2xl">★</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">80 năm Tham mưu CAND</h1>
              <p className="text-sm text-gray-600">18/4/1946 – 18/4/2026</p>
            </div>
          </div>
          <a 
            href="#cuocthi"
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors flex items-center space-x-2"
          >
            <span>Cuộc thi tìm hiểu</span>
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </header>

      {/* Main Content - Chat Interface */}
      <main className="relative z-10 flex items-center justify-center min-h-[calc(100vh-80px)] p-4">
        <div className="w-full max-w-4xl">
          <div className="bg-white rounded-2xl shadow-2xl overflow-hidden">
            {/* Chat Header với Avatar */}
            <div className="bg-blue-700 text-white p-4 flex items-center space-x-3">
              <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-md">
                <Image
                  src="/assests/chatbot_avatar.png"
                  alt="Chatbot Avatar"
                  width={40}
                  height={40}
                  className="w-full h-full object-cover"
                />
              </div>
              <div>
                <h2 className="font-bold text-lg">Trợ lý AI Tham mưu CAND</h2>
                <div className="flex items-center space-x-2">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  <span className="text-sm text-blue-200">Đang hoạt động</span>
                </div>
              </div>
            </div>

            {/* Messages Area */}
            <div className="h-[calc(100vh-380px)] min-h-[400px] overflow-y-auto p-4 space-y-4 bg-gray-50">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%]`}>
                    {message.sender === 'bot' && (
                      <div className="flex items-start space-x-2">
                        <div className="w-8 h-8 rounded-full overflow-hidden flex-shrink-0 shadow-md">
                          <Image
                            src="/assests/chatbot_avatar.png"
                            alt="Bot"
                            width={32}
                            height={32}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div className="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-gray-100">
                          <div className="text-sm text-gray-800 markdown-body">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                          
                          {/* Footer với time và TTS button */}
                          <div className="flex items-center gap-2 mt-2 pt-2 border-t border-gray-100">
                            <p className="text-xs text-gray-400">
                              {new Date(message.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                            </p>
                            
                            {/* Text-to-Speech button */}
                            {message.id !== '1' && speechSynthesisSupported && (
                              <>
                                {speakingMessageId === message.id && isSpeaking ? (
                                  <div className="flex items-center gap-1">
                                    <button
                                      onClick={isPaused ? resumeSpeaking : pauseSpeaking}
                                      className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 rounded-md transition-all"
                                      title={isPaused ? 'Tiếp tục' : 'Tạm dừng'}
                                    >
                                      {isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />}
                                    </button>
                                    <button
                                      onClick={handleStopSpeaking}
                                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded-md transition-all"
                                      title="Dừng"
                                    >
                                      <VolumeX className="w-3 h-3" />
                                    </button>
                                  </div>
                                ) : (
                                  <button
                                    onClick={() => handleSpeak(message.content, message.id)}
                                    className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-600 rounded-md transition-all"
                                    title="Nghe câu trả lời"
                                  >
                                    <Volume2 className="w-3 h-3" />
                                    <span>Nghe</span>
                                  </button>
                                )}
                              </>
                            )}
                          </div>
                          
                          {message.id !== '1' && (
                            <FeedbackButtons
                              conversationId={conversationId}
                              messageId={message.id}
                              query={message.userQuery || ''}
                              answer={message.content}
                              chunkIds={message.chunkIds}
                              className="mt-2 pt-2 border-t border-gray-100"
                            />
                          )}
                        </div>
                      </div>
                    )}
                    
                    {message.sender === 'user' && (
                      <div>
                        {/* User uploaded images */}
                        {message.uploadedImages && message.uploadedImages.length > 0 && (
                          <div className="mb-2 flex flex-wrap gap-2 justify-end">
                            {message.uploadedImages.map((img, idx) => (
                              <div 
                                key={img.id || idx} 
                                className="relative group cursor-pointer"
                                onClick={() => setPreviewImage(img.preview || img.base64 || '')}
                              >
                                <div className="w-20 h-20 rounded-xl overflow-hidden shadow-lg border-2 border-white hover:border-blue-400 transition-all">
                                  <img
                                    src={img.preview || img.base64}
                                    alt={`Uploaded ${idx + 1}`}
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                                <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 rounded-xl transition-all flex items-center justify-center">
                                  <ZoomIn className="w-5 h-5 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        
                        {message.content && (
                          <div className="bg-blue-600 text-white p-3 rounded-2xl rounded-tr-none shadow-sm">
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs text-blue-200 mt-1">
                              {new Date(message.timestamp).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-8 h-8 rounded-full overflow-hidden shadow-md">
                      <Image
                        src="/assests/chatbot_avatar.png"
                        alt="Bot"
                        width={32}
                        height={32}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Questions */}
            {messages.length === 1 && (
              <div className="px-4 py-3 bg-white border-t border-gray-100">
                <p className="text-sm text-gray-500 mb-2">Câu hỏi gợi ý:</p>
                <div className="space-y-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(question)}
                      className="w-full text-left p-3 text-sm bg-gray-50 hover:bg-blue-50 hover:text-blue-700 rounded-xl border border-gray-200 hover:border-blue-300 transition-all duration-200"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Image preview thumbnails */}
            {uploadedImages.length > 0 && (
              <div className="px-4 py-2 bg-gray-50 border-t border-gray-200">
                <div className="flex flex-wrap gap-2">
                  {uploadedImages.map((image) => (
                    <div key={image.id} className="relative group w-16 h-16 rounded-lg overflow-hidden border border-gray-200">
                      <img src={image.preview} alt="Preview" className="w-full h-full object-cover" />
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-1">
                        <button
                          type="button"
                          onClick={() => setPreviewImage(image.preview)}
                          className="p-1 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
                        >
                          <ZoomIn className="w-3 h-3 text-white" />
                        </button>
                        <button
                          type="button"
                          onClick={() => handleRemoveImage(image.id)}
                          className="p-1 bg-white/20 rounded-full hover:bg-red-500/80 transition-colors"
                        >
                          <X className="w-3 h-3 text-white" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Input Area */}
            <div className="p-4 border-t border-gray-200 bg-white">
              <div className="flex items-center space-x-2">
                {/* Image upload button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isTyping || uploadedImages.length >= 4}
                  className="p-3 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  title="Tải ảnh lên"
                >
                  <ImagePlus className="w-5 h-5" />
                </button>
                
                {/* Voice input button */}
                <VoiceInputButton
                  isListening={isListening}
                  isSupported={speechRecognitionSupported}
                  onStart={startListening}
                  onStop={stopListening}
                  disabled={isTyping}
                />
                
                {/* Text input */}
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Nhập câu hỏi hoặc dán ảnh (Ctrl+V)..."
                  className="flex-1 p-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isTyping}
                />
                
                {/* Send button */}
                <button
                  onClick={handleSendMessage}
                  disabled={(!inputMessage.trim() && uploadedImages.length === 0) || isTyping}
                  className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors duration-200"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
              
              {/* Hidden file input */}
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                multiple
                onChange={handleImageSelect}
                className="hidden"
                disabled={isTyping}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer Banner */}
      <footer className="relative z-10 bg-red-800/90 text-white text-center py-3">
        <p className="text-sm">
          Cuộc thi Tìm hiểu 80 năm Ngày truyền thống lực lượng Tham mưu Công an nhân dân (18/4/1946 – 18/4/2026)
        </p>
      </footer>

      {/* Image Preview Modal */}
      {previewImage && (
        <div
          className="fixed inset-0 z-50 bg-black/90 flex items-center justify-center p-4"
          onClick={() => setPreviewImage(null)}
        >
          <button
            onClick={() => setPreviewImage(null)}
            className="absolute top-4 right-4 p-2 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
          >
            <X className="w-6 h-6 text-white" />
          </button>
          <img
            src={previewImage}
            alt="Full preview"
            className="max-w-full max-h-full object-contain rounded-lg"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
