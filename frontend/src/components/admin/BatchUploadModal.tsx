'use client';

import React, { useState, useRef, useCallback, useEffect } from 'react';
import { 
  X, Upload, FileText, CheckCircle, AlertCircle, Loader2, File, 
  Clock, Zap, Sparkles, Pause, Play, Trash2, RotateCcw, Plus,
  FolderOpen, Archive, Database
} from 'lucide-react';
import DetailedErrorDisplay from './DetailedErrorDisplay';

interface BatchUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

type FileStatus = 'pending' | 'uploading' | 'processing' | 'paused' | 'completed' | 'error';

interface UploadFile {
  id: string;
  file: File;
  category: string;
  useGemini: boolean;
  status: FileStatus;
  progress: number;
  message: string;
  uploadSpeed?: number;
  estimatedTimeRemaining?: number;
  startTime?: number;
  result?: {
    filename: string;
    chunks_created: number;
    embeddings_created: number;
  };
  error?: string;
}

interface BatchProgress {
  totalFiles: number;
  completedFiles: number;
  failedFiles: number;
  totalProgress: number;
  averageSpeed: number;
  estimatedTimeRemaining: number;
}

const CATEGORIES = [
  { value: 'Khác', label: 'Khác' },
  { value: 'Đào tạo', label: 'Đào tạo' },
  { value: 'Tuyển sinh', label: 'Tuyển sinh' },
  { value: 'Tài chính', label: 'Tài chính' },
  { value: 'Sinh viên', label: 'Sinh viên' },
];

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const MAX_FILES = 10; // Maximum files per batch

