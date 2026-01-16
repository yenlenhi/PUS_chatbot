'use client';

import React from 'react';
import { CheckCircle, Loader2, Clock, Zap, Upload, FileCheck, Database, Sparkles } from 'lucide-react';

type StatusColor = 'blue' | 'green' | 'red' | 'yellow' | 'gray';

interface RealtimeStatusProps {
  status: 'uploading' | 'processing' | 'completed' | 'error' | 'paused';
  progress: number;
  message: string;
  color?: StatusColor;
  uploadSpeed?: number;
  estimatedTimeRemaining?: number;
  currentStepIndex?: number;
}

const PROCESSING_STEPS = [
  { key: 'upload', label: 'Upload', icon: Upload },
  { key: 'validate', label: 'Kiểm tra', icon: FileCheck },
  { key: 'process', label: 'Xử lý', icon: Database },
  { key: 'complete', label: 'Hoàn thành', icon: Sparkles },
];

const RealtimeStatus: React.FC<RealtimeStatusProps> = ({
  status,
  progress,
  message,
  color = 'blue',
  uploadSpeed,
  estimatedTimeRemaining,
  currentStepIndex = 0
}) => {
  const isActive = status === 'uploading' || status === 'processing';

  const formatSpeed = (speed: number): string => {
    if (speed < 1024) return `${speed.toFixed(1)} B/s`;
    if (speed < 1024 * 1024) return `${(speed / 1024).toFixed(1)} KB/s`;
    return `${(speed / 1024 / 1024).toFixed(1)} MB/s`;
  };

  const formatTime = (seconds: number): string => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    return `${Math.round(seconds / 60)}m`;
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5" />;
      case 'uploading':
      case 'processing':
        return <Loader2 className="w-5 h-5 animate-spin" />;
      case 'error':
        return <CheckCircle className="w-5 h-5" />;
      case 'paused':
        return <CheckCircle className="w-5 h-5" />;
      default:
        return <CheckCircle className="w-5 h-5" />;
    }
  };

  return (
    <div className={`p-4 rounded-lg border-2 transition-all duration-500 ${
      color === 'blue' ? 'bg-blue-50 border-blue-200' :
      color === 'green' ? 'bg-green-50 border-green-200' :
      color === 'red' ? 'bg-red-50 border-red-200' :
      color === 'yellow' ? 'bg-yellow-50 border-yellow-200' :
      'bg-gray-50 border-gray-200'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${
            color === 'blue' ? 'bg-blue-100 text-blue-600' :
            color === 'green' ? 'bg-green-100 text-green-600' :
            color === 'red' ? 'bg-red-100 text-red-600' :
            color === 'yellow' ? 'bg-yellow-100 text-yellow-600' :
            'bg-gray-100 text-gray-600'
          }`}>
            {getStatusIcon()}
          </div>
          <div>
            <p className="text-sm font-bold text-gray-900">{message}</p>
            <div className="flex items-center gap-3 text-xs text-gray-600 mt-1">
              {uploadSpeed && isActive && (
                <span className="flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  {formatSpeed(uploadSpeed)}
                </span>
              )}
              {estimatedTimeRemaining && estimatedTimeRemaining > 0 && isActive && (
                <span className="flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  Còn {formatTime(estimatedTimeRemaining)}
                </span>
              )}
            </div>
          </div>
        </div>
        <div className="text-right">
          <span className={`text-2xl font-bold ${
            color === 'blue' ? 'text-blue-600' :
            color === 'green' ? 'text-green-600' :
            color === 'red' ? 'text-red-600' :
            color === 'yellow' ? 'text-yellow-600' :
            'text-gray-600'
          }`}>
            {progress}%
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-4">
        <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ease-out relative overflow-hidden ${
              color === 'blue' ? 'bg-gradient-to-r from-blue-500 to-cyan-500' :
              color === 'green' ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
              color === 'red' ? 'bg-gradient-to-r from-red-500 to-rose-500' :
              color === 'yellow' ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
              'bg-gradient-to-r from-gray-500 to-gray-600'
            }`}
            style={{ width: `${progress}%` }}
          >
            {/* Shimmer effect for active states */}
            {isActive && (
              <div className="absolute inset-0 -skew-x-12 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer" />
            )}
          </div>
        </div>
      </div>

      {/* Processing Steps */}
      {isActive && (
        <div className="space-y-2">
          <p className="text-xs font-semibold text-gray-700 mb-2">Tiến trình xử lý:</p>
          <div className="flex items-center justify-between">
            {PROCESSING_STEPS.map((step, index) => {
              const isCompleted = index < currentStepIndex;
              const isCurrent = index === currentStepIndex;
              const isPending = index > currentStepIndex;
              
              const StepIcon = step.icon;
              
              return (
                <div key={step.key} className="flex flex-col items-center gap-1">
                  <div className={`p-1.5 rounded-full transition-all duration-300 ${
                    isCompleted ? 'bg-green-100 text-green-600' :
                    isCurrent ? (color === 'blue' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600') :
                    'bg-gray-100 text-gray-400'
                  }`}>
                    {isCompleted ? (
                      <CheckCircle className="w-3 h-3" />
                    ) : isCurrent ? (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    ) : (
                      <StepIcon className="w-3 h-3" />
                    )}
                  </div>
                  <span className={`text-xs font-medium ${
                    isCompleted ? 'text-green-600' :
                    isCurrent ? (color === 'blue' ? 'text-blue-600' : 'text-gray-700') :
                    'text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Status-specific Additional Info */}
      {status === 'completed' && (
        <div className="mt-3 p-2 bg-green-100/50 rounded-lg">
          <p className="text-xs text-green-700 font-medium">✓ Upload hoàn thành thành công!</p>
        </div>
      )}
      
      {status === 'error' && (
        <div className="mt-3 p-2 bg-red-100/50 rounded-lg">
          <p className="text-xs text-red-700 font-medium">✗ Có lỗi xảy ra khi xử lý</p>
        </div>
      )}
      
      {status === 'paused' && (
        <div className="mt-3 p-2 bg-yellow-100/50 rounded-lg">
          <p className="text-xs text-yellow-700 font-medium">⏸ Upload đã tạm dừng</p>
        </div>
      )}
    </div>
  );
};

export default RealtimeStatus;