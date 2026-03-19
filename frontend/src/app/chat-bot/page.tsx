'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { Send, User, FolderOpen, Book, Copy, Check, RefreshCw, Volume2, VolumeX, Pause, Play, X, ImagePlus, Home, ArrowLeft, ZoomIn, ZoomOut, RotateCw, Download, Maximize2, ChevronUp, ChevronDown, Sparkles } from 'lucide-react';
import type { Message, SourceReference, ChartData, ImageData, FileAttachment, PerformanceMetrics } from '@/types';
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
import type { UploadedImage as UploadedImageType } from '@/components/ImageUpload';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useSpeechSynthesis } from '@/hooks/useSpeechSynthesis';
import { MobileSourceDrawer } from '@/components/chat/MobileUI';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const SOURCE_REFERENCE_DISPLAY_THRESHOLD = 0.65;

const filterVisibleSourceReferences = (sourceReferences: SourceReference[] = []) =>
  sourceReferences.filter((ref) => (ref.relevance_score || 0) >= SOURCE_REFERENCE_DISPLAY_THRESHOLD);

const rankVisibleSourceReferences = (sourceReferences: SourceReference[] = [], limit = 5) =>
  filterVisibleSourceReferences(sourceReferences)
    .sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0))
    .slice(0, limit);

const FALLBACK_QUESTIONS = {
  vi: [
    'Điều kiện tuyển sinh và các phương thức xét tuyển của trường là gì?',
    'Chỉ tiêu tuyển sinh theo từng ngành hoặc nhóm ngành hiện nay như thế nào?',
    'Hồ sơ sơ tuyển hoặc hồ sơ đăng ký xét tuyển cần chuẩn bị những gì?',
    'Mốc thời gian nộp hồ sơ, sơ tuyển và nhập học diễn ra khi nào?',
    'Tiêu chuẩn sức khỏe, độ tuổi và đối tượng tuyển sinh được quy định ra sao?'
  ],
  en: [
    'What are the admission requirements and admission methods?',
    'What are the admission quotas by major or program?',
    'Which application or pre-qualification documents are required?',
    'What is the timeline for application, pre-qualification, and enrollment?',
    'What are the health, age, and applicant eligibility standards?'
  ]
} as const;

// Gemini-style Processing Indicator - Shows REAL backend processing status
interface ProcessingIndicatorProps {
  currentStatus: string;
  completedSteps: string[];
}

