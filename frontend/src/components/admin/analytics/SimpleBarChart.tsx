'use client';

import React from 'react';

interface SimpleBarChartProps {
  data: { label: string; value: number; color?: string }[];
  height?: number;
  showValues?: boolean;
  showLabels?: boolean;
  horizontal?: boolean;
  className?: string;
}

const SimpleBarChart: React.FC<SimpleBarChartProps> = ({
  data,
  height = 180,
  showValues = true,
  showLabels = true,
  horizontal = false,
  className = '',
}) => {
  const maxValue = Math.max(...data.map((d) => d.value), 1);

  if (horizontal) {
    return (
      <div className={`space-y-3 ${className}`}>
        {data.map((item, index) => (
          <div key={index} className="flex items-center space-x-3">
            {showLabels && (
              <span className="text-sm text-gray-600 w-20 truncate" title={item.label}>
                {item.label}
              </span>
            )}
            <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
              <div
                className={`h-3 rounded-full transition-all duration-500 ${
                  item.color || 'bg-gradient-to-r from-red-500 to-red-600'
                }`}
                style={{ width: `${(item.value / maxValue) * 100}%` }}
              />
            </div>
            {showValues && (
              <span className="text-sm font-medium text-gray-900 w-12 text-right">
                {item.value.toLocaleString()}
              </span>
            )}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`flex items-end justify-between space-x-2 ${className}`} style={{ height }}>
      {data.map((item, index) => (
        <div key={index} className="flex flex-col items-center flex-1">
          <div
            className="w-full relative group"
            style={{ height: `${height - 24}px` }}
          >
            <div
              className={`absolute bottom-0 left-1/2 -translate-x-1/2 w-8 max-w-full rounded-t transition-all duration-500 ${
                item.color || 'bg-gradient-to-t from-red-600 to-red-400'
              }`}
              style={{ height: `${(item.value / maxValue) * 100}%` }}
            >
              {showValues && (
                <div className="absolute -top-6 left-1/2 -translate-x-1/2 text-xs font-medium text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                  {item.value.toLocaleString()}
                </div>
              )}
            </div>
          </div>
          {showLabels && (
            <span className="text-xs text-gray-600 mt-1 text-center truncate w-full" title={item.label}>
              {item.label}
            </span>
          )}
        </div>
      ))}
    </div>
  );
};

export default SimpleBarChart;
