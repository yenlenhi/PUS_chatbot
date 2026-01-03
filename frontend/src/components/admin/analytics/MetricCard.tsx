'use client';

import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon: LucideIcon;
  iconColor?: string;
  trend?: 'up' | 'down' | 'neutral';
  subtitle?: string;
  className?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon: Icon,
  iconColor = 'bg-red-500',
  trend,
  subtitle,
  className = '',
}) => {
  const getTrendIcon = () => {
    if (!trend && change !== undefined) {
      if (change > 0) return TrendingUp;
      if (change < 0) return TrendingDown;
      return Minus;
    }
    switch (trend) {
      case 'up':
        return TrendingUp;
      case 'down':
        return TrendingDown;
      default:
        return Minus;
    }
  };

  const getTrendColor = () => {
    const actualTrend = trend || (change !== undefined ? (change > 0 ? 'up' : change < 0 ? 'down' : 'neutral') : 'neutral');
    switch (actualTrend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const TrendIcon = getTrendIcon();
  const trendColor = getTrendColor();

  return (
    <div className={`bg-white rounded-lg sm:rounded-xl shadow-md border border-gray-200 p-3 sm:p-4 lg:p-6 hover:shadow-lg transition-all duration-300 ${className}`}>
      <div className="flex items-start justify-between mb-2 sm:mb-3 lg:mb-4">
        <div className={`${iconColor} p-2 sm:p-2.5 lg:p-3 rounded-lg shadow-sm`}>
          <Icon className="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6 text-white" />
        </div>
        {change !== undefined && (
          <div className={`flex items-center space-x-1 ${trendColor}`}>
            <TrendIcon className="w-3 h-3 sm:w-4 sm:h-4" />
            <span className="text-xs sm:text-sm font-medium">
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      
      <h3 className="text-gray-600 text-xs sm:text-sm mb-1 line-clamp-2">{title}</h3>
      <p className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 truncate">{value}</p>
      
      {(subtitle || changeLabel) && (
        <p className="text-xs text-gray-500 mt-1 sm:mt-2 line-clamp-2">
          {changeLabel || subtitle}
        </p>
      )}
    </div>
  );
};

export default MetricCard;
