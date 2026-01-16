'use client';

import React from 'react';
import { AlertCircle, Wifi, Server, FileX, Shield, Clock, RefreshCw, ExternalLink, Copy } from 'lucide-react';

export interface ErrorDetails {
  code: string;
  category: 'network' | 'server' | 'file' | 'permission' | 'timeout' | 'unknown';
  title: string;
  message: string;
  suggestion: string;
  retryable: boolean;
  technicalDetails?: string;
}

interface DetailedErrorDisplayProps {
  error: string;
  onRetry?: () => void;
  onCopy?: () => void;
  className?: string;
}

const DetailedErrorDisplay: React.FC<DetailedErrorDisplayProps> = ({
  error,
  onRetry,
  onCopy,
  className = ''
}) => {
  const parseError = (errorMessage: string): ErrorDetails => {
    const lowerError = errorMessage.toLowerCase();
    
    // Network errors
    if (lowerError.includes('fetch') || lowerError.includes('network') || lowerError.includes('connection')) {
      return {
        code: 'NETWORK_ERROR',
        category: 'network',
        title: 'Lỗi kết nối mạng',
        message: 'Không thể kết nối đến server',
        suggestion: 'Kiểm tra kết nối internet và thử lại',
        retryable: true,
        technicalDetails: errorMessage
      };
    }
    
    // Server errors (5xx)
    if (lowerError.includes('500') || lowerError.includes('internal server') || lowerError.includes('server error')) {
      return {
        code: 'SERVER_ERROR',
        category: 'server',
        title: 'Lỗi server',
        message: 'Server đang gặp sự cố',
        suggestion: 'Vui lòng thử lại sau ít phút',
        retryable: true,
        technicalDetails: errorMessage
      };
    }
    
    // File size errors
    if (lowerError.includes('file quá lớn') || lowerError.includes('file size') || lowerError.includes('too large')) {
      return {
        code: 'FILE_SIZE_ERROR',
        category: 'file',
        title: 'File quá lớn',
        message: 'Kích thước file vượt quá giới hạn cho phép',
        suggestion: 'Chọn file có kích thước dưới 50MB hoặc nén file trước khi upload',
        retryable: false,
        technicalDetails: errorMessage
      };
    }
    
    // File format errors
    if (lowerError.includes('file format') || lowerError.includes('định dạng') || lowerError.includes('không hỗ trợ')) {
      return {
        code: 'FILE_FORMAT_ERROR',
        category: 'file',
        title: 'Định dạng file không hỗ trợ',
        message: 'Chỉ chấp nhận file PDF',
        suggestion: 'Chuyển đổi file sang định dạng PDF trước khi upload',
        retryable: false,
        technicalDetails: errorMessage
      };
    }
    
    // Permission errors
    if (lowerError.includes('permission') || lowerError.includes('unauthorized') || lowerError.includes('403')) {
      return {
        code: 'PERMISSION_ERROR',
        category: 'permission',
        title: 'Không có quyền truy cập',
        message: 'Bạn không có quyền upload file',
        suggestion: 'Liên hệ admin để được cấp quyền',
        retryable: false,
        technicalDetails: errorMessage
      };
    }
    
    // Timeout errors
    if (lowerError.includes('timeout') || lowerError.includes('timed out')) {
      return {
        code: 'TIMEOUT_ERROR',
        category: 'timeout',
        title: 'Hết thời gian chờ',
        message: 'Upload mất quá nhiều thời gian',
        suggestion: 'Kiểm tra kết nối mạng và thử upload file nhỏ hơn',
        retryable: true,
        technicalDetails: errorMessage
      };
    }
    
    // PDF processing errors
    if (lowerError.includes('pdf') || lowerError.includes('corrupt') || lowerError.includes('damaged')) {
      return {
        code: 'PDF_PROCESSING_ERROR',
        category: 'file',
        title: 'Lỗi xử lý PDF',
        message: 'File PDF bị lỗi hoặc không thể đọc được',
        suggestion: 'Kiểm tra lại file PDF hoặc thử file khác',
        retryable: false,
        technicalDetails: errorMessage
      };
    }
    
    // Generic server errors
    if (lowerError.includes('upload failed') && lowerError.includes('status')) {
      const statusMatch = errorMessage.match(/status\s+(\d+)/);
      const status = statusMatch ? statusMatch[1] : 'unknown';
      
      return {
        code: `HTTP_${status}`,
        category: 'server',
        title: `Lỗi HTTP ${status}`,
        message: 'Server trả về lỗi',
        suggestion: 'Thử lại sau hoặc liên hệ support',
        retryable: status.startsWith('5'),
        technicalDetails: errorMessage
      };
    }
    
    // Default unknown error
    return {
      code: 'UNKNOWN_ERROR',
      category: 'unknown',
      title: 'Lỗi không xác định',
      message: errorMessage || 'Có lỗi xảy ra',
      suggestion: 'Thử lại hoặc liên hệ support nếu lỗi tiếp tục xảy ra',
      retryable: true,
      technicalDetails: errorMessage
    };
  };

  const getErrorIcon = (category: string) => {
    switch (category) {
      case 'network':
        return <Wifi className="w-5 h-5" />;
      case 'server':
        return <Server className="w-5 h-5" />;
      case 'file':
        return <FileX className="w-5 h-5" />;
      case 'permission':
        return <Shield className="w-5 h-5" />;
      case 'timeout':
        return <Clock className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  const getErrorColors = (category: string) => {
    switch (category) {
      case 'network':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-200',
          icon: 'text-orange-600',
          iconBg: 'bg-orange-100',
          title: 'text-orange-800',
          message: 'text-orange-700'
        };
      case 'server':
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          iconBg: 'bg-red-100',
          title: 'text-red-800',
          message: 'text-red-700'
        };
      case 'file':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-200',
          icon: 'text-blue-600',
          iconBg: 'bg-blue-100',
          title: 'text-blue-800',
          message: 'text-blue-700'
        };
      case 'permission':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-200',
          icon: 'text-yellow-600',
          iconBg: 'bg-yellow-100',
          title: 'text-yellow-800',
          message: 'text-yellow-700'
        };
      default:
        return {
          bg: 'bg-red-50',
          border: 'border-red-200',
          icon: 'text-red-600',
          iconBg: 'bg-red-100',
          title: 'text-red-800',
          message: 'text-red-700'
        };
    }
  };

  const errorDetails = parseError(error);
  const colors = getErrorColors(errorDetails.category);

  const copyToClipboard = () => {
    const debugInfo = `
Error Code: ${errorDetails.code}
Category: ${errorDetails.category}
Message: ${errorDetails.message}
Technical Details: ${errorDetails.technicalDetails}
Timestamp: ${new Date().toISOString()}
    `.trim();
    
    navigator.clipboard.writeText(debugInfo);
    onCopy?.();
  };

  return (
    <div className={`${colors.bg} ${colors.border} border-2 rounded-lg p-4 space-y-3 ${className}`}>
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className={`${colors.iconBg} p-2 rounded-lg flex-shrink-0`}>
          {getErrorIcon(errorDetails.category)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className={`font-semibold ${colors.title}`}>
                {errorDetails.title}
              </h3>
              <p className={`text-sm mt-1 ${colors.message}`}>
                {errorDetails.message}
              </p>
            </div>
            <div className="flex gap-1 flex-shrink-0">
              <button
                onClick={copyToClipboard}
                className="p-1.5 hover:bg-white/50 rounded transition-colors"
                title="Copy error details"
              >
                <Copy className="w-4 h-4 text-gray-500" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Error Code */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-mono bg-white/70 px-2 py-1 rounded border">
          {errorDetails.code}
        </span>
      </div>

      {/* Suggestion */}
      <div className={`text-sm ${colors.message} bg-white/30 p-3 rounded-lg border border-white/50`}>
        <p className="font-medium mb-1">💡 Gợi ý khắc phục:</p>
        <p>{errorDetails.suggestion}</p>
      </div>

      {/* Action buttons */}
      <div className="flex gap-2 pt-2">
        {errorDetails.retryable && onRetry && (
          <button
            onClick={onRetry}
            className={`px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium ${colors.title} transition-colors flex items-center gap-2`}
          >
            <RefreshCw className="w-4 h-4" />
            Thử lại
          </button>
        )}
        
        <button
          onClick={() => window.open('https://docs.uni-bot.com/troubleshooting', '_blank')}
          className="px-4 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-lg text-sm font-medium text-gray-600 transition-colors flex items-center gap-2"
        >
          <ExternalLink className="w-4 h-4" />
          Hỗ trợ
        </button>
      </div>

      {/* Technical details (expandable) */}
      {errorDetails.technicalDetails && (
        <details className="mt-2">
          <summary className="text-xs text-gray-500 cursor-pointer hover:text-gray-700">
            Chi tiết kỹ thuật
          </summary>
          <pre className="text-xs font-mono bg-white/50 p-2 mt-1 rounded border overflow-x-auto">
            {errorDetails.technicalDetails}
          </pre>
        </details>
      )}
    </div>
  );
};

export default DetailedErrorDisplay;