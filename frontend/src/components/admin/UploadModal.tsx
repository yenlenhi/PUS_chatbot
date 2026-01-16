'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { X, Upload, FileText, CheckCircle, AlertCircle, Loader2, File, Clock, Zap, Sparkles } from 'lucide-react';
import DetailedErrorDisplay from './DetailedErrorDisplay';

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

type UploadStatus = 'idle' | 'uploading' | 'processing' | 'success' | 'error';

interface UploadState {
  status: UploadStatus;
  progress: number;
  message: string;
  startTime?: number;
  estimatedTimeRemaining?: number;
  uploadSpeed?: number;
  result?: {
    filename: string;
    chunks_created: number;
    embeddings_created: number;
  };
}

const CATEGORIES = [
  { value: 'Khác', label: 'Khác' },
  { value: 'Đào tạo', label: 'Đào tạo' },
  { value: 'Tuyển sinh', label: 'Tuyển sinh' },
  { value: 'Tài chính', label: 'Tài chính' },
  { value: 'Sinh viên', label: 'Sinh viên' },
];

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

const UploadModal: React.FC<UploadModalProps> = ({ isOpen, onClose, onUploadSuccess }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [category, setCategory] = useState('Khác');
  const [useGemini, setUseGemini] = useState(true);
  const [uploadState, setUploadState] = useState<UploadState>({
    status: 'idle',
    progress: 0,
    message: '',
  });
  const [isDragging, setIsDragging] = useState(false);
  const [isHovering, setIsHovering] = useState(false);
  const [showErrorDetails, setShowErrorDetails] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const startTimeRef = useRef<number>(0);

  const resetState = useCallback(() => {
    setSelectedFile(null);
    setCategory('Khác');
    setUseGemini(true);
    setUploadState({ status: 'idle', progress: 0, message: '' });
    setIsHovering(false);
    setShowErrorDetails(false);
    startTimeRef.current = 0;
  }, []);

  // Calculate upload metrics
  const calculateUploadMetrics = useCallback((progress: number, fileSize?: number) => {
    if (!startTimeRef.current || progress === 0) return {};
    
    const elapsed = (Date.now() - startTimeRef.current) / 1000; // seconds
    const speed = fileSize ? (fileSize * (progress / 100)) / elapsed : 0; // bytes per second
    const remainingProgress = 100 - progress;
    const estimatedTimeRemaining = progress > 0 ? (elapsed * remainingProgress) / progress : 0;
    
    return {
      uploadSpeed: speed,
      estimatedTimeRemaining: Math.max(0, estimatedTimeRemaining)
    };
  }, []);

  const formatSpeed = (bytesPerSecond: number) => {
    if (bytesPerSecond < 1024) return `${bytesPerSecond.toFixed(0)} B/s`;
    if (bytesPerSecond < 1024 * 1024) return `${(bytesPerSecond / 1024).toFixed(1)} KB/s`;
    return `${(bytesPerSecond / (1024 * 1024)).toFixed(1)} MB/s`;
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${Math.ceil(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.ceil(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  const handleClose = useCallback(() => {
    if (uploadState.status === 'uploading' || uploadState.status === 'processing') {
      if (!confirm('Đang xử lý file. Bạn có chắc muốn đóng?')) {
        return;
      }
    }
    resetState();
    onClose();
  }, [uploadState.status, resetState, onClose]);

  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'Chỉ chấp nhận file PDF. Vui lòng chọn file có đuôi .pdf';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File quá lớn. Kích thước tối đa là 50MB, file của bạn là ${(file.size / (1024 * 1024)).toFixed(1)}MB`;
    }
    if (file.size === 0) {
      return 'File rỗng. Vui lòng chọn file khác.';
    }
    return null;
  };

  const handleFileSelect = useCallback((file: File) => {
    const error = validateFile(file);
    if (error) {
      setUploadState({ status: 'error', progress: 0, message: error });
      return;
    }
    setSelectedFile(file);
    setUploadState({ status: 'idle', progress: 0, message: '' });
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    // Only set to false if leaving the drop zone completely
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }, []);

  const handleMouseEnter = useCallback(() => {
    if (!isProcessing) setIsHovering(true);
  }, [uploadState.status]);

  const handleMouseLeave = useCallback(() => {
    setIsHovering(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  const handleUpload = async () => {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('category', category);
    formData.append('use_gemini', String(useGemini));

    try {
      startTimeRef.current = Date.now();
      setUploadState({
        status: 'uploading',
        progress: 10,
        message: 'Đang tải file lên server...',
        startTime: startTimeRef.current,
      });

      // Use API route proxy instead of calling backend directly
      // This ensures BACKEND_URL is used from server-side
      const uploadUrl = '/api/upload';
      
      // Enhanced progress simulation with metrics
      const progressInterval = setInterval(() => {
        setUploadState(prev => {
          if (prev.progress < 30) {
            const newProgress = prev.progress + 5;
            const metrics = calculateUploadMetrics(newProgress, selectedFile?.size);
            return { 
              ...prev, 
              progress: newProgress,
              ...metrics
            };
          }
          return prev;
        });
      }, 200);

      const response = await fetch(uploadUrl, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
      }

      setUploadState({
        status: 'processing',
        progress: 40,
        message: 'Đang xử lý PDF...',
      });

      // Enhanced processing progress with metrics
      const processingMessages = [
        { progress: 50, message: 'Đang trích xuất văn bản...', icon: FileText },
        { progress: 65, message: 'Đang phân đoạn nội dung...', icon: Zap },
        { progress: 80, message: 'Đang tạo embeddings...', icon: Sparkles },
        { progress: 90, message: 'Đang lưu vào database...', icon: CheckCircle },
      ];

      for (const step of processingMessages) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setUploadState(prev => {
          const metrics = calculateUploadMetrics(step.progress, selectedFile?.size);
          return {
            ...prev,
            progress: step.progress,
            message: step.message,
            ...metrics
          };
        });
      }

      const result = await response.json();

      if (result.success) {
        setUploadState({
          status: 'success',
          progress: 100,
          message: result.message || 'Upload thành công!',
          result: {
            filename: result.filename,
            chunks_created: result.chunks_created,
            embeddings_created: result.embeddings_created,
          },
        });

        // Auto close after success
        setTimeout(() => {
          onUploadSuccess();
          handleClose();
        }, 2000);
      } else {
        setUploadState({
          status: 'error',
          progress: 0,
          message: result.message || 'Có lỗi xảy ra khi xử lý file',
        });
      }
    } catch (error) {
      console.error('Upload error:', error);
      setUploadState({
        status: 'error',
        progress: 0,
        message: error instanceof Error ? error.message : 'Có lỗi xảy ra khi upload file',
      });
    }
  };

  if (!isOpen) return null;

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const isProcessing = uploadState.status === 'uploading' || uploadState.status === 'processing';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop - Improved with blur and gradient */}
      <div 
        className="fixed inset-0 bg-gradient-to-br from-gray-900/80 via-gray-800/70 to-gray-900/80 backdrop-blur-sm transition-all duration-300"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl max-w-lg w-full transform transition-all animate-modal-appear">
          {/* Header - Enhanced with gradient */}
          <div className="flex items-center justify-between p-6 border-b border-gray-100 bg-gradient-to-r from-red-50 to-orange-50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <FileText className="w-5 h-5 text-red-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">
                Upload Tài liệu PDF
              </h2>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-white rounded-lg transition-all shadow-sm"
              disabled={isProcessing}
              title="Đóng"
            >
              <X className="w-5 h-5 text-gray-500 hover:text-gray-700" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Drop Zone - Enhanced with better visuals */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onMouseEnter={handleMouseEnter}
              onMouseLeave={handleMouseLeave}
              onClick={() => !isProcessing && fileInputRef.current?.click()}
              className={`
                relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer overflow-hidden
                transition-all duration-500 ease-in-out
                ${isDragging 
                  ? 'border-red-500 bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 scale-[1.03] shadow-2xl transform rotate-1' 
                  : selectedFile 
                    ? 'border-green-500 bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 shadow-lg transform scale-[1.01]' 
                    : isHovering
                      ? 'border-red-400 bg-gradient-to-br from-red-50 via-pink-50 to-purple-50 shadow-lg transform scale-[1.01]'
                      : 'border-gray-300 hover:border-red-300 hover:shadow-md'
                }
                ${isProcessing ? 'cursor-not-allowed opacity-60' : ''}
              `}
            >
              {/* Animated Background Particles */}
              {(isDragging || isHovering) && (
                <div className="absolute inset-0 pointer-events-none">
                  <div className="absolute top-4 left-4 w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="absolute top-8 right-8 w-1 h-1 bg-orange-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="absolute bottom-6 left-8 w-1.5 h-1.5 bg-pink-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  <div className="absolute bottom-4 right-4 w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '450ms' }} />
                </div>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleInputChange}
                className="hidden"
                disabled={isProcessing}
              />

              {selectedFile ? (
                <div className="relative z-10 flex flex-col items-center animate-in fade-in duration-500 slide-in-from-bottom-4">
                  <div className="p-4 bg-gradient-to-br from-green-100 to-emerald-100 rounded-2xl mb-4 shadow-inner">
                    <File className="w-12 h-12 text-green-600" />
                  </div>
                  <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 shadow-lg border border-green-200/50">
                    <p className="text-sm font-bold text-gray-900 mb-1">{selectedFile.name}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-600">
                      <span className="font-medium">{formatFileSize(selectedFile.size)}</span>
                      <span className="w-1 h-1 bg-gray-400 rounded-full"></span>
                      <span className="text-green-600 font-medium">✓ Sẵn sàng upload</span>
                    </div>
                  </div>
                  {!isProcessing && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                      }}
                      className="mt-4 px-4 py-2 text-sm font-semibold text-red-600 hover:text-white bg-white hover:bg-red-600 border border-red-200 hover:border-red-600 rounded-lg transition-all duration-300 hover:scale-105 hover:shadow-md"
                    >
                      Chọn file khác
                    </button>
                  )}
                </div>
              ) : (
                <div className="relative z-10 flex flex-col items-center animate-in fade-in duration-300">
                  <div className={`p-5 rounded-2xl mb-4 transition-all duration-500 ${
                    isDragging 
                      ? 'bg-gradient-to-br from-red-100 to-orange-100 shadow-lg scale-110'
                      : isHovering
                        ? 'bg-gradient-to-br from-gray-100 to-red-50 shadow-md scale-105'
                        : 'bg-gradient-to-br from-gray-100 to-gray-50'
                  }`}>
                    <Upload className={`w-12 h-12 transition-all duration-300 ${
                      isDragging ? 'text-red-600 animate-pulse' : isHovering ? 'text-red-500' : 'text-gray-400'
                    }`} />
                  </div>
                  <div className="text-center space-y-2">
                    <p className={`text-sm font-bold transition-all duration-300 ${
                      isDragging ? 'text-red-600' : isHovering ? 'text-red-500' : 'text-gray-700'
                    }`}>
                      {isDragging ? 'Thả file PDF vào đây!' : 'Kéo thả file PDF vào đây'}
                    </p>
                    <p className="text-xs text-gray-500">
                      hoặc <span className="font-semibold text-red-600">click để chọn file</span> (tối đa 50MB)
                    </p>
                    <div className="flex items-center justify-center gap-2 mt-3">
                      <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                      <span className="text-xs text-gray-400 font-medium">Hỗ trợ file .PDF</span>
                      <div className="w-2 h-2 bg-red-400 rounded-full animate-pulse"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Options - Enhanced with mobile optimization */}
            <div className="space-y-4">
              {/* Category */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Danh mục
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  disabled={isProcessing}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 disabled:bg-gray-100 disabled:cursor-not-allowed font-medium shadow-sm transition-all text-touch min-h-touch"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Use Gemini Toggle - Enhanced with mobile optimization */}
              <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
                <div className="flex-1 pr-4">
                  <p className="text-sm font-semibold text-gray-800">
                    Sử dụng Gemini OCR
                  </p>
                  <p className="text-xs text-gray-600 mt-0.5">
                    Khuyến nghị cho PDF scan/ảnh <span className="hidden sm:inline">(xử lý lâu hơn)</span>
                  </p>
                </div>
                <button
                  onClick={() => !isProcessing && setUseGemini(!useGemini)}
                  disabled={isProcessing}
                  className={`
                    relative w-16 h-8 rounded-full transition-all duration-300 min-w-touch min-h-touch flex items-center
                    ${useGemini ? 'bg-red-600 shadow-md' : 'bg-gray-300'}
                    ${isProcessing ? 'cursor-not-allowed opacity-50' : 'cursor-pointer hover:shadow-lg'}
                  `}
                >
                  <span
                    className={`
                      absolute top-1 left-1 w-6 h-6 bg-white rounded-full shadow-md
                      transition-transform duration-300 ease-in-out
                      ${useGemini ? 'translate-x-8' : 'translate-x-0'}
                    `}
                  />
                </button>
              </div>
            </div>

            {/* Enhanced Progress Bar with Metrics */}
            {isProcessing && (
              <div className="space-y-4 p-4 sm:p-6 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-xl border border-blue-200 shadow-lg">
                {/* Progress Header */}
                <div className="flex items-start sm:items-center justify-between gap-3">
                  <div className="flex items-start sm:items-center gap-3 flex-1">
                    <div className="p-2 bg-white rounded-lg shadow-sm flex-shrink-0">
                      <Loader2 className="w-5 h-5 animate-spin text-red-600" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-bold text-gray-900 truncate">{uploadState.message}</p>
                      <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-3 text-xs text-gray-600 mt-1">
                        {uploadState.uploadSpeed && (
                          <span className="flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            {formatSpeed(uploadState.uploadSpeed)}
                          </span>
                        )}
                        {uploadState.estimatedTimeRemaining && uploadState.estimatedTimeRemaining > 0 && (
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            Còn {formatTime(uploadState.estimatedTimeRemaining)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-xl sm:text-2xl font-bold text-red-600">{uploadState.progress}%</span>
                  </div>
                </div>
                
                {/* Enhanced Progress Bar */}
                <div className="relative">
                  <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden shadow-inner">
                    <div
                      className="h-full bg-gradient-to-r from-red-500 via-orange-500 to-yellow-500 transition-all duration-500 ease-out shadow-sm relative overflow-hidden"
                      style={{ width: `${uploadState.progress}%` }}
                    >
                      {/* Shimmer effect */}
                      <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
                    </div>
                  </div>
                  
                  {/* Progress Steps - Mobile responsive */}
                  <div className="flex justify-between mt-2 text-xs text-gray-500">
                    <span className={uploadState.progress >= 25 ? 'text-green-600 font-medium' : ''}>Tải lên</span>
                    <span className={`${uploadState.progress >= 50 ? 'text-green-600 font-medium' : ''} hidden xs:inline`}>Xử lý</span>
                    <span className={uploadState.progress >= 75 ? 'text-green-600 font-medium' : ''}>Embedding</span>
                    <span className={uploadState.progress >= 100 ? 'text-green-600 font-medium' : ''}>Hoàn thành</span>
                  </div>
                </div>
              </div>
            )}

            {/* Status Messages - Enhanced */}
            {uploadState.status === 'success' && (
              <div className="flex items-start p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200 shadow-sm animate-in fade-in duration-300">
                <div className="p-1 bg-green-100 rounded-full mr-3 flex-shrink-0">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-green-800">
                    {uploadState.message}
                  </p>
                  {uploadState.result && (
                    <p className="text-xs text-green-700 mt-1.5 font-medium">
                      ✓ Đã tạo {uploadState.result.chunks_created} chunks và {uploadState.result.embeddings_created} embeddings
                    </p>
                  )}
                </div>
              </div>
            )}

            {uploadState.status === 'error' && (
              <DetailedErrorDisplay
                error={uploadState.message}
                onRetry={() => {
                  setUploadState(prev => ({ ...prev, status: 'idle', message: '' }));
                  setShowErrorDetails(false);
                }}
                onCopy={() => {
                  // Toast notification có thể thêm vào đây
                  console.log('Error details copied to clipboard');
                }}
                className="animate-in fade-in duration-300"
              />
            )}
          </div>

          {/* Footer - Enhanced with mobile optimization */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 p-4 sm:p-6 border-t border-gray-100 bg-gray-50/50">
            <button
              onClick={handleClose}
              disabled={isProcessing}
              className="px-5 py-3 text-gray-700 font-medium hover:bg-white border border-gray-200 hover:border-gray-300 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm min-h-touch order-2 sm:order-1"
            >
              Hủy
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isProcessing}
              className={`
                px-6 py-3 rounded-lg font-semibold transition-all min-h-touch order-1 sm:order-2
                flex items-center justify-center gap-2
                ${!selectedFile || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-red-600 to-red-700 hover:from-red-700 hover:to-red-800 text-white shadow-md hover:shadow-lg transform hover:scale-[1.02] active:scale-[0.98]'
                }
              `}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Đang xử lý...</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  <span>Upload</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
