'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Send, User, FolderOpen, Book, Copy, Check, RefreshCw, Volume2, VolumeX, Pause, Play, X, ImagePlus, Home, ArrowLeft } from 'lucide-react';
import type { Message, SourceReference, ChartData, ImageData, UploadedImage } from '@/types';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/cjs/styles/prism';
import Image from 'next/image';
import PDFViewerModal from '@/components/PDFViewerModal';
import DocumentSidebar from '@/components/DocumentSidebar';
import DocumentRepository from '@/components/DocumentRepository';
import FeedbackButtons from '@/components/FeedbackButtons';
import VoiceInputButton from '@/components/VoiceInputButton';
import ChartRenderer from '@/components/ChartRenderer';
import ImageRenderer from '@/components/ImageRenderer';
import { UploadedImage as UploadedImageType } from '@/components/ImageUpload';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';

// Custom hook for typewriter effect
const useTypewriter = (text: string, speed: number = 20, enabled: boolean = true) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!enabled) {
      setDisplayedText(text);
      setIsComplete(true);
      return;
    }

    setDisplayedText('');
    setIsComplete(false);
    
    if (!text) return;

    let index = 0;
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayedText(text.slice(0, index + 1));
        index++;
      } else {
        setIsComplete(true);
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, enabled]);

  return { displayedText, isComplete };
};

