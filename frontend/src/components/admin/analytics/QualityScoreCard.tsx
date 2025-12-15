'use client';

import React from 'react';
import { Star, ThumbsUp, ThumbsDown, AlertTriangle } from 'lucide-react';

interface QualityScore {
  category: string;
  score: number;
  weight: number;
}

interface QualityScoreCardProps {
  overallScore: number;
  breakdown: QualityScore[];
  className?: string;
}

const QualityScoreCard: React.FC<QualityScoreCardProps> = ({
  overallScore,
  breakdown,
  className = '',
}) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBackground = (score: number) => {
    if (score >= 80) return 'bg-green-500';
    if (score >= 60) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'Tốt';
    if (score >= 60) return 'Khá';
    if (score >= 40) return 'Trung bình';
    return 'Cần cải thiện';
  };

  const getIcon = (category: string) => {
    if (category.includes('hài lòng')) return ThumbsUp;
    if (category.includes('phản hồi')) return Star;
    if (category.includes('fallback')) return AlertTriangle;
    return Star;
  };

  // Calculate the circumference and offset for the circular progress
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (overallScore / 100) * circumference;

  return (
    <div className={`${className}`}>
      {/* Overall Score */}
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background circle */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke="#e5e7eb"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress circle */}
            <circle
              cx="64"
              cy="64"
              r={radius}
              stroke={overallScore >= 80 ? '#22c55e' : overallScore >= 60 ? '#eab308' : '#ef4444'}
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-3xl font-bold ${getScoreColor(overallScore)}`}>
              {overallScore.toFixed(0)}
            </span>
            <span className="text-xs text-gray-500">/ 100</span>
          </div>
        </div>
      </div>

      <div className="text-center mb-6">
        <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium text-white ${getScoreBackground(overallScore)}`}>
          {getScoreLabel(overallScore)}
        </span>
      </div>

      {/* Breakdown */}
      <div className="space-y-4">
        {breakdown.map((item, index) => {
          const Icon = getIcon(item.category);
          return (
            <div key={index} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Icon className="w-4 h-4 text-gray-400" />
                  <span className="text-sm text-gray-700">{item.category}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`text-sm font-medium ${getScoreColor(item.score)}`}>
                    {item.score.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-400">
                    ({(item.weight * 100).toFixed(0)}%)
                  </span>
                </div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${getScoreBackground(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default QualityScoreCard;
