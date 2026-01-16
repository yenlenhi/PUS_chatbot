'use client';

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, Database, FileText, Clock, 
  Zap, CheckCircle, AlertCircle, Activity,
  BarChart3, PieChart, Users, Upload
} from 'lucide-react';

interface QuickStatsProps {
  totalDocuments: number;
  activeDocuments: number;
  totalChunks: number;
  totalSize: number;
  recentUploads?: number;
  processingQueue?: number;
  averageProcessingTime?: number;
  uploadSuccess?: number;
  className?: string;
}

const QuickStats: React.FC<QuickStatsProps> = ({
  totalDocuments,
  activeDocuments,
  totalChunks,
  totalSize,
  recentUploads = 0,
  processingQueue = 0,
  averageProcessingTime = 0,
  uploadSuccess = 0,
  className = '',
}) => {
  const [animatedValues, setAnimatedValues] = useState({
    totalDocuments: 0,
    activeDocuments: 0,
    totalChunks: 0,
    totalSize: 0,
  });

  // Animate counter values
  useEffect(() => {
    const duration = 1000; // 1 second
    const steps = 60;
    const stepTime = duration / steps;

    let currentStep = 0;

    const interval = setInterval(() => {
      currentStep++;
      const progress = currentStep / steps;
      const easeOut = 1 - Math.pow(1 - progress, 3);

      setAnimatedValues({
        totalDocuments: Math.floor(totalDocuments * easeOut),
        activeDocuments: Math.floor(activeDocuments * easeOut),
        totalChunks: Math.floor(totalChunks * easeOut),
        totalSize: Math.floor(totalSize * easeOut),
      });

      if (currentStep >= steps) {
        clearInterval(interval);
        setAnimatedValues({
          totalDocuments,
          activeDocuments,
          totalChunks,
          totalSize,
        });
      }
    }, stepTime);

    return () => clearInterval(interval);
  }, [totalDocuments, activeDocuments, totalChunks, totalSize]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(1)} GB`;
  };

  const formatTime = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatNumber = (num: number) => {
    if (num < 1000) return num.toString();
    if (num < 1000000) return `${(num / 1000).toFixed(1)}K`;
    return `${(num / 1000000).toFixed(1)}M`;
  };

  const getSuccessRate = () => {
    if (totalDocuments === 0) return 0;
    return Math.round((uploadSuccess / totalDocuments) * 100);
  };

  // HardDrive icon component
  const HardDrive = ({ className }: { className?: string }) => (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
      <line x1="8" y1="21" x2="16" y2="21"></line>
      <line x1="12" y1="17" x2="12" y2="21"></line>
    </svg>
  );

  const stats = [
    {
      title: 'Tổng tài liệu',
      value: animatedValues.totalDocuments,
      icon: FileText,
      color: 'blue',
      bgColor: 'bg-blue-50',
      iconBg: 'bg-blue-100',
      textColor: 'text-blue-600',
      formatter: (val: number) => formatNumber(val),
    },
    {
      title: 'Đang hoạt động',
      value: animatedValues.activeDocuments,
      icon: CheckCircle,
      color: 'green',
      bgColor: 'bg-green-50',
      iconBg: 'bg-green-100',
      textColor: 'text-green-600',
      formatter: (val: number) => formatNumber(val),
    },
    {
      title: 'Tổng chunks',
      value: animatedValues.totalChunks,
      icon: Database,
      color: 'purple',
      bgColor: 'bg-purple-50',
      iconBg: 'bg-purple-100',
      textColor: 'text-purple-600',
      formatter: (val: number) => formatNumber(val),
    },
    {
      title: 'Dung lượng',
      value: animatedValues.totalSize,
      icon: HardDrive,
      color: 'orange',
      bgColor: 'bg-orange-50',
      iconBg: 'bg-orange-100',
      textColor: 'text-orange-600',
      formatter: (val: number) => formatFileSize(val),
    },
  ];

  const liveStats = [
    {
      title: 'Upload gần đây',
      value: recentUploads,
      icon: Upload,
      color: 'text-blue-600',
    },
    {
      title: 'Đang xử lý',
      value: processingQueue,
      icon: Activity,
      color: 'text-yellow-600',
    },
    {
      title: 'Thời gian TB',
      value: averageProcessingTime,
      icon: Clock,
      color: 'text-gray-600',
      formatter: formatTime,
    },
    {
      title: 'Tỷ lệ thành công',
      value: getSuccessRate(),
      icon: TrendingUp,
      color: 'text-green-600',
      suffix: '%',
    },
  ];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Main Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={stat.title}
              className={`${stat.bgColor} rounded-xl p-4 border border-gray-100 shadow-sm hover:shadow-md transition-all duration-300 hover:scale-[1.02]`}
              style={{
                animationDelay: `${index * 100}ms`,
                animation: 'slideInFromBottom 0.5s ease-out forwards',
              }}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-600 mb-1">
                    {stat.title}
                  </p>
                  <p className={`text-2xl font-bold ${stat.textColor}`}>
                    {stat.formatter(stat.value)}
                  </p>
                </div>
                <div className={`${stat.iconBg} p-2 rounded-lg`}>
                  <Icon className={`w-6 h-6 ${stat.textColor}`} />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Live Stats */}
      <div className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <Activity className="w-5 h-5 text-blue-600" />
            Thống kê thời gian thực
          </h3>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span className="text-sm text-gray-500">Live</span>
          </div>
        </div>
        
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {liveStats.map((stat, index) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.title}
                className="text-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-all duration-200"
              >
                <Icon className={`w-5 h-5 mx-auto mb-2 ${stat.color}`} />
                <p className="text-xs text-gray-600 mb-1">{stat.title}</p>
                <p className={`text-xl font-bold ${stat.color}`}>
                  {stat.formatter ? stat.formatter(stat.value) : stat.value}
                  {stat.suffix || ''}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default QuickStats;