// Message component with typewriter effect
interface MessageBubbleProps {
  message: Message;
  isLatest: boolean;
  conversationId: string;
  onViewSources: (sources: SourceReference[]) => void;
  onCopy: (content: string) => void;
  onCopyQA: (query: string, answer: string) => void;
  onRegenerate: (query: string) => void;
  onSpeak: (content: string) => void;
  onStopSpeaking: () => void;
  onPauseSpeaking: () => void;
  onResumeSpeaking: () => void;
  isSpeaking: boolean;
  isPaused: boolean;
  speakingMessageId: string | null;
  speechSupported: boolean;
  copiedId: string | null;
  copiedQAId: string | null;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  message,
  isLatest,
  conversationId,
  onViewSources,
  onCopy,
  onCopyQA,
  onRegenerate,
  onSpeak,
  onStopSpeaking,
  onPauseSpeaking,
  onResumeSpeaking,
  isSpeaking,
  isPaused,
  speakingMessageId,
  speechSupported,
  copiedId,
  copiedQAId
}) => {
  const shouldAnimate = message.sender === 'bot' && isLatest && message.id !== '1';
  const { displayedText, isComplete } = useTypewriter(message.content, 15, shouldAnimate);
  
  const contentToShow = shouldAnimate ? displayedText : message.content;
  const isCopied = copiedId === message.id;
  const isCopiedQA = copiedQAId === message.id;
  const isThisMessageSpeaking = speakingMessageId === message.id && isSpeaking;

  // User message with separate avatar
  if (message.sender === 'user') {
    return (
      <div className="flex justify-end items-start gap-3">
        {/* Message content */}
        <div className="max-w-[75%] md:max-w-[70%]">
          {/* Uploaded images - shown above text */}
          {message.uploadedImages && message.uploadedImages.length > 0 && (
            <div className="mb-2 flex flex-wrap gap-2 justify-end">
              {message.uploadedImages.map((img, idx) => (
                <div 
                  key={img.id || idx} 
                  className="relative w-24 h-24 rounded-xl overflow-hidden shadow-lg border-2 border-white"
                >
                  <img
                    src={img.preview || img.base64}
                    alt={`Uploaded ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          )}
          
          {/* Text bubble */}
          {message.content && (
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 shadow-lg shadow-blue-500/20">
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
            </div>
          )}
          
          {/* Footer: time and copy button */}
          <div className="flex items-center justify-end gap-2 mt-1.5 px-1">
            <span className="text-xs text-gray-400">
              {(message.timestamp instanceof Date ? message.timestamp : new Date(message.timestamp)).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
            </span>
            <button
              onClick={() => onCopy(message.content)}
              className={`flex items-center gap-1 px-2 py-0.5 text-xs rounded-md transition-all duration-200 ${
                isCopied 
                  ? 'bg-green-100 text-green-600' 
                  : 'bg-gray-100 hover:bg-gray-200 text-gray-500'
              }`}
              title="Sao chép"
            >
              {isCopied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              <span>{isCopied ? 'Đã chép' : 'Sao chép'}</span>
            </button>
          </div>
        </div>
        
        {/* User Avatar - separate */}
        <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/30">
          <User className="w-5 h-5 text-white" />
        </div>
      </div>
    );
  }

  // Bot message
  return (
    <div className="flex justify-start items-start gap-3">
      {/* Bot Avatar */}
      <div className="flex-shrink-0">
        <Image
          src="/assests/chatbot_avatar.png"
          alt="PSU ChatBot"
          width={40}
          height={40}
          className="rounded-full shadow-md"
        />
      </div>
      
      {/* Message content */}
      <div className="max-w-[85%] md:max-w-[80%] bg-white rounded-2xl rounded-tl-sm p-4 shadow-md border border-gray-100">
        <div className="text-sm markdown-body leading-relaxed text-gray-800">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, className, children, ...props }) {
                const match = /language-(\w+)/.exec(className || '');
                const isInline = !match && (children?.toString().indexOf('\n') === -1);
                return !isInline && match ? (
                  <SyntaxHighlighter
                    style={oneDark as Record<string, React.CSSProperties>}
                    language={match[1]}
                    PreTag="div"
                    className="rounded-lg text-xs my-2"
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={`${className} bg-gray-200 text-red-600 px-1 py-0.5 rounded text-xs`} {...props}>
                    {children}
                  </code>
                );
              },
              table({ children }) {
                return (
                  <div className="overflow-x-auto my-3">
                    <table className="min-w-full border-collapse border border-gray-300 text-xs">
                      {children}
                    </table>
                  </div>
                );
              },
              th({ children }) {
                return (
                  <th className="border border-gray-300 bg-gray-100 px-3 py-2 text-left font-semibold">
                    {children}
                  </th>
                );
              },
              td({ children }) {
                return (
                  <td className="border border-gray-300 px-3 py-2">
                    {children}
                  </td>
                );
              },
            }}
          >
            {contentToShow}
          </ReactMarkdown>
          {/* Typing cursor while streaming */}
          {shouldAnimate && !isComplete && (
            <span className="inline-block w-2 h-4 bg-red-500 animate-pulse ml-1 align-middle"></span>
          )}
        </div>

        {/* Charts */}
        {message.chartData && message.chartData.length > 0 && isComplete && (
          <div className="mt-3">
            {message.chartData.map((chart, index) => (
              <ChartRenderer key={index} chartData={chart} />
            ))}
          </div>
        )}

        {/* Images */}
        {message.images && message.images.length > 0 && isComplete && (
          <ImageRenderer images={message.images} />
        )}

        {/* Source indicator */}
        {message.sourceReferences && message.sourceReferences.length > 0 && isComplete && (
          <button
            onClick={() => onViewSources(message.sourceReferences || [])}
            className="mt-3 text-xs text-red-600 hover:text-red-700 flex items-center gap-1 bg-red-50 px-2.5 py-1.5 rounded-full transition-colors"
          >
            <Book className="w-3 h-3" />
            {message.sourceReferences.length} nguồn tham khảo
          </button>
        )}

        {/* Footer */}
        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-400">
            {(message.timestamp instanceof Date ? message.timestamp : new Date(message.timestamp)).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
          </span>
          
          {message.id !== '1' && isComplete && (
            <>
              <button
                onClick={() => onCopy(message.content)}
                className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${
                  isCopied 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-500'
                }`}
                title="Sao chép câu trả lời"
              >
                {isCopied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              </button>
              
              {message.userQuery && (
                <button
                  onClick={() => onCopyQA(message.userQuery || '', message.content)}
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${
                    isCopiedQA 
                      ? 'bg-green-100 text-green-600' 
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-500'
                  }`}
                  title="Sao chép Q&A"
                >
                  {isCopiedQA ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  <span>Q&A</span>
                </button>
              )}
              
              {message.userQuery && (
                <button
                  onClick={() => onRegenerate(message.userQuery || '')}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100 hover:bg-gray-200 text-gray-500 rounded-md transition-all duration-200"
                  title="Tạo lại câu trả lời"
                >
                  <RefreshCw className="w-3 h-3" />
                </button>
              )}
              
              {/* Text-to-Speech button */}
              {speechSupported && (
                <button
                  onClick={() => {
                    if (isThisMessageSpeaking) {
                      if (isPaused) {
                        onResumeSpeaking();
                      } else {
                        onPauseSpeaking();
                      }
                    } else {
                      onSpeak(message.content);
                    }
                  }}
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${
                    isThisMessageSpeaking
                      ? 'bg-blue-100 text-blue-600'
                      : 'bg-gray-100 hover:bg-gray-200 text-gray-500'
                  }`}
                  title={isThisMessageSpeaking ? (isPaused ? 'Tiếp tục' : 'Tạm dừng') : 'Đọc câu trả lời'}
                >
                  {isThisMessageSpeaking ? (
                    isPaused ? <Play className="w-3 h-3" /> : <Pause className="w-3 h-3" />
                  ) : (
                    <Volume2 className="w-3 h-3" />
                  )}
                </button>
              )}
              
              {isThisMessageSpeaking && (
                <button
                  onClick={onStopSpeaking}
                  className="flex items-center gap-1 px-2 py-1 text-xs bg-red-100 hover:bg-red-200 text-red-600 rounded-md transition-all duration-200"
                  title="Dừng đọc"
                >
                  <VolumeX className="w-3 h-3" />
                </button>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const ChatBotPage = () => {
  const [conversationId] = useState(() => `web-chat-${Date.now()}`);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Tôi là PSU ChatBot của Trường Đại học An ninh Nhân dân. Tôi có thể giúp bạn tìm hiểu các quy định về tuyển sinh; quy chế đào tạo; quy định thi, kiểm tra, đánh giá; quy định về quản lý, giáo dục học viên và hệ thống bảo đảm chất lượng giáo dục, đào tạo của Nhà trường. Bạn cần tôi hỗ trợ gì?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [latestMessageId, setLatestMessageId] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [copiedQAMessageId, setCopiedQAMessageId] = useState<string | null>(null);
  const [uploadedImages, setUploadedImages] = useState<UploadedImageType[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Document sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSourceReferences, setCurrentSourceReferences] = useState<SourceReference[]>([]);

  // Document repository state
  const [repositoryOpen, setRepositoryOpen] = useState(false);

  // PDF Viewer state
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<{ filename: string; page?: number } | null>(null);

  // Speech Recognition (Voice to Text)
  const {
    transcript,
    isListening,
    isSupported: speechRecognitionSupported,
    error: speechRecognitionError,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition({ lang: 'vi-VN' });

  // Speech Synthesis (Text to Voice)
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
  const {
    speak,
    stop: stopSpeaking,
    pause: pauseSpeaking,
    resume: resumeSpeaking,
    isSpeaking,
    isPaused,
    isSupported: speechSynthesisSupported,
    error: speechSynthesisError
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

  const handleOpenDocument = (filename: string, page?: number) => {
    setSelectedDocument({ filename, page });
    setPdfViewerOpen(true);
  };

  const handleCloseDocument = () => {
    setPdfViewerOpen(false);
    setSelectedDocument(null);
  };

  const handleClearSources = () => {
    setCurrentSourceReferences([]);
  };

  // Handle text-to-speech for a message
  const handleSpeak = useCallback((content: string, messageId: string) => {
    setSpeakingMessageId(messageId);
    speak(content);
  }, [speak]);

  const handleStopSpeaking = useCallback(() => {
    stopSpeaking();
    setSpeakingMessageId(null);
  }, [stopSpeaking]);

  // Copy message to clipboard
  const handleCopyMessage = useCallback(async (content: string, messageId: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedMessageId(messageId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }, []);

  // Copy Q&A (question + answer) to clipboard
  const handleCopyQA = useCallback(async (query: string, answer: string, messageId: string) => {
    try {
      const qaText = `**Câu hỏi:** ${query}\n\n**Trả lời:** ${answer}`;
      await navigator.clipboard.writeText(qaText);
      setCopiedQAMessageId(messageId);
      setTimeout(() => setCopiedQAMessageId(null), 2000);
    } catch (err) {
      console.error('Failed to copy Q&A:', err);
    }
  }, []);

  // View sources in sidebar
  const handleViewSources = useCallback((sources: SourceReference[]) => {
    setCurrentSourceReferences(sources);
    setSidebarOpen(true);
  }, []);

  const handleSendMessage = async (messageToSend?: string) => {
    const textToSend = messageToSend || inputMessage;
    if (!textToSend.trim() && uploadedImages.length === 0) return;

    const currentQuery = textToSend; // Store before clearing
    const currentImages = [...uploadedImages]; // Store before clearing

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: textToSend,
      sender: 'user',
      timestamp: new Date(),
      uploadedImages: currentImages.length > 0 ? currentImages : undefined
    };

    setMessages(prev => [...prev, userMessage]);
    if (!messageToSend) setInputMessage('');
    setUploadedImages([]); // Clear uploaded images after sending
    setIsTyping(true);

    try {
      const response = await fetch('/api/chat', {
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
        const allSourceReferences: SourceReference[] = data.source_references || [];
        
        // Limit to top 5 most relevant sources (sorted by relevance_score)
        const sourceReferences: SourceReference[] = allSourceReferences
          .sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0))
          .slice(0, 5);

        // Extract chunk IDs for feedback
        const chunkIds: number[] = sourceReferences
          .map((ref: SourceReference) => parseInt(ref.chunk_id, 10))
          .filter((id: number) => !isNaN(id));

        // Update current source references for sidebar
        if (sourceReferences.length > 0) {
          setCurrentSourceReferences(sourceReferences);
          setSidebarOpen(true); // Auto-open sidebar when sources are available
        }

        const newMessageId = (Date.now() + 1).toString();
        const botMessage: Message = {
          id: newMessageId,
          role: 'assistant',
          content: data.response || data.answer || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
          sender: 'bot',
          timestamp: new Date(),
          sourceReferences: sourceReferences,
          confidence: data.confidence,
          userQuery: currentQuery, // Store for feedback
          chunkIds: chunkIds, // Store for feedback
          chartData: data.chart_data || [], // Charts from backend
          images: data.images || [] // Images from backend
        };
        setMessages(prev => [...prev, botMessage]);
        setLatestMessageId(newMessageId);
      } else {
        throw new Error('API call failed');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      const newErrorId = (Date.now() + 1).toString();
      const errorMessage: Message = {
        id: newErrorId,
        role: 'assistant',
        content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      setLatestMessageId(newErrorId);
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
    <div 
      className="min-h-screen bg-cover bg-center bg-fixed"
      style={{ backgroundImage: "url('/assests/background_image.jpg')" }}
    >
      {/* Header */}
      <header className="bg-white shadow-md border-b-4 border-red-600 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 md:h-20">
            <div className="flex items-center space-x-3 md:space-x-4">
              {/* Back to Home button */}
              <Link
                href="/"
                className="flex items-center gap-1 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium"
                title="Về trang chủ"
              >
                <ArrowLeft className="w-4 h-4" />
                <Home className="w-4 h-4" />
              </Link>
              
              <Image
                src="/assests/logo-main.png"
                alt="Logo Trường Đại học An ninh Nhân dân"
                width={50}
                height={50}
                className="object-contain"
              />
              <div>
                <h1 className="text-lg md:text-xl font-bold text-gray-900">
                  PSU ChatBot
                </h1>
                <p className="text-xs md:text-sm text-gray-600 hidden sm:block">Hỗ trợ tư vấn 24/7</p>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setRepositoryOpen(true)}
                className="flex items-center gap-2 px-3 py-2 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg transition-colors text-sm font-medium"
              >
                <FolderOpen className="w-4 h-4" />
                <span className="hidden sm:inline">Tài liệu</span>
              </button>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="flex items-center gap-2 px-3 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors text-sm font-medium relative"
              >
                <Book className="w-4 h-4" />
                <span className="hidden sm:inline">Nguồn</span>
                {currentSourceReferences.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {currentSourceReferences.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Adjusted for sidebar */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'mr-0 md:mr-96' : 'mr-0'}`}>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4 md:py-8">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 h-[calc(100vh-140px)] md:h-[calc(100vh-160px)] flex flex-col">
            {/* Chat Header */}
            <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-4 md:p-6 rounded-t-xl">
              <div className="flex items-center space-x-3">
                <div className="relative">
                  <Image
                    src="/assests/chatbot_avatar.png"
                    alt="PSU ChatBot Avatar"
                    width={40}
                    height={40}
                    className="rounded-full border-2 border-white"
                  />
                  <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
                </div>
                <div>
                  <h2 className="text-base md:text-lg font-semibold">PSU ChatBot</h2>
                  <p className="text-red-100 text-xs md:text-sm">Đang hoạt động</p>
                </div>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-4 md:space-y-6">
              {messages.map((message, index) => (
                <MessageBubble
                  key={message.id}
                  message={message}
                  isLatest={message.id === latestMessageId}
                  conversationId={conversationId}
                  onViewSources={handleViewSources}
                  onCopy={(content) => handleCopyMessage(content, message.id)}
                  onCopyQA={(query, answer) => handleCopyQA(query, answer, message.id)}
                  onRegenerate={(query) => handleSendMessage(query)}
                  onSpeak={(content) => handleSpeak(content, message.id)}
                  onStopSpeaking={handleStopSpeaking}
                  onPauseSpeaking={pauseSpeaking}
                  onResumeSpeaking={resumeSpeaking}
                  isSpeaking={isSpeaking}
                  isPaused={isPaused}
                  speakingMessageId={speakingMessageId}
                  speechSupported={speechSynthesisSupported}
                  copiedId={copiedMessageId}
                  copiedQAId={copiedQAMessageId}
                />
              ))}

              {isTyping && (
                <div className="flex justify-start">
                  <div className="bg-gray-100 text-gray-800 rounded-2xl p-3 md:p-4 max-w-[85%] shadow-sm">
                    <div className="flex items-center space-x-3">
                      <Image
                        src="/assests/chatbot_avatar.png"
                        alt="PSU ChatBot"
                        width={28}
                        height={28}
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
            <div className="p-3 md:p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
              {/* Voice recognition error message */}
              {speechRecognitionError && (
                <div className="mb-2 px-3 py-2 bg-red-50 border border-red-200 rounded-lg text-red-600 text-xs">
                  {speechRecognitionError}
                </div>
              )}
              {/* Voice recognition listening indicator */}
              {isListening && (
                <div className="mb-2 px-3 py-2 bg-blue-50 border border-blue-200 rounded-lg text-blue-600 text-xs flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                  Đang lắng nghe... Nói câu hỏi của bạn
                  {transcript && <span className="text-gray-500">({transcript})</span>}
                </div>
              )}
              {/* Image Upload Preview - Show previews above input when there are images */}
              {uploadedImages.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2 p-2 bg-gray-50 rounded-lg border border-gray-200">
                  {uploadedImages.map((image) => (
                    <div key={image.id} className="relative group">
                      <img
                        src={image.preview}
                        alt={image.name}
                        className="w-16 h-16 object-cover rounded-lg border border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={() => setUploadedImages(prev => prev.filter(img => img.id !== image.id))}
                        className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                        title="Xóa ảnh"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  ))}
                  {/* Add more button if under limit */}
                  {uploadedImages.length < 4 && (
                    <label className="w-16 h-16 rounded-lg border-2 border-dashed border-gray-300 hover:border-blue-400 flex items-center justify-center text-gray-400 hover:text-blue-500 transition-colors cursor-pointer">
                      <input
                        type="file"
                        accept="image/*"
                        multiple
                        className="hidden"
                        onChange={async (e) => {
                          const files = e.target.files;
                          if (!files) return;
                          const remainingSlots = 4 - uploadedImages.length;
                          const filesToProcess = Array.from(files).slice(0, remainingSlots);
                          
                          for (const file of filesToProcess) {
                            if (!file.type.startsWith('image/')) continue;
                            const reader = new FileReader();
                            reader.onload = () => {
                              const base64 = reader.result as string;
                              setUploadedImages(prev => [...prev, {
                                id: `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                                name: file.name,
                                mimeType: file.type,
                                preview: URL.createObjectURL(file),
                                base64
                              }]);
                            };
                            reader.readAsDataURL(file);
                          }
                          e.target.value = '';
                        }}
                      />
                      <ImagePlus className="w-5 h-5" />
                    </label>
                  )}
                  <span className="flex items-center text-xs text-gray-500 ml-2">
                    {uploadedImages.length}/4 ảnh
                  </span>
                </div>
              )}
              <div className="flex items-center gap-2 md:gap-3">
                {/* Image Upload Button - Only show when no images */}
                {uploadedImages.length === 0 && (
                  <label className="flex items-center justify-center w-10 h-10 md:w-11 md:h-11 rounded-xl bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors cursor-pointer flex-shrink-0">
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      className="hidden"
                      disabled={isTyping}
                      onChange={async (e) => {
                        const files = e.target.files;
                        if (!files) return;
                        const filesToProcess = Array.from(files).slice(0, 4);
                        
                        for (const file of filesToProcess) {
                          if (!file.type.startsWith('image/')) continue;
                          const reader = new FileReader();
                          reader.onload = () => {
                            const base64 = reader.result as string;
                            setUploadedImages(prev => [...prev, {
                              id: `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                              name: file.name,
                              mimeType: file.type,
                              preview: URL.createObjectURL(file),
                              base64
                            }]);
                          };
                          reader.readAsDataURL(file);
                        }
                        e.target.value = '';
                      }}
                    />
                    <ImagePlus className="w-5 h-5" />
                  </label>
                )}
                {/* Voice Input Button */}
                {speechRecognitionSupported && (
                  <div className="flex-shrink-0">
                    <VoiceInputButton
                      isListening={isListening}
                      isSupported={speechRecognitionSupported}
                      onStart={startListening}
                      onStop={stopListening}
                      disabled={isTyping}
                    />
                  </div>
                )}
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && handleSendMessage()}
                  onPaste={async (e) => {
                    const items = e.clipboardData?.items;
                    if (!items) return;
                    
                    const imageItems = Array.from(items).filter(item => item.type.startsWith('image/'));
                    if (imageItems.length === 0) return;
                    
                    e.preventDefault(); // Prevent pasting image as text
                    
                    const remainingSlots = 4 - uploadedImages.length;
                    if (remainingSlots <= 0) return;
                    
                    for (const item of imageItems.slice(0, remainingSlots)) {
                      const file = item.getAsFile();
                      if (!file) continue;
                      
                      const reader = new FileReader();
                      reader.onload = () => {
                        const base64 = reader.result as string;
                        setUploadedImages(prev => [...prev, {
                          id: `img-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
                          name: file.name || `pasted-image-${Date.now()}.png`,
                          mimeType: file.type,
                          preview: URL.createObjectURL(file),
                          base64
                        }]);
                      };
                      reader.readAsDataURL(file);
                    }
                  }}
                  placeholder={isListening ? "Đang lắng nghe..." : uploadedImages.length > 0 ? "Mô tả hoặc hỏi về ảnh..." : "Nhập câu hỏi hoặc dán ảnh (Ctrl+V)..."}
                  className="flex-1 min-w-0 h-10 md:h-11 px-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  disabled={isTyping || isListening}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={(!inputMessage.trim() && uploadedImages.length === 0) || isTyping}
                  className="flex-shrink-0 w-10 h-10 md:w-11 md:h-11 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 disabled:bg-gray-400 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center shadow-sm hover:shadow-md"
                >
                  <Send className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Document Sidebar */}
      <DocumentSidebar
        sourceReferences={currentSourceReferences}
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onOpenDocument={handleOpenDocument}
        onClear={handleClearSources}
      />

      {/* Document Repository Modal */}
      <DocumentRepository
        isOpen={repositoryOpen}
        onClose={() => setRepositoryOpen(false)}
        onOpenDocument={(filename) => handleOpenDocument(filename)}
      />

      {/* PDF Viewer Modal */}
      {selectedDocument && (
        <PDFViewerModal
          isOpen={pdfViewerOpen}
          onClose={handleCloseDocument}
          filename={selectedDocument.filename}
          initialPage={selectedDocument.page}
        />
      )}
    </div>
  );
};

export default ChatBotPage;