const ProcessingIndicator: React.FC<ProcessingIndicatorProps> = ({ currentStatus, completedSteps }) => {
  const [isExpanded, setIsExpanded] = React.useState(true);

  // Map status messages to step info with descriptions
  const getStepInfo = (status: string) => {
    if (status.includes('tìm kiếm') || status.includes('search')) {
      return {
        title: 'Đang tìm kiếm tài liệu liên quan',
        description: 'Tôi đang tìm kiếm trong cơ sở dữ liệu tài liệu để tìm thông tin phù hợp với câu hỏi của bạn...'
      };
    }
    if (status.includes('phân tích') || status.includes('context') || status.includes('ngữ cảnh')) {
      return {
        title: 'Đang phân tích ngữ cảnh',
        description: 'Đang phân tích và so sánh các tài liệu tìm được với ngữ cảnh câu hỏi để đảm bảo độ chính xác...'
      };
    }
    if (status.includes('soạn') || status.includes('tạo') || status.includes('generate') || status.includes('answer')) {
      return {
        title: 'Đang soạn câu trả lời',
        description: 'Đang tổng hợp thông tin và soạn câu trả lời chi tiết, dễ hiểu cho câu hỏi của bạn...'
      };
    }
    // Default
    return {
      title: currentStatus || 'Đang xử lý...',
      description: 'Hệ thống đang xử lý yêu cầu của bạn...'
    };
  };

  const allSteps = [
    { key: 'search', title: 'Tìm kiếm tài liệu' },
    { key: 'analyze', title: 'Phân tích ngữ cảnh' },
    { key: 'generate', title: 'Soạn câu trả lời' },
  ];

  // Determine which step is active based on current status
  const getCurrentStepIndex = () => {
    if (currentStatus.includes('tìm kiếm') || currentStatus.includes('search')) return 0;
    if (currentStatus.includes('phân tích') || currentStatus.includes('context')) return 1;
    if (currentStatus.includes('soạn') || currentStatus.includes('tạo') || currentStatus.includes('generate')) return 2;
    return 0;
  };

  const currentInfo = getStepInfo(currentStatus);
  const activeStepIdx = getCurrentStepIndex();
  const isCompletedStep = (stepKey: string, idx: number) => {
    const completed = completedSteps.some((step) => {
      const normalized = step.toLowerCase();
      if (stepKey === 'search') return normalized.includes('tìm kiếm') || normalized.includes('search');
      if (stepKey === 'analyze') return normalized.includes('phân tích') || normalized.includes('context') || normalized.includes('ngữ cảnh');
      return normalized.includes('soạn') || normalized.includes('tạo') || normalized.includes('generate') || normalized.includes('answer');
    });

    return completed || idx < activeStepIdx;
  };

  return (
    <div className="w-full">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 transition-colors mb-2 group"
      >
        <Sparkles className="w-4 h-4 text-amber-500 animate-pulse" />
        <span className="font-medium">Hiện tiến trình tư duy</span>
        {isExpanded ? (
          <ChevronUp className="w-4 h-4 transition-transform group-hover:scale-110" />
        ) : (
          <ChevronDown className="w-4 h-4 transition-transform group-hover:scale-110" />
        )}
      </button>

      {/* Thinking Content */}
      {isExpanded && (
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-4 border border-gray-200 animate-fadeIn">
          {/* Step Title */}
          <h4 className="text-sm font-semibold text-gray-800 mb-2 flex items-center gap-2">
            <span className="inline-block w-2 h-2 bg-amber-500 rounded-full animate-pulse"></span>
            {currentInfo.title}
          </h4>

          {/* Step Description */}
          <p className="text-sm text-gray-600 leading-relaxed">
            {currentInfo.description}
          </p>

          {/* Progress Steps */}
          <div className="flex items-center gap-2 mt-3">
            {allSteps.map((step, idx) => (
              <div key={step.key} className="flex items-center gap-1">
                {(() => {
                  const isCompleted = isCompletedStep(step.key, idx);
                  const isActive = idx === activeStepIdx;
                  return (
                    <>
                      <div
                        className={`w-2 h-2 rounded-full transition-all duration-300 ${isCompleted
                          ? 'bg-green-500'
                          : isActive
                            ? 'bg-amber-500 animate-pulse'
                            : 'bg-gray-300'
                          }`}
                      />
                      <span className={`text-xs ${isCompleted
                        ? 'text-green-600'
                        : isActive
                          ? 'text-amber-600 font-medium'
                          : 'text-gray-400'
                        }`}>
                        {step.title}
                      </span>
                      {idx < allSteps.length - 1 && (
                        <span className="text-gray-300 mx-1">→</span>
                      )}
                    </>
                  );
                })()}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Image Modal Component for viewing images in detail
interface ImageModalProps {
  isOpen: boolean;
  onClose: () => void;
  imageSrc: string;
  imageAlt?: string;
}

const ImageModal: React.FC<ImageModalProps> = ({ isOpen, onClose, imageSrc, imageAlt = 'Image' }) => {
  const [scale, setScale] = useState(1);
  const [rotation, setRotation] = useState(0);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  useEffect(() => {
    if (isOpen) {
      setScale(1);
      setRotation(0);
      setPosition({ x: 0, y: 0 });
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;
      if (e.key === 'Escape') onClose();
      if (e.key === '+' || e.key === '=') setScale(s => Math.min(s + 0.25, 5));
      if (e.key === '-') setScale(s => Math.max(s - 0.25, 0.25));
      if (e.key === 'r') setRotation(r => (r + 90) % 360);
      if (e.key === '0') { setScale(1); setRotation(0); setPosition({ x: 0, y: 0 }); }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? -0.1 : 0.1;
    setScale(s => Math.min(Math.max(s + delta, 0.25), 5));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (scale > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `image-${Date.now()}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-sm flex items-center justify-center"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      {/* Control Bar */}
      <div className="absolute top-4 left-1/2 -translate-x-1/2 bg-white/10 backdrop-blur-md rounded-full px-4 py-2 flex items-center gap-3 z-10">
        <button
          onClick={() => setScale(s => Math.max(s - 0.25, 0.25))}
          className="p-2 rounded-full hover:bg-white/20 text-white transition-colors"
          title="Thu nhỏ (-)"
        >
          <ZoomOut className="w-5 h-5" />
        </button>
        <span className="text-white text-sm min-w-[60px] text-center font-medium">
          {Math.round(scale * 100)}%
        </span>
        <button
          onClick={() => setScale(s => Math.min(s + 0.25, 5))}
          className="p-2 rounded-full hover:bg-white/20 text-white transition-colors"
          title="Phóng to (+)"
        >
          <ZoomIn className="w-5 h-5" />
        </button>
        <div className="w-px h-6 bg-white/30" />
        <button
          onClick={() => setRotation(r => (r + 90) % 360)}
          className="p-2 rounded-full hover:bg-white/20 text-white transition-colors"
          title="Xoay (R)"
        >
          <RotateCw className="w-5 h-5" />
        </button>
        <button
          onClick={() => { setScale(1); setRotation(0); setPosition({ x: 0, y: 0 }); }}
          className="p-2 rounded-full hover:bg-white/20 text-white transition-colors"
          title="Đặt lại (0)"
        >
          <Maximize2 className="w-5 h-5" />
        </button>
        <div className="w-px h-6 bg-white/30" />
        <button
          onClick={handleDownload}
          className="p-2 rounded-full hover:bg-white/20 text-white transition-colors"
          title="Tải xuống"
        >
          <Download className="w-5 h-5" />
        </button>
      </div>

      {/* Close Button */}
      <button
        onClick={onClose}
        className="absolute top-4 right-4 p-2 rounded-full bg-white/10 hover:bg-white/20 text-white transition-colors z-10"
        title="Đóng (Esc)"
      >
        <X className="w-6 h-6" />
      </button>

      {/* Image Container */}
      <div
        className="relative overflow-hidden w-full h-full flex items-center justify-center"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        style={{ cursor: scale > 1 ? (isDragging ? 'grabbing' : 'grab') : 'default' }}
      >
        <Image
          src={imageSrc}
          alt={imageAlt}
          width={1600}
          height={1200}
          unoptimized
          className="max-w-[90vw] max-h-[85vh] object-contain select-none transition-transform duration-200"
          style={{
            transform: `translate(${position.x}px, ${position.y}px) scale(${scale}) rotate(${rotation}deg)`,
          }}
          draggable={false}
        />
      </div>

      {/* Keyboard Shortcuts Hint */}
      <div className="absolute bottom-4 left-1/2 -translate-x-1/2 text-white/60 text-xs">
        <span className="bg-white/10 px-2 py-1 rounded">Cuộn chuột</span> zoom •
        <span className="bg-white/10 px-2 py-1 rounded mx-1">R</span> xoay •
        <span className="bg-white/10 px-2 py-1 rounded">Esc</span> đóng •
        <span className="bg-white/10 px-2 py-1 rounded ml-1">Kéo</span> di chuyển khi phóng to
      </div>
    </div>
  );
};

const TYPEWRITER_MAX_ANIMATED_CHARS = 120;

// Custom hook for typewriter effect - optimized to prevent flickering
const useTypewriter = (
  text: string,
  speed: number = 5,
  enabled: boolean = true,
  maxAnimatedChars: number = TYPEWRITER_MAX_ANIMATED_CHARS
) => {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);
  const textRef = useRef(text);

  useEffect(() => {
    if (!enabled) {
      setDisplayedText(text);
      setIsComplete(true);
      return;
    }

    // Only reset if text actually changed significantly (not just appending)
    if (text !== textRef.current) {
      const isAppending = text.startsWith(textRef.current);
      if (!isAppending) {
        setDisplayedText('');
        setIsComplete(false);
      }
      textRef.current = text;
    }

    if (!text) return;

    const animateTarget = Math.min(text.length, maxAnimatedChars);

    // For long answers, animate only the opening segment then reveal all text.
    if (text.length > maxAnimatedChars && displayedText.length >= animateTarget) {
      if (displayedText !== text) {
        setDisplayedText(text);
      }
      setIsComplete(true);
      return;
    }

    // If already showing all text, just update
    if (displayedText === text) {
      setIsComplete(true);
      return;
    }

    let index = displayedText.length;
    const timer = setInterval(() => {
      if (index < animateTarget) {
        // Update multiple characters at once for smoother rendering
        const charsToAdd = Math.min(3, animateTarget - index);
        setDisplayedText(text.slice(0, index + charsToAdd));
        index += charsToAdd;
      } else {
        if (text.length > maxAnimatedChars) {
          setDisplayedText(text);
        }
        setIsComplete(true);
        clearInterval(timer);
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, enabled, displayedText, maxAnimatedChars]);

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
  onSendFollowUp: (question: string) => void;
  processingStatus: string; // Real backend processing status
  completedSteps: string[]; // Completed processing steps
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
  copiedQAId,
  onSendFollowUp,
  processingStatus,
  completedSteps
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  // Typewriter animation - use reasonable speed (5ms) and add 3 chars at a time
  const shouldAnimate = message.sender === 'bot' && isLatest && message.id !== '1';
  const { displayedText, isComplete } = useTypewriter(message.content, 5, shouldAnimate);

  const contentToShow = shouldAnimate ? displayedText : message.content;
  const isCopied = copiedId === message.id;
  const isCopiedQA = copiedQAId === message.id;
  const isThisMessageSpeaking = speakingMessageId === message.id && isSpeaking;
  const visibleSourceReferences = filterVisibleSourceReferences(message.sourceReferences);

  // Parse follow-up questions from content
  const parseFollowUpQuestions = (content: string): { mainContent: string; followUpQuestions: string[] } => {
    // Support multiple formats: with/without markdown bold markers
    const markers = [
      '**--- CÁC CÂU HỎI LIÊN QUAN ---**',
      '--- CÁC CÂU HỎI LIÊN QUAN ---',
      '**--- RELATED QUESTIONS ---**',
      '--- RELATED QUESTIONS ---'
    ];

    for (const marker of markers) {
      if (content.includes(marker)) {
        const parts = content.split(marker);
        const mainContent = parts[0].trim();
        const followUpSection = parts[1]?.trim() || '';

        // Extract questions (lines that end with '?' or '?**')
        const questions = followUpSection
          .split('\n')
          .map(line => line.trim())
          // Remove bullet points, dashes, and markdown bold markers
          .map(line => line.replace(/^[-*]\s*/, '').replace(/\*\*/g, '').trim())
          .filter(line => line.endsWith('?') && line.length > 5);

        return { mainContent, followUpQuestions: questions };
      }
    }

    return { mainContent: content, followUpQuestions: [] };
  };

  const parsedFollowUps = parseFollowUpQuestions(contentToShow);
  const followUpQuestions =
    message.followUpQuestions && message.followUpQuestions.length > 0
      ? message.followUpQuestions
      : parsedFollowUps.followUpQuestions;
  const mainContent =
    message.followUpQuestions && message.followUpQuestions.length > 0
      ? contentToShow
      : parsedFollowUps.mainContent;

  // User message with separate avatar
  if (message.sender === 'user') {
    return (
      <>
        <div className="flex justify-end items-start gap-2 sm:gap-3 animate-message-right group/msg">
          {/* Message content */}
          <div className="max-w-[85%] sm:max-w-[75%] md:max-w-[70%]">
            {/* Uploaded images - shown above text */}
            {message.uploadedImages && message.uploadedImages.length > 0 && (
              <div className="mb-2 flex flex-wrap gap-1.5 sm:gap-2 justify-end">
                {message.uploadedImages.map((img, idx) => (
                  <div
                    key={img.id || idx}
                    className="relative group cursor-pointer"
                    onClick={() => setSelectedImage(img.preview || img.base64 || '')}
                  >
                    <div className="relative w-20 h-20 sm:w-24 sm:h-24 md:w-28 md:h-28 rounded-lg sm:rounded-xl overflow-hidden shadow-lg border border-white sm:border-2 hover:border-blue-400 transition-all duration-200 hover:shadow-xl">
                      <Image
                        src={img.preview || img.base64}
                        alt={`Uploaded ${idx + 1}`}
                        fill
                        unoptimized
                        sizes="(max-width: 640px) 80px, (max-width: 768px) 96px, 112px"
                        className="object-cover transition-transform duration-200 group-hover:scale-105"
                      />
                    </div>
                    {/* Zoom overlay */}
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 rounded-xl transition-all duration-200 flex items-center justify-center">
                      <ZoomIn className="w-6 h-6 text-white opacity-0 group-hover:opacity-100 transition-opacity duration-200 drop-shadow-lg" />
                    </div>
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
              <span className="text-xs text-gray-400 opacity-0 group-hover/msg:opacity-100 transition-opacity duration-200">
                {(message.timestamp instanceof Date ? message.timestamp : new Date(message.timestamp)).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
              </span>
              <button
                onClick={() => onCopy(message.content)}
                className={`flex items-center gap-1 px-2 py-0.5 text-xs rounded-md transition-all duration-200 ${isCopied
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
          <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-gradient-to-br from-blue-500 to-blue-600 flex items-center justify-center shadow-md sm:shadow-lg shadow-blue-500/30">
            <User className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </div>
        </div>

        {/* Image Modal for User Messages */}
        <ImageModal
          isOpen={!!selectedImage}
          onClose={() => setSelectedImage(null)}
          imageSrc={selectedImage || ''}
          imageAlt="Uploaded image"
        />
      </>
    );
  }

  // Bot message
  return (
    <div className="flex justify-start items-start gap-2 sm:gap-3 animate-message-left group/msg">
      {/* Bot Avatar with Gold Ring Pulse */}
      <div className="flex-shrink-0 relative">
        <div className={`rounded-full ${isLatest && !contentToShow ? 'animate-gold-ring' : ''}`}>
          <Image
            src="/assests/chatbot_avatar.png"
            alt="PSU ChatBot"
            width={32}
            height={32}
            className="w-8 h-8 sm:w-10 sm:h-10 rounded-full shadow-sm sm:shadow-md"
          />
        </div>
        <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full border border-white online-pulse"></div>
      </div>

      {/* Message content */}
      <div className="max-w-[90%] sm:max-w-[85%] md:max-w-[80%] bg-white rounded-xl sm:rounded-2xl rounded-tl-sm p-3 sm:p-4 shadow-sm sm:shadow-md border border-gray-100">
        <div className="text-sm markdown-body leading-relaxed text-gray-800">
          {/* Show Processing Indicator when content is empty (streaming just started) */}
          {!mainContent && isLatest && (
            <ProcessingIndicator currentStatus={processingStatus} completedSteps={completedSteps} />
          )}

          {/* Render markdown content when available */}
          {mainContent && (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ className, children, ...props }) {
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
              {mainContent}
            </ReactMarkdown>
          )}

          {/* Typing cursor while streaming */}
          {shouldAnimate && !isComplete && mainContent && (
            <span className="inline-block w-2 h-4 bg-red-500 animate-pulse ml-1 align-middle"></span>
          )}
        </div>

        {/* Follow-up Questions Section */}
        {followUpQuestions.length > 0 && isComplete && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-xs font-bold text-indigo-900 mb-3 flex items-center gap-2">
              💡 Câu hỏi liên quan
            </h4>
            <div className="space-y-2">
              {followUpQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => onSendFollowUp(question)}
                  className="w-full text-left p-3 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-lg border border-blue-200 hover:border-indigo-300 text-gray-700 hover:text-indigo-700 transition-all duration-300 shadow-sm hover:shadow-md hover:scale-[1.02] transform group"
                >
                  <div className="flex items-start gap-3">
                    <span className="text-blue-500 text-sm mt-0.5 group-hover:scale-110 transition-transform">💬</span>
                    <span className="font-medium leading-relaxed text-sm flex-1">{question}</span>
                    <Send className="w-4 h-4 text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                  </div>
                </button>
              ))}
            </div>
          </div>
        )}

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

        {/* File Attachments */}
        {message.attachments && message.attachments.length > 0 && isComplete && (
          <div className="mt-3 space-y-2">
            {message.attachments.map((attachment, idx) => (
              <a
                key={idx}
                href={`${API_BASE_URL}${attachment.download_url}`}
                download
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 px-4 py-3 bg-gradient-to-r from-blue-50 to-indigo-50 hover:from-blue-100 hover:to-indigo-100 rounded-lg border border-blue-200 hover:border-blue-300 transition-all duration-200 group"
              >
                <div className="flex-shrink-0 w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                  <FolderOpen className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-blue-900 group-hover:text-blue-700 truncate">
                    {attachment.file_name}
                  </p>
                  {attachment.description && (
                    <p className="text-xs text-blue-600 mt-0.5 truncate">
                      {attachment.description}
                    </p>
                  )}
                  {attachment.file_size && (
                    <p className="text-xs text-gray-500 mt-0.5">
                      {(attachment.file_size / 1024).toFixed(1)} KB
                    </p>
                  )}
                </div>
                <Download className="w-4 h-4 text-blue-600 group-hover:text-blue-700 flex-shrink-0" />
              </a>
            ))}
          </div>
        )}

        {/* Source indicator */}
        {visibleSourceReferences.length > 0 && isComplete && (
          <button
            onClick={() => onViewSources(visibleSourceReferences)}
            className="mt-3 text-xs text-red-600 hover:text-red-700 flex items-center gap-1 bg-red-50 px-2.5 py-1.5 rounded-full transition-colors"
          >
            <Book className="w-3 h-3" />
            {visibleSourceReferences.length} nguồn tham khảo (≥{Math.round(SOURCE_REFERENCE_DISPLAY_THRESHOLD * 100)}%)
          </button>
        )}

        {/* Footer */}
        <div className="flex flex-wrap items-center gap-2 mt-3 pt-3 border-t border-gray-100">
          <span className="text-xs text-gray-400 opacity-0 group-hover/msg:opacity-100 transition-opacity duration-200">
            {(message.timestamp instanceof Date ? message.timestamp : new Date(message.timestamp)).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}
          </span>

          {message.id !== '1' && isComplete && (
            <>
              <button
                onClick={() => onCopy(message.content)}
                className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${isCopied
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
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${isCopiedQA
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
                  className={`flex items-center gap-1 px-2 py-1 text-xs rounded-md transition-all duration-200 ${isThisMessageSpeaking
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

        {/* Feedback Buttons - Like/Dislike */}
        {message.id !== '1' && isComplete && message.userQuery && (
          <div className="mt-3 pt-3 border-t border-gray-100">
            <FeedbackButtons
              conversationId={conversationId}
              messageId={message.id}
              query={message.userQuery}
              answer={message.content}
              chunkIds={message.sourceReferences?.map((ref, idx) => idx) || []}
            />
          </div>
        )}
      </div>
    </div>
  );
};

const ChatBotPage = () => {
  const [conversationId] = useState(() => `web-chat-${Date.now()}`);
  const [language, setLanguage] = useState<'vi' | 'en'>('vi'); // Language toggle state
  const [messages, setMessages] = useState<Message[]>(() => [
    {
      id: '1',
      role: 'assistant',
      content: 'Xin chào! Tôi là PSU ChatBot của Trường Đại học An ninh Nhân dân. Tôi chỉ hỗ trợ tra cứu thông tin tuyển sinh chính thức như điều kiện tuyển sinh, phương thức xét tuyển, chỉ tiêu, hồ sơ, lịch tuyển sinh và thủ tục nhập học. Bạn cần tôi tra cứu nội dung tuyển sinh nào?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [processingStatus, setProcessingStatus] = useState<string>(''); // Real backend status
  const [completedSteps, setCompletedSteps] = useState<string[]>([]); // Track completed steps
  const [latestMessageId, setLatestMessageId] = useState<string | null>(null);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [copiedQAMessageId, setCopiedQAMessageId] = useState<string | null>(null);
  const [uploadedImages, setUploadedImages] = useState<UploadedImageType[]>([]);
  const [previewImage, setPreviewImage] = useState<string | null>(null); // For image preview modal
  const [showDisclaimer, setShowDisclaimer] = useState(false); // Toggle for disclaimer
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Document sidebar state
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentSourceReferences, setCurrentSourceReferences] = useState<SourceReference[]>([]);

  // Document repository state
  const [repositoryOpen, setRepositoryOpen] = useState(false);
  // PDF Viewer state
  const [pdfViewerOpen, setPdfViewerOpen] = useState(false);
  const [selectedDocument, setSelectedDocument] = useState<{ filename: string; page?: number } | null>(null);
  const visibleCurrentSourceReferences = filterVisibleSourceReferences(currentSourceReferences);

  // Speech Recognition (Voice to Text) - dynamic language based on toggle
  const {
    transcript,
    isListening,
    isSupported: speechRecognitionSupported,
    error: speechRecognitionError,
    startListening,
    stopListening,
    resetTranscript
  } = useSpeechRecognition({ lang: language === 'vi' ? 'vi-VN' : 'en-US' });

  // Speech Synthesis (Text to Voice)
  const [speakingMessageId, setSpeakingMessageId] = useState<string | null>(null);
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
      // Replace input with transcript instead of appending to avoid duplication
      setInputMessage(transcript.trim());
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

    // Create placeholder bot message for streaming
    const newMessageId = (Date.now() + 1).toString();
    let streamedContent = '';
    let streamedSources: SourceReference[] = [];
    let streamedConfidence = 0;
    let streamedConversationId = conversationId;

    // Add initial empty bot message for streaming
    const initialBotMessage: Message = {
      id: newMessageId,
      role: 'assistant',
      content: '',
      sender: 'bot',
      timestamp: new Date(),
      userQuery: currentQuery,
    };
    setMessages(prev => [...prev, initialBotMessage]);
    setLatestMessageId(newMessageId);
    setIsTyping(false); // Hide typing indicator, show streaming message

    try {
      // Use streaming endpoint - call backend directly with SSE header
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      // If images are present, use non-streaming (vision not supported for streaming)
      if (currentImages.length > 0) {
        const response = await fetch('/api/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: currentQuery,
            conversation_id: conversationId,
            language: language,
            conversation_history: messages
              .filter(m => m.id !== '1')
              .slice(-6)
              .map(m => ({ role: m.role, content: m.content })),
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
          const sourceReferences = rankVisibleSourceReferences(allSourceReferences);

          const chunkIds: number[] = sourceReferences
            .map((ref: SourceReference) => parseInt(ref.chunk_id, 10))
            .filter((id: number) => !isNaN(id));

          if (sourceReferences.length > 0) {
            setCurrentSourceReferences(sourceReferences);
            setSidebarOpen(true);
          }

          setMessages(prev => prev.map(msg =>
            msg.id === newMessageId
              ? {
                ...msg,
                content: data.response || data.answer || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
                followUpQuestions: data.follow_up_questions || [],
                sourceReferences: sourceReferences,
                attachments: data.attachments || [],
                confidence: data.confidence,
                chunkIds: chunkIds,
                chartData: data.chart_data || [],
                images: data.images || [],
                performance: data.performance
              }
              : msg
          ));
        } else {
          const errorPayload = await response.json().catch(() => null);
          throw new Error(errorPayload?.detail || errorPayload?.error || 'API call failed');
        }
        return;
      }

      // Use streaming for text-only messages
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message: currentQuery,
          conversation_id: conversationId,
          language: language,
          conversation_history: messages
            .filter(m => m.id !== '1')
            .slice(-6)
            .map(m => ({ role: m.role, content: m.content })),
        })
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('No response body');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let streamedAttachments: FileAttachment[] = [];
      let streamedChartData: ChartData[] = [];
      let streamedImages: ImageData[] = [];
      let streamedFollowUpQuestions: string[] = [];
      let streamedPerformance: PerformanceMetrics | undefined;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process SSE lines
        let newlineIndex;
        while ((newlineIndex = buffer.indexOf('\n')) >= 0) {
          const line = buffer.slice(0, newlineIndex);
          buffer = buffer.slice(newlineIndex + 1);

          if (line.startsWith('data: ')) {
            const dataStr = line.slice(6);
            try {
              const chunk = JSON.parse(dataStr);

              if (chunk.type === 'metadata') {
                streamedConversationId = chunk.conversation_id || streamedConversationId;
              } else if (chunk.type === 'sources') {
                // Backend sends source_references, not sources
                const allSourceReferences: SourceReference[] = chunk.source_references || [];
                streamedSources = rankVisibleSourceReferences(allSourceReferences);
                streamedConfidence = chunk.confidence || 0;

                if (streamedSources.length > 0) {
                  setCurrentSourceReferences(streamedSources);
                  setSidebarOpen(true);
                }
              } else if (chunk.type === 'answer_chunk') {
                streamedContent += chunk.content || '';
                // Update message content progressively
                setMessages(prev => prev.map(msg =>
                  msg.id === newMessageId
                    ? { ...msg, content: streamedContent }
                    : msg
                ));
              } else if (chunk.type === 'attachments') {
                streamedAttachments = chunk.attachments || [];
                setMessages(prev => prev.map(msg =>
                  msg.id === newMessageId
                    ? { ...msg, attachments: streamedAttachments }
                    : msg
                ));
              } else if (chunk.type === 'complete') {
                // Handle complete chunk with attachments and charts
                streamedAttachments = chunk.attachments || [];
                streamedChartData = chunk.chart_data || [];
                streamedImages = chunk.images || [];
                streamedFollowUpQuestions = chunk.follow_up_questions || [];
                streamedPerformance = chunk.performance;
                // Clear processing status when complete
                setProcessingStatus('');
                setCompletedSteps([]);
              } else if (chunk.type === 'status') {
                // Track real processing status from backend
                const statusMsg = chunk.message || '';
                setCompletedSteps(prev => {
                  // Add completed step if moving to new step
                  if (prev.length === 0 || !prev.includes(statusMsg)) {
                    return [...prev, statusMsg];
                  }
                  return prev;
                });
                setProcessingStatus(statusMsg);
              } else if (chunk.type === 'done') {
                // Streaming complete
                setProcessingStatus('');
                setCompletedSteps([]);
                break;
              } else if (chunk.type === 'error') {
                throw new Error(chunk.message || 'Streaming error');
              }
            } catch (parseError) {
              // Continue on parse errors
              console.warn('Error parsing SSE chunk:', parseError);
            }
          }
        }
      }

      // Final update with all metadata
      const chunkIds: number[] = streamedSources
        .map((ref: SourceReference) => parseInt(ref.chunk_id, 10))
        .filter((id: number) => !isNaN(id));

      setMessages(prev => prev.map(msg =>
        msg.id === newMessageId
          ? {
            ...msg,
            content: streamedContent || 'Xin lỗi, tôi không thể trả lời câu hỏi này lúc này.',
            followUpQuestions: streamedFollowUpQuestions,
            sourceReferences: streamedSources,
            confidence: streamedConfidence,
            chunkIds: chunkIds,
            attachments: streamedAttachments,
            chartData: streamedChartData,
            images: streamedImages,
            performance: streamedPerformance,
          }
          : msg
      ));

    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg =>
        msg.id === newMessageId
          ? { ...msg, content: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.' }
          : msg
      ));
    }
  };

  // Suggested questions from API (trending topics)
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  // Fallback suggested questions
  const fallbackQuestions = FALLBACK_QUESTIONS[language];

  // Fetch suggested questions from API
  useEffect(() => {
    const fetchSuggestedQuestions = async () => {
      setLoadingSuggestions(true);
      try {
        const response = await fetch('/api/analytics/suggested-questions?limit=5');
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.questions && data.questions.length > 0) {
            // Extract question text from API response
            const questions = data.questions.map((q: { question: string }) => q.question);
            setSuggestedQuestions(questions);
          } else {
            // Use fallback if API returns empty
            setSuggestedQuestions([...fallbackQuestions]);
          }
        } else {
          // Use fallback on error
          setSuggestedQuestions([...fallbackQuestions]);
        }
      } catch (error) {
        console.error('Error fetching suggested questions:', error);
        // Use fallback on error
        setSuggestedQuestions([...fallbackQuestions]);
      } finally {
        setLoadingSuggestions(false);
      }
    };

    fetchSuggestedQuestions();
  }, [fallbackQuestions]);

  // Update fallback questions when language changes (if using fallback)
  useEffect(() => {
    if (suggestedQuestions.length === 0 && !loadingSuggestions) {
      setSuggestedQuestions([...fallbackQuestions]);
    }
  }, [fallbackQuestions, loadingSuggestions, suggestedQuestions.length]);



  return (
    <div
      className="min-h-screen bg-cover bg-center bg-fixed"
      style={{ backgroundImage: "url('/assests/background_image.jpg')" }}
    >
      {/* Enhanced Header with Glassmorphism */}
      <header className="backdrop-blur-xl bg-white/80 shadow-xl border-b-4 border-red-600 sticky top-0 z-10 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16 md:h-20">
            <div className="flex items-center space-x-2 sm:space-x-3 md:space-x-4 min-w-0 flex-1">
              {/* Back to Home button */}
              <Link
                href="/"
                className="group flex items-center gap-1 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 text-gray-700 rounded-xl transition-all duration-300 text-xs sm:text-sm font-medium flex-shrink-0 shadow-sm hover:shadow-md hover:scale-105"
                title="Về trang chủ"
              >
                <ArrowLeft className="w-3.5 h-3.5 sm:w-4 sm:h-4 group-hover:-translate-x-0.5 transition-transform" />
                <Home className="w-3.5 h-3.5 sm:w-4 sm:h-4 group-hover:scale-110 transition-transform" />
              </Link>

              <Image
                src="/assests/logo-main.png"
                alt="Logo Trường Đại học An ninh Nhân dân"
                width={40}
                height={40}
                className="object-contain w-8 h-8 sm:w-10 sm:h-10 md:w-12 md:h-12 flex-shrink-0"
              />
              <div className="min-w-0 flex-1">
                <h1 className="text-sm sm:text-lg md:text-xl font-bold text-gray-900 truncate">
                  PSU ChatBot
                </h1>
                <p className="text-xs md:text-sm text-gray-600 hidden xs:block sm:block truncate">Hỗ trợ tư vấn 24/7</p>
              </div>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-1 sm:gap-2 flex-shrink-0">
              {/* Language Toggle */}
              <div className="flex items-center bg-gray-100 rounded-lg p-0.5 sm:p-1">
                <button
                  onClick={() => setLanguage('vi')}
                  className={`px-1.5 sm:px-2.5 py-1 sm:py-1.5 text-xs font-semibold rounded-md transition-all duration-200 ${language === 'vi'
                    ? 'bg-red-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                    }`}
                  title="Tiếng Việt"
                >
                  VI
                </button>
                <button
                  onClick={() => setLanguage('en')}
                  className={`px-1.5 sm:px-2.5 py-1 sm:py-1.5 text-xs font-semibold rounded-md transition-all duration-200 ${language === 'en'
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                    }`}
                  title="English"
                >
                  EN
                </button>
              </div>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="group flex items-center gap-1 sm:gap-2 px-3 sm:px-4 py-2 sm:py-2.5 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-gray-100 hover:to-gray-200 text-gray-700 rounded-xl transition-all duration-300 text-xs sm:text-sm font-medium relative shadow-sm hover:shadow-md hover:scale-105"
              >
                <Book className="w-3.5 h-3.5 sm:w-4 sm:h-4 group-hover:scale-110 transition-transform" />
                <span className="hidden sm:inline">{language === 'vi' ? 'Nguồn' : 'Sources'}</span>
                {visibleCurrentSourceReferences.length > 0 && (
                  <span className="absolute -top-1 -right-1 bg-gradient-to-r from-red-500 to-red-600 text-white text-xs rounded-full w-4 h-4 sm:w-5 sm:h-5 flex items-center justify-center animate-pulse shadow-lg">
                    {visibleCurrentSourceReferences.length}
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Optimized Main Content - Maximum Chat Space */}
      <div className={`transition-all duration-500 ease-out ${sidebarOpen ? 'sm:mr-80 md:mr-96' : 'mr-0'}`}>
        <div className="max-w-4xl mx-auto px-2 sm:px-4 lg:px-8 py-2 sm:py-3">
          <div className="backdrop-blur-xl bg-white/90 rounded-xl sm:rounded-2xl shadow-2xl border border-white/20 h-[calc(100vh-100px)] sm:h-[calc(100vh-110px)] md:h-[calc(100vh-120px)] flex flex-col overflow-hidden">
            {/* Compact Chat Header */}
            <div className="bg-gradient-to-r from-red-600 to-red-700 text-white p-2 sm:p-3 relative overflow-hidden">
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center space-x-2">
                  <div>
                    <h2 className="text-sm font-bold">
                      PSU ChatBot
                    </h2>
                  </div>
                </div>
                {/* Compact disclaimer toggle */}
                <button
                  onClick={() => setShowDisclaimer(!showDisclaimer)}
                  className="text-xs text-red-100 hover:text-white p-1 rounded transition-colors"
                  title="Xem lưu ý"
                >
                  ℹ️
                </button>
              </div>
              {/* Collapsible disclaimer */}
              {showDisclaimer && (
                <div className="mt-2 p-2 bg-white/10 rounded-lg border border-white/20 animate-in slide-in-from-top duration-200">
                  <p className="text-xs text-red-50 leading-relaxed">
                    ⚠️ <span className="font-medium">{language === 'vi' ? 'Lưu ý:' : 'Note:'}</span>{' '}
                    {language === 'vi'
                      ? 'Thông tin từ AI chỉ mang tính tham khảo. Liên hệ phòng ban để được hỗ trợ chính thức.'
                      : 'AI information is for reference only. Contact departments for official support.'}
                  </p>
                </div>
              )}
            </div>

            {/* Expanded Messages Container */}
            <div className="flex-1 overflow-y-auto p-3 sm:p-4 space-y-3 sm:space-y-4 bg-gradient-to-b from-white/50 to-gray-50/50 min-h-0">
              {/* Custom scrollbar styling added via global CSS would be ideal here */}
              {messages.map((message) => (
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
                  onSendFollowUp={handleSendMessage}
                  processingStatus={processingStatus}
                  completedSteps={completedSteps}
                />
              ))}

              {isTyping && (
                <div className="flex justify-start animate-in fade-in slide-in-from-left duration-500">
                  <div className="bg-gradient-to-r from-gray-100 to-gray-50 text-gray-800 rounded-2xl sm:rounded-3xl p-4 md:p-5 max-w-[85%] shadow-lg border border-gray-200/50 backdrop-blur-sm">
                    <div className="flex items-center space-x-3">
                      <div className="relative">
                        <Image
                          src="/assests/chatbot_avatar.png"
                          alt="PSU ChatBot"
                          width={32}
                          height={32}
                          className="rounded-full ring-2 ring-gray-200"
                        />
                        <div className="absolute -bottom-1 -right-1 w-3 h-3 bg-green-400 rounded-full border-2 border-white"></div>
                      </div>
                      <div className="flex space-x-1">
                        <div className="w-2.5 h-2.5 bg-gradient-to-r from-red-400 to-red-500 rounded-full animate-bounce shadow-sm"></div>
                        <div className="w-2.5 h-2.5 bg-gradient-to-r from-red-400 to-red-500 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2.5 h-2.5 bg-gradient-to-r from-red-400 to-red-500 rounded-full animate-bounce shadow-sm" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                      <span className="text-xs text-gray-500 font-medium">Đang trả lời...</span>
                    </div>
                  </div>
                </div>
              )}

              {messages.length === 1 && (
                <div className="space-y-4 animate-in fade-in slide-in-from-bottom duration-700 delay-300">

                  {/* Enhanced Suggested Questions */}
                  <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl p-4 shadow-lg border border-blue-200/50">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-base text-indigo-900 font-bold flex items-center gap-2">
                        🤔 {language === 'vi' ? 'Câu hỏi gợi ý cho bạn:' : 'Suggested questions for you:'}
                      </h3>
                      {loadingSuggestions && (
                        <div className="flex items-center gap-1">
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce"></div>
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                          <div className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        </div>
                      )}
                    </div>
                    <div className="grid grid-cols-1 gap-3">
                      {loadingSuggestions ? (
                        // Enhanced loading skeleton
                        Array.from({ length: 4 }).map((_, index) => (
                          <div
                            key={index}
                            className="p-3 bg-gradient-to-r from-gray-100 to-gray-50 rounded-lg border border-gray-200 animate-pulse"
                          >
                            <div className="h-4 bg-gray-300 rounded w-full mb-2"></div>
                            <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                          </div>
                        ))
                      ) : (
                        suggestedQuestions.slice(0, 4).map((question, index) => (
                          <button
                            key={index}
                            onClick={() => setInputMessage(question)}
                            className={`group text-left p-3 bg-gradient-to-r from-white to-blue-50 hover:from-blue-50 hover:to-indigo-100 rounded-lg border border-blue-200 hover:border-indigo-300 text-gray-700 hover:text-indigo-700 transition-all duration-300 shadow-sm hover:shadow-md hover:scale-[1.02] transform hover-float animate-fadeIn stagger-${(index % 4) + 1}`}
                          >
                            <div className="flex items-start gap-3">
                              <span className="text-blue-500 text-sm mt-0.5">💡</span>
                              <span className="font-medium leading-relaxed text-sm">{question}</span>
                            </div>
                          </button>
                        ))
                      )}
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Compact Input Section */}
            <div className="p-2 sm:p-3 border-t border-gray-200/50 bg-gradient-to-r from-gray-50/80 to-white/80 backdrop-blur-sm">
              {/* Voice recognition error message */}
              {speechRecognitionError && (
                <div className="mb-3 px-3 sm:px-4 py-2 sm:py-3 bg-gradient-to-r from-red-50 to-pink-50 border border-red-200/50 rounded-xl text-red-600 text-sm flex items-center gap-2 shadow-sm">
                  <span className="text-red-500">⚠️</span>
                  {speechRecognitionError}
                </div>
              )}
              {/* Voice recognition listening indicator */}
              {isListening && (
                <div className="mb-3 px-3 sm:px-4 py-2 sm:py-3 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200/50 rounded-xl text-blue-700 text-sm flex items-center gap-3 shadow-sm animate-pulse">
                  <div className="relative">
                    <div className="w-3 h-3 bg-red-500 rounded-full animate-ping"></div>
                    <div className="absolute inset-0 w-3 h-3 bg-red-600 rounded-full"></div>
                  </div>
                  <span className="font-medium">
                    {language === 'vi' ? '🎤 Đang lắng nghe... Nói câu hỏi của bạn' : '🎤 Listening... Speak your question'}
                  </span>
                  {transcript && <span className="text-blue-600 font-semibold truncate">({transcript})</span>}
                </div>
              )}
              {/* Enhanced Image Upload Preview */}
              {uploadedImages.length > 0 && (
                <div className="mb-3 sm:mb-4 p-3 sm:p-4 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl border border-blue-200/50 shadow-lg backdrop-blur-sm">
                  <div className="flex items-center gap-2 mb-3">
                    <div className="p-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg">
                      <ImagePlus className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-bold text-blue-900">
                      {uploadedImages.length}/4 ảnh đã chọn
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-3 sm:gap-4">
                    {uploadedImages.map((image) => (
                      <div key={image.id} className="relative group">
                        <div
                          className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl overflow-hidden border-3 border-white shadow-lg hover:shadow-xl transition-all duration-300 cursor-pointer hover:scale-105 bg-gradient-to-br from-white to-gray-100"
                          onClick={() => setPreviewImage(image.preview)}
                        >
                          <Image
                            src={image.preview}
                            alt={image.name}
                            fill
                            unoptimized
                            sizes="(max-width: 640px) 80px, 96px"
                            className="object-cover transition-all duration-300 group-hover:scale-110"
                          />
                          {/* Enhanced zoom overlay */}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-all duration-300 flex items-center justify-center">
                            <ZoomIn className="w-6 h-6 text-white drop-shadow-lg" />
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            setUploadedImages(prev => prev.filter(img => img.id !== image.id));
                          }}
                          className="absolute -top-2 -right-2 w-6 h-6 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300 hover:scale-110 shadow-lg"
                          title="Xóa ảnh"
                        >
                          <X className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    ))}
                    {/* Enhanced Add more button */}
                    {uploadedImages.length < 4 && (
                      <label className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl border-2 border-dashed border-blue-300 hover:border-blue-500 flex flex-col items-center justify-center text-blue-400 hover:text-blue-600 transition-all duration-300 cursor-pointer bg-gradient-to-br from-white to-blue-50/30 hover:from-blue-50 hover:to-blue-100 hover:scale-105 group">
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
                        <ImagePlus className="w-6 h-6 sm:w-7 sm:h-7 group-hover:scale-110 transition-transform" />
                        <span className="text-xs font-medium mt-1">Thêm</span>
                      </label>
                    )}
                  </div>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-blue-200/30">
                    <span className="text-sm text-blue-700 font-bold flex items-center gap-2">
                      <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></span>
                      Click ảnh để xem chi tiết
                    </span>
                    <button
                      onClick={() => setUploadedImages([])}
                      className="text-xs text-red-600 hover:text-red-800 font-semibold bg-red-50 hover:bg-red-100 px-3 py-1.5 rounded-lg transition-all duration-200 hover:shadow-sm"
                    >
                      Xóa tất cả
                    </button>
                  </div>
                </div>
              )}
              <div className="flex items-center gap-1 sm:gap-2">
                {/* Enhanced Image Upload Button */}
                {uploadedImages.length === 0 && (
                  <label className="group flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-r from-gray-100 to-gray-200 text-gray-600 hover:from-indigo-100 hover:to-purple-200 hover:text-indigo-600 transition-all duration-300 cursor-pointer flex-shrink-0 shadow-sm hover:shadow-md hover:scale-105">
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

                          // Validate file size (max 5MB)
                          const maxSize = 5 * 1024 * 1024; // 5MB
                          if (file.size > maxSize) {
                            const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                            alert(`Ảnh "${file.name}" vượt quá 5MB (hiện tại: ${sizeMB}MB). Vui lòng chọn ảnh nhỏ hơn.`);
                            continue;
                          }

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
                    <ImagePlus className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
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

                      // Validate file size (max 5MB)
                      const maxSize = 5 * 1024 * 1024; // 5MB
                      if (file.size > maxSize) {
                        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
                        alert(`Ảnh paste vượt quá 5MB (hiện tại: ${sizeMB}MB). Vui lòng chọn ảnh nhỏ hơn.`);
                        continue;
                      }

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
                  placeholder={
                    isListening
                      ? (language === 'vi' ? "🎤 Đang lắng nghe..." : "🎤 Listening...")
                      : uploadedImages.length > 0
                        ? (language === 'vi' ? "💭 Mô tả hoặc hỏi về ảnh..." : "💭 Describe or ask about the image...")
                        : (language === 'vi' ? "💬 Nhập câu hỏi hoặc dán ảnh (Ctrl+V)..." : "💬 Type a question or paste an image (Ctrl+V)...")
                  }
                  className="flex-1 min-w-0 min-h-[44px] sm:min-h-[48px] px-4 sm:px-5 py-3 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-red-500/50 focus:border-red-500 text-sm sm:text-base font-medium bg-white/90 backdrop-blur-sm shadow-sm hover:shadow-md transition-all duration-300 placeholder:text-gray-400 input-focus-glow"
                  disabled={isTyping || isListening}
                />
                <button
                  onClick={() => handleSendMessage()}
                  disabled={(!inputMessage.trim() && uploadedImages.length === 0) || isTyping}
                  className="group flex-shrink-0 w-11 h-11 sm:w-12 sm:h-12 bg-gradient-to-r from-red-500 via-red-600 to-red-700 text-white rounded-2xl hover:from-red-600 hover:via-red-700 hover:to-red-800 disabled:bg-gray-300 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center shadow-lg shadow-red-500/30 hover:shadow-xl hover:shadow-red-500/40 hover:scale-105 btn-send-ripple"
                  aria-label="Gửi tin nhắn"
                >
                  <Send className="w-5 h-5 sm:w-6 sm:h-6 group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
              {/* Ultra Compact Footer */}
              <div className="mt-1.5 pt-1.5 border-t border-gray-200">
                <div className="text-center">
                  <p className="text-xs text-gray-500 leading-tight">
                    📋 {language === 'vi'
                      ? <>Mọi thông tin pháp lý chính thức xin tham khảo văn bản được công bố trên <a href="https://dhannd.bocongan.gov.vn/" target="_blank" rel="noopener noreferrer" className="text-red-600 hover:text-red-700 hover:underline font-medium">website/trang thông báo của trường</a>.</>
                      : <>For all official legal information, please refer to documents published on the <a href="https://dhannd.bocongan.gov.vn/" target="_blank" rel="noopener noreferrer" className="text-red-600 hover:text-red-700 hover:underline font-medium">university&apos;s website/notice board</a>.</>
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Document Sidebar */}
      <DocumentSidebar
        sourceReferences={visibleCurrentSourceReferences}
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

      {/* Image Preview Modal for uploaded images before sending */}
      <ImageModal
        isOpen={!!previewImage}
        onClose={() => setPreviewImage(null)}
        imageSrc={previewImage || ''}
        imageAlt="Preview image"
      />

      {/* Mobile Source Drawer - Bottom Sheet */}
      <MobileSourceDrawer
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        sources={visibleCurrentSourceReferences}
        onViewDocument={handleOpenDocument}
      />

      {/* Floating Action Button for Sources on Mobile - REMOVED as per user request to avoid overlap */}
      {/* <SourceFAB
        sourceCount={visibleCurrentSourceReferences.length}
        onClick={() => setSidebarOpen(true)}
      /> */}
    </div>
  );
};

export default ChatBotPage;