const BatchUploadModal: React.FC<BatchUploadModalProps> = ({ isOpen, onClose, onUploadSuccess }) => {
  const [files, setFiles] = useState<UploadFile[]>([]);
  const [defaultCategory, setDefaultCategory] = useState('Khác');
  const [defaultUseGemini, setDefaultUseGemini] = useState(true);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [batchProgress, setBatchProgress] = useState<BatchProgress>({
    totalFiles: 0,
    completedFiles: 0,
    failedFiles: 0,
    totalProgress: 0,
    averageSpeed: 0,
    estimatedTimeRemaining: 0,
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const processQueueRef = useRef<boolean>(false);

  // Utility functions
  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

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

  const generateId = () => Math.random().toString(36).substr(2, 9);

  // File validation
  const validateFile = (file: File): string | null => {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      return 'Chỉ chấp nhận file PDF';
    }
    if (file.size > MAX_FILE_SIZE) {
      return `File quá lớn (tối đa 50MB)`;
    }
    if (file.size === 0) {
      return 'File rỗng';
    }
    return null;
  };

  // Add files to queue
  const addFiles = useCallback((newFiles: FileList | File[]) => {
    const fileArray = Array.from(newFiles);
    const validFiles: UploadFile[] = [];
    
    fileArray.forEach(file => {
      // Check if file already exists
      const exists = files.some(f => f.file.name === file.name && f.file.size === file.size);
      if (exists) return;
      
      // Check file count limit
      if (files.length + validFiles.length >= MAX_FILES) return;
      
      // Validate file
      const error = validateFile(file);
      if (error) return;
      
      validFiles.push({
        id: generateId(),
        file,
        category: defaultCategory,
        useGemini: defaultUseGemini,
        status: 'pending',
        progress: 0,
        message: 'Chờ upload...',
      });
    });
    
    setFiles(prev => [...prev, ...validFiles]);
  }, [files, defaultCategory, defaultUseGemini]);

  // Remove file from queue
  const removeFile = useCallback((id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  // Retry failed file
  const retryFile = useCallback((id: string) => {
    setFiles(prev => prev.map(f => 
      f.id === id 
        ? { ...f, status: 'pending', error: undefined, progress: 0 }
        : f
    ));
  }, []);

  // Update file settings
  const updateFile = useCallback((id: string, updates: Partial<UploadFile>) => {
    setFiles(prev => prev.map(f => f.id === id ? { ...f, ...updates } : f));
  }, []);

  // Batch controls
  const pauseAll = useCallback(() => {
    processQueueRef.current = false;
    setFiles(prev => prev.map(f => 
      f.status === 'uploading' || f.status === 'processing' 
        ? { ...f, status: 'paused', message: 'Đã tạm dừng' }
        : f
    ));
    setIsProcessing(false);
  }, []);

  const resumeAll = useCallback(() => {
    processQueueRef.current = true;
    setFiles(prev => prev.map(f => 
      f.status === 'paused' 
        ? { ...f, status: 'pending', message: 'Chờ upload...' }
        : f
    ));
    setIsProcessing(true);
    processUploadQueue();
  }, []);

  const retryFailed = useCallback(() => {
    setFiles(prev => prev.map(f => 
      f.status === 'error' 
        ? { ...f, status: 'pending', message: 'Chờ upload...', progress: 0, error: undefined }
        : f
    ));
  }, []);

  const clearCompleted = useCallback(() => {
    setFiles(prev => prev.filter(f => f.status !== 'completed'));
  }, []);

  // Upload single file
  const uploadSingleFile = useCallback(async (uploadFile: UploadFile) => {
    if (!processQueueRef.current) return;

    const formData = new FormData();
    formData.append('file', uploadFile.file);
    formData.append('category', uploadFile.category);
    formData.append('use_gemini', String(uploadFile.useGemini));

    const startTime = Date.now();
    updateFile(uploadFile.id, { 
      status: 'uploading', 
      startTime,
      message: 'Đang tải file lên server...',
      progress: 10 
    });

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!processQueueRef.current) return;

      // Simulate progress updates
      for (let progress = 20; progress <= 40 && processQueueRef.current; progress += 10) {
        await new Promise(resolve => setTimeout(resolve, 200));
        const elapsed = (Date.now() - startTime) / 1000;
        const speed = (uploadFile.file.size * (progress / 100)) / elapsed;
        updateFile(uploadFile.id, { progress, uploadSpeed: speed });
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Upload failed`);
      }

      updateFile(uploadFile.id, {
        status: 'processing',
        progress: 50,
        message: 'Đang xử lý PDF...',
      });

      // Processing phases
      const processingSteps = [
        { progress: 60, message: 'Đang trích xuất văn bản...', delay: 500 },
        { progress: 70, message: 'Đang phân đoạn nội dung...', delay: 500 },
        { progress: 85, message: 'Đang tạo embeddings...', delay: 800 },
        { progress: 95, message: 'Đang lưu vào database...', delay: 300 },
      ];

      for (const step of processingSteps) {
        if (!processQueueRef.current) return;
        await new Promise(resolve => setTimeout(resolve, step.delay));
        updateFile(uploadFile.id, {
          progress: step.progress,
          message: step.message,
        });
      }

      const result = await response.json();

      if (result.success) {
        updateFile(uploadFile.id, {
          status: 'completed',
          progress: 100,
          message: 'Upload thành công!',
          result: {
            filename: result.filename,
            chunks_created: result.chunks_created,
            embeddings_created: result.embeddings_created,
          },
        });
      } else {
        updateFile(uploadFile.id, {
          status: 'error',
          progress: 0,
          message: result.message || 'Có lỗi xảy ra',
          error: result.message,
        });
      }
    } catch (error) {
      updateFile(uploadFile.id, {
        status: 'error',
        progress: 0,
        message: error instanceof Error ? error.message : 'Có lỗi xảy ra',
        error: error instanceof Error ? error.message : 'Unknown error',
      });
    }
  }, [updateFile]);

  // Process upload queue
  const processUploadQueue = useCallback(async () => {
    if (!processQueueRef.current) return;

    const pendingFiles = files.filter(f => f.status === 'pending');
    
    for (const file of pendingFiles) {
      if (!processQueueRef.current) break;
      await uploadSingleFile(file);
    }

    // Check if all files are processed using functional state update to get latest state
    setFiles(prevFiles => {
      const allProcessed = prevFiles.every(f => 
        f.status === 'completed' || f.status === 'error' || f.status === 'paused'
      );
      
      if (allProcessed) {
        setIsProcessing(false);
        processQueueRef.current = false;
        
        // Auto close if all successful
        const allSuccessful = prevFiles.every(f => f.status === 'completed');
        if (allSuccessful && prevFiles.length > 0) {
          setTimeout(() => {
            onUploadSuccess();
            // Reset state and close
            setFiles([]);
            setIsProcessing(false);
            setIsDragging(false);
            onClose();
          }, 2000);
        }
      }
      
      return prevFiles; // Return unchanged state
    });
  }, [files, uploadSingleFile, onUploadSuccess, onClose]);

  // Start batch upload
  const startBatchUpload = useCallback(() => {
    if (files.length === 0) return;
    
    processQueueRef.current = true;
    setIsProcessing(true);
    processUploadQueue();
  }, [files, processUploadQueue]);

  // Calculate batch progress
  useEffect(() => {
    const totalFiles = files.length;
    const completedFiles = files.filter(f => f.status === 'completed').length;
    const failedFiles = files.filter(f => f.status === 'error').length;
    const totalProgress = totalFiles > 0 ? (files.reduce((sum, f) => sum + f.progress, 0) / totalFiles) : 0;
    
    const speeds = files.filter(f => f.uploadSpeed).map(f => f.uploadSpeed!);
    const averageSpeed = speeds.length > 0 ? speeds.reduce((sum, speed) => sum + speed, 0) / speeds.length : 0;
    
    const times = files.filter(f => f.estimatedTimeRemaining).map(f => f.estimatedTimeRemaining!);
    const estimatedTimeRemaining = times.length > 0 ? Math.max(...times) : 0;

    setBatchProgress({
      totalFiles,
      completedFiles,
      failedFiles,
      totalProgress,
      averageSpeed,
      estimatedTimeRemaining,
    });
  }, [files]);

  // Drag and drop handlers
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    if (!e.currentTarget.contains(e.relatedTarget as Node)) {
      setIsDragging(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      addFiles(droppedFiles);
    }
  }, [addFiles]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      addFiles(selectedFiles);
    }
    // Reset input value to allow selecting same file again
    e.target.value = '';
  }, [addFiles]);

  // Reset and close
  const handleClose = useCallback(() => {
    if (isProcessing) {
      if (!confirm('Đang xử lý file. Bạn có chắc muốn đóng?')) {
        return;
      }
      processQueueRef.current = false;
    }
    
    setFiles([]);
    setIsProcessing(false);
    setIsDragging(false);
    onClose();
  }, [isProcessing, onClose]);

  if (!isOpen) return null;

  const hasFiles = files.length > 0;
  const canStartUpload = hasFiles && !isProcessing && files.some(f => f.status === 'pending');
  const canPause = isProcessing;
  const canResume = !isProcessing && files.some(f => f.status === 'paused');
  const hasErrors = files.some(f => f.status === 'error');
  const hasCompleted = files.some(f => f.status === 'completed');

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Enhanced Backdrop */}
      <div 
        className="fixed inset-0 bg-gradient-to-br from-gray-900/85 via-gray-800/75 to-gray-900/85 backdrop-blur-sm transition-all duration-300"
        onClick={handleClose}
      />

      {/* Modal - Larger for batch operations */}
      <div className="flex min-h-full items-center justify-center p-2 sm:p-4">
        <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-4xl transform transition-all animate-modal-appear mx-2">
          {/* Header */}
          <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-100 bg-gradient-to-r from-purple-50 to-pink-50">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Archive className="w-5 h-5 sm:w-6 sm:h-6 text-purple-600" />
              </div>
              <div>
                <h2 className="text-lg sm:text-xl font-semibold text-gray-900">
                  Batch Upload PDF
                </h2>
                <p className="text-xs sm:text-sm text-gray-600">
                  Tải lên nhiều file cùng lúc (tối đa {MAX_FILES} files)
                </p>
              </div>
            </div>
            <button
              onClick={handleClose}
              className="p-2 hover:bg-white rounded-lg transition-all shadow-sm min-w-touch min-h-touch flex items-center justify-center"
              title="Đóng"
            >
              <X className="w-5 h-5 text-gray-500 hover:text-gray-700" />
            </button>
          </div>

          {/* Content */}
          <div className="p-4 sm:p-6 space-y-4 sm:space-y-6 max-h-[70vh] overflow-y-auto">
            {/* Drop Zone */}
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`
                relative border-2 border-dashed rounded-xl p-6 sm:p-8 text-center cursor-pointer overflow-hidden
                transition-all duration-500 ease-in-out min-h-[120px]
                ${isDragging 
                  ? 'border-purple-500 bg-gradient-to-br from-purple-50 via-pink-50 to-indigo-50 scale-[1.02] shadow-xl' 
                  : 'border-gray-300 hover:border-purple-300 hover:bg-gradient-to-br hover:from-gray-50 hover:to-purple-50/30 hover:shadow-md'
                }
                ${files.length >= MAX_FILES ? 'opacity-50 cursor-not-allowed' : ''}
              `}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                disabled={files.length >= MAX_FILES}
              />

              <div className="flex flex-col items-center">
                <div className={`p-4 sm:p-5 rounded-2xl mb-3 sm:mb-4 transition-all duration-500 ${
                  isDragging 
                    ? 'bg-gradient-to-br from-purple-100 to-pink-100 shadow-lg scale-110'
                    : 'bg-gradient-to-br from-gray-100 to-gray-50'
                }`}>
                  <FolderOpen className={`w-10 h-10 sm:w-12 sm:h-12 transition-all duration-300 ${
                    isDragging ? 'text-purple-600 animate-pulse' : 'text-gray-400'
                  }`} />
                </div>
                <div className="text-center space-y-2">
                  <p className={`text-sm sm:text-base font-bold transition-all duration-300 ${
                    isDragging ? 'text-purple-600' : 'text-gray-700'
                  }`}>
                    {files.length >= MAX_FILES 
                      ? `Đã đạt giới hạn ${MAX_FILES} files`
                      : isDragging 
                        ? 'Thả các file PDF vào đây!'
                        : 'Kéo thả nhiều file PDF vào đây'
                    }
                  </p>
                  {files.length < MAX_FILES && (
                    <p className="text-xs sm:text-sm text-gray-500">
                      hoặc <span className="font-semibold text-purple-600">chạm để chọn files</span> (tối đa 50MB/file)
                    </p>
                  )}
                  <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
                    <span>{files.length}/{MAX_FILES} files</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Default Settings */}
            {hasFiles && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Danh mục mặc định
                  </label>
                  <select
                    value={defaultCategory}
                    onChange={(e) => setDefaultCategory(e.target.value)}
                    disabled={isProcessing}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 text-sm disabled:bg-gray-100"
                  >
                    {CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {cat.label}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-700">Gemini OCR</p>
                    <p className="text-xs text-gray-500">Cho PDF scan/ảnh</p>
                  </div>
                  <button
                    onClick={() => !isProcessing && setDefaultUseGemini(!defaultUseGemini)}
                    disabled={isProcessing}
                    className={`relative w-12 h-6 rounded-full transition-all duration-300 ${
                      defaultUseGemini ? 'bg-purple-600' : 'bg-gray-300'
                    }`}
                  >
                    <span
                      className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full shadow-sm transition-transform duration-300 ${
                        defaultUseGemini ? 'translate-x-6' : 'translate-x-0'
                      }`}
                    />
                  </button>
                </div>
              </div>
            )}

            {/* File List */}
            {hasFiles && (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    File Queue ({files.length})
                  </h3>
                  <div className="flex gap-2">
                    {hasCompleted && (
                      <button
                        onClick={clearCompleted}
                        className="text-xs px-3 py-1.5 text-green-600 hover:bg-green-50 border border-green-200 rounded-lg transition-all"
                      >
                        Xóa hoàn thành
                      </button>
                    )}
                    {hasErrors && (
                      <button
                        onClick={retryFailed}
                        className="text-xs px-3 py-1.5 text-red-600 hover:bg-red-50 border border-red-200 rounded-lg transition-all"
                      >
                        Thử lại lỗi
                      </button>
                    )}
                  </div>
                </div>

                {/* Batch Progress */}
                {isProcessing && (
                  <div className="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-3">
                        <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
                        <div>
                          <p className="text-sm font-bold text-gray-900">
                            Đang xử lý batch upload
                          </p>
                          <div className="flex items-center gap-3 text-xs text-gray-600">
                            <span>
                              {batchProgress.completedFiles}/{batchProgress.totalFiles} files
                            </span>
                            {batchProgress.averageSpeed > 0 && (
                              <span className="flex items-center gap-1">
                                <Zap className="w-3 h-3" />
                                {formatSpeed(batchProgress.averageSpeed)}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <span className="text-xl font-bold text-purple-600">
                        {batchProgress.totalProgress.toFixed(0)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-300"
                        style={{ width: `${batchProgress.totalProgress}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Files */}
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {files.map((file) => (
                    <div
                      key={file.id}
                      className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg shadow-sm"
                    >
                      {/* File Icon & Status */}
                      <div className="flex-shrink-0">
                        {file.status === 'completed' && (
                          <CheckCircle className="w-5 h-5 text-green-600" />
                        )}
                        {file.status === 'error' && (
                          <AlertCircle className="w-5 h-5 text-red-600" />
                        )}
                        {(file.status === 'uploading' || file.status === 'processing') && (
                          <Loader2 className="w-5 h-5 animate-spin text-purple-600" />
                        )}
                        {file.status === 'pending' && (
                          <File className="w-5 h-5 text-gray-400" />
                        )}
                        {file.status === 'paused' && (
                          <Pause className="w-5 h-5 text-yellow-600" />
                        )}
                      </div>

                      {/* File Info */}
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {file.file.name}
                        </p>
                        <div className="flex items-center gap-3 text-xs text-gray-500">
                          <span>{formatFileSize(file.file.size)}</span>
                          <span>{file.category}</span>
                          {file.useGemini && <span className="text-blue-600">Gemini</span>}
                        </div>
                        {file.status !== 'pending' && file.status !== 'completed' && (
                          <div className="mt-1">
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-gray-600">{file.message}</span>
                              <span className="text-purple-600 font-medium">{file.progress}%</span>
                            </div>
                            <div className="w-full h-1 bg-gray-200 rounded-full mt-1">
                              <div
                                className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-300"
                                style={{ width: `${file.progress}%` }}
                              />
                            </div>
                          </div>
                        )}
                        {file.error && (
                          <div className="mt-2">
                            <DetailedErrorDisplay
                              error={file.error}
                              onRetry={() => retryFile(file.id)}
                              onCopy={() => {
                                console.log('Error details copied to clipboard');
                              }}
                              className="text-xs"
                            />
                          </div>
                        )}
                        {file.result && (
                          <p className="text-xs text-green-600 mt-1">
                            ✓ {file.result.chunks_created} chunks, {file.result.embeddings_created} embeddings
                          </p>
                        )}
                      </div>

                      {/* Remove Button */}
                      <button
                        onClick={() => removeFile(file.id)}
                        disabled={file.status === 'uploading' || file.status === 'processing'}
                        className="flex-shrink-0 p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-end gap-3 p-4 sm:p-6 border-t border-gray-100 bg-gray-50/50">
            <button
              onClick={handleClose}
              disabled={isProcessing}
              className="px-5 py-3 text-gray-700 font-medium hover:bg-white border border-gray-200 hover:border-gray-300 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm min-h-touch order-2 sm:order-1"
            >
              Đóng
            </button>
            
            <div className="flex gap-2 order-1 sm:order-2">
              {canPause && (
                <button
                  onClick={pauseAll}
                  className="px-4 py-3 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg transition-all min-h-touch flex items-center gap-2 font-medium"
                >
                  <Pause className="w-4 h-4" />
                  Tạm dừng
                </button>
              )}
              
              {canResume && (
                <button
                  onClick={resumeAll}
                  className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-all min-h-touch flex items-center gap-2 font-medium"
                >
                  <Play className="w-4 h-4" />
                  Tiếp tục
                </button>
              )}
              
              {canStartUpload && (
                <button
                  onClick={startBatchUpload}
                  className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg transition-all min-h-touch flex items-center gap-2 font-semibold shadow-md hover:shadow-lg"
                >
                  <Upload className="w-4 h-4" />
                  Upload All ({files.filter(f => f.status === 'pending').length})
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BatchUploadModal;