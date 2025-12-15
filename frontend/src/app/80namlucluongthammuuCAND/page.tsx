'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Send, ExternalLink, Volume2, VolumeX, Pause, Play, ImagePlus, X, ZoomIn, Star, Calendar, Award, Users, ChevronRight, MessageCircle } from 'lucide-react';
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
  const [showChat, setShowChat] = useState(false);
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

  const milestones = [
    { year: "1946", event: "Ngày 18/4/1946 - Thành lập lực lượng Tham mưu CAND" },
    { year: "1954", event: "Chiến thắng Điện Biên Phủ - Đóng góp quan trọng trong công tác tham mưu" },
    { year: "1975", event: "Giải phóng miền Nam - Thống nhất đất nước" },
    { year: "2026", event: "Kỷ niệm 80 năm truyền thống vẻ vang" },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-900 via-red-800 to-red-900">
      {/* Decorative Background Elements */}
      <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-yellow-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-red-600/20 rounded-full blur-3xl"></div>
        {/* Stars decoration */}
        <Star className="absolute top-20 right-20 w-16 h-16 text-yellow-400/40 fill-yellow-400/40" />
        <Star className="absolute top-40 right-40 w-8 h-8 text-yellow-400/30 fill-yellow-400/30" />
        <Star className="absolute bottom-40 left-20 w-12 h-12 text-yellow-400/30 fill-yellow-400/30" />
      </div>

      {/* Header */}
      <header className="relative z-20 bg-gradient-to-r from-red-900/95 via-red-800/95 to-red-900/95 backdrop-blur-md shadow-2xl border-b border-yellow-500/30">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo và Title */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full bg-white/10 backdrop-blur-sm p-1 border-2 border-yellow-500/50 shadow-lg shadow-yellow-500/20">
                  <Image
                    src="/assests/Logo-Bo-Cong-An.webp"
                    alt="Logo Bộ Công An"
                    width={60}
                    height={60}
                    className="w-full h-full object-contain"
                  />
                </div>
                <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-yellow-500 rounded-full flex items-center justify-center shadow-lg">
                  <span className="text-red-900 text-xs font-bold">80</span>
                </div>
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-white tracking-wide">
                  <span className="text-yellow-400">80 NĂM</span> THAM MƯU CAND
                </h1>
                <p className="text-yellow-200/80 text-sm flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  18/4/1946 – 18/4/2026
                </p>
              </div>
            </div>

            {/* Action Button */}
            <div className="hidden md:flex items-center space-x-4">
              <button 
                onClick={() => setShowChat(true)}
                className="bg-yellow-500 hover:bg-yellow-400 text-red-900 px-6 py-3 rounded-full font-bold transition-all duration-300 flex items-center space-x-2 shadow-lg shadow-yellow-500/30 hover:shadow-yellow-500/50 hover:scale-105"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Hỏi đáp AI</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 py-16 md:py-24">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            {/* Left Content */}
            <div className="text-center md:text-left space-y-6">
              <div className="inline-block px-4 py-2 bg-yellow-500/20 backdrop-blur-sm rounded-full border border-yellow-500/30">
                <span className="text-yellow-400 font-semibold text-sm">🎉 Cuộc thi tìm hiểu truyền thống</span>
              </div>
              
              <h2 className="text-4xl md:text-6xl font-bold text-white leading-tight">
                <span className="text-yellow-400">80 Năm</span>
                <br />
                <span className="text-3xl md:text-5xl">Ngày Truyền Thống</span>
                <br />
                <span className="text-2xl md:text-4xl text-yellow-200">Lực Lượng Tham Mưu</span>
                <br />
                <span className="text-xl md:text-3xl text-white/90">Công An Nhân Dân</span>
              </h2>

              <p className="text-white/80 text-lg max-w-xl mx-auto md:mx-0">
                Hành trình 80 năm xây dựng, chiến đấu và trưởng thành của lực lượng Tham mưu Công an nhân dân Việt Nam (1946 - 2026)
              </p>

              <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start">
                <button 
                  onClick={() => setShowChat(true)}
                  className="bg-yellow-500 hover:bg-yellow-400 text-red-900 px-8 py-4 rounded-full font-bold text-lg transition-all duration-300 flex items-center justify-center space-x-2 shadow-xl shadow-yellow-500/30 hover:shadow-yellow-500/50 hover:scale-105"
                >
                  <MessageCircle className="w-6 h-6" />
                  <span>Bắt đầu tìm hiểu</span>
                </button>
                <a 
                  href="#milestones"
                  className="border-2 border-yellow-500/50 hover:border-yellow-500 text-yellow-400 hover:text-yellow-300 px-8 py-4 rounded-full font-semibold text-lg transition-all duration-300 flex items-center justify-center space-x-2 hover:bg-yellow-500/10"
                >
                  <span>Xem dấu mốc lịch sử</span>
                  <ChevronRight className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Right Content - 80 Years Badge */}
            <div className="flex justify-center md:justify-end">
              <div className="relative">
                <div className="w-64 h-64 md:w-80 md:h-80 rounded-full bg-gradient-to-br from-yellow-400 via-yellow-500 to-yellow-600 flex items-center justify-center shadow-2xl shadow-yellow-500/50 animate-pulse">
                  <div className="w-56 h-56 md:w-72 md:h-72 rounded-full bg-gradient-to-br from-red-800 to-red-900 flex flex-col items-center justify-center border-4 border-yellow-400">
                    <span className="text-yellow-400 text-7xl md:text-9xl font-bold">80</span>
                    <span className="text-yellow-400 text-2xl md:text-3xl font-bold">NĂM</span>
                    <span className="text-white text-sm md:text-base mt-2">1946 - 2026</span>
                  </div>
                </div>
                {/* Floating stars */}
                <Star className="absolute -top-4 -right-4 w-10 h-10 text-yellow-400 fill-yellow-400 animate-bounce" />
                <Star className="absolute -bottom-2 -left-2 w-8 h-8 text-yellow-400 fill-yellow-400 animate-bounce delay-100" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative z-10 py-12 bg-black/20 backdrop-blur-sm">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { icon: Calendar, value: "80", label: "Năm truyền thống", suffix: "+" },
              { icon: Users, value: "10000", label: "Cán bộ chiến sĩ", suffix: "+" },
              { icon: Award, value: "500", label: "Danh hiệu cao quý", suffix: "+" },
              { icon: Star, value: "63", label: "Tỉnh thành", suffix: "" },
            ].map((stat, index) => (
              <div key={index} className="text-center p-6 rounded-2xl bg-white/5 backdrop-blur-sm border border-white/10 hover:bg-white/10 transition-all duration-300 hover:scale-105">
                <stat.icon className="w-8 h-8 text-yellow-400 mx-auto mb-3" />
                <div className="text-3xl md:text-4xl font-bold text-white">
                  {stat.value}<span className="text-yellow-400">{stat.suffix}</span>
                </div>
                <div className="text-white/70 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Milestones Section */}
      <section id="milestones" className="relative z-10 py-16">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h3 className="text-3xl md:text-4xl font-bold text-white mb-4">
              <span className="text-yellow-400">Dấu mốc</span> Lịch sử
            </h3>
            <p className="text-white/70 max-w-2xl mx-auto">
              Những mốc son trong hành trình 80 năm xây dựng và phát triển của lực lượng Tham mưu CAND
            </p>
          </div>

          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-1/2 top-0 bottom-0 w-1 bg-gradient-to-b from-yellow-400 via-yellow-500 to-yellow-400 -translate-x-1/2 hidden md:block"></div>
            
            <div className="space-y-8">
              {milestones.map((milestone, index) => (
                <div key={index} className={`flex flex-col md:flex-row items-center gap-4 ${index % 2 === 0 ? 'md:flex-row' : 'md:flex-row-reverse'}`}>
                  <div className={`flex-1 ${index % 2 === 0 ? 'md:text-right' : 'md:text-left'}`}>
                    <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 hover:bg-white/15 transition-all duration-300">
                      <div className="text-yellow-400 text-2xl font-bold mb-2">{milestone.year}</div>
                      <p className="text-white/90">{milestone.event}</p>
                    </div>
                  </div>
                  <div className="w-12 h-12 rounded-full bg-yellow-500 flex items-center justify-center z-10 shadow-lg shadow-yellow-500/50">
                    <Star className="w-6 h-6 text-red-900 fill-red-900" />
                  </div>
                  <div className="flex-1 hidden md:block"></div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative z-10 py-16 bg-gradient-to-r from-yellow-500/20 to-yellow-600/20 backdrop-blur-sm">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-3xl md:text-4xl font-bold text-white mb-4">
            Tìm hiểu thêm với <span className="text-yellow-400">Trợ lý AI</span>
          </h3>
          <p className="text-white/80 mb-8 max-w-2xl mx-auto">
            Đặt câu hỏi và khám phá lịch sử 80 năm truyền thống vẻ vang của lực lượng Tham mưu Công an nhân dân
          </p>
          <button 
            onClick={() => setShowChat(true)}
            className="bg-yellow-500 hover:bg-yellow-400 text-red-900 px-10 py-4 rounded-full font-bold text-xl transition-all duration-300 shadow-2xl shadow-yellow-500/40 hover:shadow-yellow-500/60 hover:scale-105"
          >
            Mở Trợ lý AI
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 bg-red-950/80 backdrop-blur-sm border-t border-yellow-500/20">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-3">
              <Image
                src="/assests/Logo-Bo-Cong-An.webp"
                alt="Logo Bộ Công An"
                width={50}
                height={50}
                className="w-12 h-12 object-contain"
              />
              <div>
                <p className="text-white font-semibold">Bộ Công An Việt Nam</p>
                <p className="text-yellow-400/80 text-sm">80 năm Tham mưu CAND (1946 - 2026)</p>
              </div>
            </div>
            <div className="text-center md:text-right">
              <p className="text-white/70 text-sm">
                Cuộc thi Tìm hiểu 80 năm Ngày truyền thống
              </p>
              <p className="text-yellow-400 text-sm font-semibold">
                Lực lượng Tham mưu Công an nhân dân
              </p>
            </div>
          </div>
        </div>
      </footer>

      {/* Chat Modal */}
      {showChat && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
          <div className="w-full max-w-4xl h-[85vh] bg-white rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300 flex flex-col">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-red-800 via-red-700 to-red-800 text-white p-4 flex items-center justify-between flex-shrink-0">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-full overflow-hidden border-2 border-yellow-400/50 shadow-lg bg-white/10 p-1">
                  <Image
                    src="/assests/Logo-Bo-Cong-An.webp"
                    alt="Logo"
                    width={44}
                    height={44}
                    className="w-full h-full object-contain"
                  />
                </div>
                <div>
                  <h2 className="font-bold text-lg">Trợ lý AI - 80 năm Tham mưu CAND</h2>
                  <div className="flex items-center space-x-2">
                    <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                    <span className="text-sm text-yellow-200">Đang hoạt động</span>
                  </div>
                </div>
              </div>
              <button
                onClick={() => setShowChat(false)}
                className="p-2 hover:bg-white/20 rounded-full transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-gray-50 to-white">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%]`}>
                    {message.sender === 'bot' && (
                      <div className="flex items-start space-x-3">
                        <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 shadow-md border-2 border-red-200 bg-white p-1">
                          <Image
                            src="/assests/Logo-Bo-Cong-An.webp"
                            alt="Bot"
                            width={36}
                            height={36}
                            className="w-full h-full object-contain"
                          />
                        </div>
                        <div className="bg-white p-4 rounded-2xl rounded-tl-none shadow-md border border-gray-100">
                          <div className="text-sm text-gray-800 markdown-body prose prose-sm max-w-none">
                            <ReactMarkdown remarkPlugins={[remarkGfm]}>
                              {message.content}
                            </ReactMarkdown>
                          </div>
                          
                          {/* Footer với time và TTS button */}
                          <div className="flex items-center gap-2 mt-3 pt-3 border-t border-gray-100">
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
                                      className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-700 rounded-md transition-all"
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
                                <div className="w-20 h-20 rounded-xl overflow-hidden shadow-lg border-2 border-white hover:border-red-400 transition-all">
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
                          <div className="bg-gradient-to-r from-red-700 to-red-600 text-white p-4 rounded-2xl rounded-tr-none shadow-md">
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs text-red-200 mt-2">
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
                  <div className="flex items-start space-x-3">
                    <div className="w-10 h-10 rounded-full overflow-hidden shadow-md border-2 border-red-200 bg-white p-1">
                      <Image
                        src="/assests/Logo-Bo-Cong-An.webp"
                        alt="Bot"
                        width={36}
                        height={36}
                        className="w-full h-full object-contain"
                      />
                    </div>
                    <div className="bg-white p-4 rounded-2xl rounded-tl-none shadow-md">
                      <div className="flex space-x-2">
                        <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Suggested Questions */}
            {messages.length === 1 && (
              <div className="px-4 py-3 bg-gray-50 border-t border-gray-100 flex-shrink-0">
                <p className="text-sm text-gray-500 mb-2 font-medium">💡 Câu hỏi gợi ý:</p>
                <div className="flex flex-wrap gap-2">
                  {suggestedQuestions.map((question, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(question)}
                      className="text-left px-4 py-2 text-sm bg-white hover:bg-red-50 hover:text-red-700 rounded-full border border-gray-200 hover:border-red-300 transition-all duration-200 shadow-sm"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Image preview thumbnails */}
            {uploadedImages.length > 0 && (
              <div className="px-4 py-2 bg-gray-50 border-t border-gray-200 flex-shrink-0">
                <div className="flex flex-wrap gap-2">
                  {uploadedImages.map((image) => (
                    <div key={image.id} className="relative group w-16 h-16 rounded-lg overflow-hidden border-2 border-gray-200">
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
            <div className="p-4 border-t border-gray-200 bg-white flex-shrink-0">
              <div className="flex items-center space-x-3">
                {/* Image upload button */}
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isTyping || uploadedImages.length >= 4}
                  className="p-3 rounded-full bg-gray-100 text-gray-600 hover:bg-red-100 hover:text-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
                  placeholder="Nhập câu hỏi về 80 năm Tham mưu CAND..."
                  className="flex-1 p-3 border border-gray-200 rounded-full focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent text-sm bg-gray-50"
                  disabled={isTyping}
                />
                
                {/* Send button */}
                <button
                  onClick={handleSendMessage}
                  disabled={(!inputMessage.trim() && uploadedImages.length === 0) || isTyping}
                  className="p-3 bg-gradient-to-r from-red-700 to-red-600 hover:from-red-600 hover:to-red-500 text-white rounded-full disabled:bg-gray-300 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-red-500/30"
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
      )}

      {/* Floating Chat Button (Mobile) */}
      <button
        onClick={() => setShowChat(true)}
        className="md:hidden fixed bottom-6 right-6 z-40 w-16 h-16 bg-yellow-500 hover:bg-yellow-400 text-red-900 rounded-full shadow-2xl shadow-yellow-500/50 flex items-center justify-center transition-all duration-300 hover:scale-110"
      >
        <MessageCircle className="w-8 h-8" />
      </button>

      {/* Image Preview Modal */}
      {previewImage && (
        <div
          className="fixed inset-0 z-[60] bg-black/95 flex items-center justify-center p-4"
          onClick={() => setPreviewImage(null)}
        >
          <button
            onClick={() => setPreviewImage(null)}
            className="absolute top-4 right-4 p-3 bg-white/20 rounded-full hover:bg-white/40 transition-colors"
          >
            <X className="w-8 h-8 text-white" />
          </button>
          <img
            src={previewImage}
            alt="Full preview"
            className="max-w-full max-h-full object-contain rounded-lg shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}
