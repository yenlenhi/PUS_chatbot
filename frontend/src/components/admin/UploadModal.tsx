'use client';

import React, { useState, useRef, useCallback } from 'react';
import { X, Upload, FileText, CheckCircle, AlertCircle, Loader2, File } from 'lucide-react';

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
  const fileInputRef = useRef<HTMLInputElement>(null);

  const resetState = useCallback(() => {
    setSelectedFile(null);
    setCategory('Khác');
    setUseGemini(true);
    setUploadState({ status: 'idle', progress: 0, message: '' });
  }, []);

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
    setIsDragging(false);
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
      setUploadState({
        status: 'uploading',
        progress: 10,
        message: 'Đang tải file lên server...',
      });

      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Simulate progress for upload
      const progressInterval = setInterval(() => {
        setUploadState(prev => {
          if (prev.progress < 30) {
            return { ...prev, progress: prev.progress + 5 };
          }
          return prev;
        });
      }, 200);

      const response = await fetch(`${API_URL}/api/v1/admin/upload`, {
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

      // Simulate processing progress
      const processingMessages = [
        { progress: 50, message: 'Đang trích xuất văn bản...' },
        { progress: 65, message: 'Đang phân đoạn nội dung...' },
        { progress: 80, message: 'Đang tạo embeddings...' },
        { progress: 90, message: 'Đang lưu vào database...' },
      ];

      for (const step of processingMessages) {
        await new Promise(resolve => setTimeout(resolve, 500));
        setUploadState(prev => ({
          ...prev,
          progress: step.progress,
          message: step.message,
        }));
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
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-xl shadow-2xl max-w-lg w-full transform transition-all">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-xl font-semibold text-gray-900">
              Upload Tài liệu PDF
            </h2>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              disabled={isProcessing}
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => !isProcessing && fileInputRef.current?.click()}
              className={`
                border-2 border-dashed rounded-xl p-8 text-center cursor-pointer
                transition-all duration-200
                ${isDragging 
                  ? 'border-red-500 bg-red-50' 
                  : selectedFile 
                    ? 'border-green-500 bg-green-50' 
                    : 'border-gray-300 hover:border-red-400 hover:bg-gray-50'
                }
                ${isProcessing ? 'cursor-not-allowed opacity-60' : ''}
              `}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                onChange={handleInputChange}
                className="hidden"
                disabled={isProcessing}
              />

              {selectedFile ? (
                <div className="flex flex-col items-center">
                  <File className="w-12 h-12 text-green-600 mb-3" />
                  <p className="text-sm font-medium text-gray-900">{selectedFile.name}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {formatFileSize(selectedFile.size)}
                  </p>
                  {!isProcessing && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedFile(null);
                      }}
                      className="mt-2 text-xs text-red-600 hover:text-red-800"
                    >
                      Chọn file khác
                    </button>
                  )}
                </div>
              ) : (
                <div className="flex flex-col items-center">
                  <Upload className="w-12 h-12 text-gray-400 mb-3" />
                  <p className="text-sm font-medium text-gray-700">
                    Kéo thả file PDF vào đây
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    hoặc click để chọn file (tối đa 50MB)
                  </p>
                </div>
              )}
            </div>

            {/* Options */}
            <div className="space-y-4">
              {/* Category */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Danh mục
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  disabled={isProcessing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent text-gray-900 disabled:bg-gray-100"
                >
                  {CATEGORIES.map((cat) => (
                    <option key={cat.value} value={cat.value}>
                      {cat.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Use Gemini Toggle */}
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-sm font-medium text-gray-700">
                    Sử dụng Gemini OCR
                  </p>
                  <p className="text-xs text-gray-500 mt-0.5">
                    Khuyến nghị cho PDF scan/ảnh (xử lý lâu hơn)
                  </p>
                </div>
                <button
                  onClick={() => !isProcessing && setUseGemini(!useGemini)}
                  disabled={isProcessing}
                  className={`
                    relative w-12 h-6 rounded-full transition-colors
                    ${useGemini ? 'bg-red-600' : 'bg-gray-300'}
                    ${isProcessing ? 'cursor-not-allowed' : 'cursor-pointer'}
                  `}
                >
                  <span
                    className={`
                      absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow
                      transition-transform duration-200
                      ${useGemini ? 'translate-x-6' : 'translate-x-0'}
                    `}
                  />
                </button>
              </div>
            </div>

            {/* Progress Bar */}
            {isProcessing && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-700">{uploadState.message}</span>
                  <span className="text-gray-500">{uploadState.progress}%</span>
                </div>
                <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-red-600 transition-all duration-300 ease-out"
                    style={{ width: `${uploadState.progress}%` }}
                  />
                </div>
              </div>
            )}

            {/* Status Messages */}
            {uploadState.status === 'success' && (
              <div className="flex items-start p-4 bg-green-50 rounded-lg">
                <CheckCircle className="w-5 h-5 text-green-600 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-green-800">
                    {uploadState.message}
                  </p>
                  {uploadState.result && (
                    <p className="text-xs text-green-600 mt-1">
                      Đã tạo {uploadState.result.chunks_created} chunks và {uploadState.result.embeddings_created} embeddings
                    </p>
                  )}
                </div>
              </div>
            )}

            {uploadState.status === 'error' && (
              <div className="flex items-start p-4 bg-red-50 rounded-lg">
                <AlertCircle className="w-5 h-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-800">{uploadState.message}</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200">
            <button
              onClick={handleClose}
              disabled={isProcessing}
              className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
            >
              Hủy
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isProcessing}
              className={`
                px-6 py-2 rounded-lg font-medium transition-all
                flex items-center gap-2
                ${!selectedFile || isProcessing
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-red-600 hover:bg-red-700 text-white shadow-sm hover:shadow'
                }
              `}
            >
              {isProcessing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Đang xử lý...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  Upload
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
