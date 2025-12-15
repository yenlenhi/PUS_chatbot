'use client';

import React from 'react';

interface FunnelChartProps {
  data: { stage: string; count: number; percentage?: number | null; conversion_rate?: number | null }[];
  className?: string;
}

const FunnelChart: React.FC<FunnelChartProps> = ({ data, className = '' }) => {
  if (!data || data.length === 0) {
    return (
      <div className={`text-center text-gray-500 py-4 ${className}`}>
        Không có dữ liệu
      </div>
    );
  }

  const maxCount = Math.max(...data.map((d) => d.count || 0), 1);

  const colors = [
    'bg-red-500',
    'bg-red-400',
    'bg-orange-400',
    'bg-yellow-400',
  ];

  return (
    <div className={`space-y-3 ${className}`}>
      {data.map((item, index) => (
        <div key={index} className="relative">
          <div className="flex items-center space-x-4">
            {/* Stage label */}
            <div className="w-40 flex-shrink-0">
              <span className="text-sm font-medium text-gray-700">
                {item.stage}
              </span>
            </div>

            {/* Funnel bar */}
            <div className="flex-1 relative">
              <div
                className={`${colors[index % colors.length]} h-8 rounded-r-lg transition-all duration-500 flex items-center justify-end pr-3`}
                style={{
                  width: `${((item.count || 0) / maxCount) * 100}%`,
                  minWidth: '60px',
                }}
              >
                <span className="text-white text-sm font-bold">
                  {(item.count || 0).toLocaleString()}
                </span>
              </div>
            </div>

            {/* Percentage */}
            <div className="w-20 text-right flex-shrink-0">
              <span className="text-sm font-medium text-gray-900">
                {(item.percentage ?? 0).toFixed(1)}%
              </span>
              {item.conversion_rate != null && index > 0 && (
                <span className="block text-xs text-gray-500">
                  ↓ {item.conversion_rate.toFixed(1)}%
                </span>
              )}
            </div>
          </div>

          {/* Connection line */}
          {index < data.length - 1 && (
            <div className="ml-40 pl-4 h-3 flex items-center">
              <div className="w-px h-full bg-gray-300" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default FunnelChart;
