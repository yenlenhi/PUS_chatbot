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
    <div className={`bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-all duration-300 ${className}`}>
      <div className="flex items-start justify-between mb-4">
        <div className={`${iconColor} p-3 rounded-lg shadow-sm`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
        {change !== undefined && (
          <div className={`flex items-center space-x-1 ${trendColor}`}>
            <TrendIcon className="w-4 h-4" />
            <span className="text-sm font-medium">
              {change > 0 ? '+' : ''}{change.toFixed(1)}%
            </span>
          </div>
        )}
      </div>
      
      <h3 className="text-gray-600 text-sm mb-1">{title}</h3>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      
      {(subtitle || changeLabel) && (
        <p className="text-xs text-gray-500 mt-2">
          {changeLabel || subtitle}
        </p>
      )}
    </div>
  );
};

export default MetricCard;
