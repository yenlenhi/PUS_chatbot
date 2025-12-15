'use client';

import React from 'react';

interface SimplePieChartProps {
  data: { label: string; value: number; color: string }[];
  size?: number;
  showLegend?: boolean;
  showPercentage?: boolean;
  className?: string;
}

const SimplePieChart: React.FC<SimplePieChartProps> = ({
  data,
  size = 180,
  showLegend = true,
  showPercentage = true,
  className = '',
}) => {
  const total = data.reduce((sum, d) => sum + d.value, 0) || 1;
  const radius = 40;
  const center = 50;

  let currentAngle = -90; // Start from top

  const segments = data.map((d) => {
    const percentage = (d.value / total) * 100;
    const angle = (d.value / total) * 360;
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    currentAngle = endAngle;

    // Calculate arc path
    const startRad = (startAngle * Math.PI) / 180;
    const endRad = (endAngle * Math.PI) / 180;

    const x1 = center + radius * Math.cos(startRad);
    const y1 = center + radius * Math.sin(startRad);
    const x2 = center + radius * Math.cos(endRad);
    const y2 = center + radius * Math.sin(endRad);

    const largeArc = angle > 180 ? 1 : 0;

    const pathD = `M ${center} ${center} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;

    return {
      ...d,
      percentage,
      pathD,
    };
  });

  return (
    <div className={`flex items-center space-x-6 ${className}`}>
      {/* Pie Chart */}
      <div style={{ width: size, height: size }} className="flex-shrink-0">
        <svg viewBox="0 0 100 100" className="w-full h-full transform -rotate-0">
          {segments.map((segment, index) => (
            <g key={index} className="group cursor-pointer">
              <path
                d={segment.pathD}
                fill={segment.color}
                className="transition-all duration-200 hover:opacity-80"
                stroke="white"
                strokeWidth="0.5"
              />
            </g>
          ))}
          {/* Center circle for donut effect */}
          <circle cx={center} cy={center} r={radius * 0.6} fill="white" />
          {/* Center text */}
          <text
            x={center}
            y={center - 5}
            textAnchor="middle"
            className="text-xs font-bold fill-gray-900"
          >
            {total.toLocaleString()}
          </text>
          <text
            x={center}
            y={center + 8}
            textAnchor="middle"
            className="text-[8px] fill-gray-500"
          >
            Tổng
          </text>
        </svg>
      </div>

      {/* Legend */}
      {showLegend && (
        <div className="flex-1 space-y-2">
          {segments.map((segment, index) => (
            <div key={index} className="flex items-center space-x-2">
              <div
                className="w-3 h-3 rounded-full flex-shrink-0"
                style={{ backgroundColor: segment.color }}
              />
              <span className="text-sm text-gray-700 flex-1 truncate">
                {segment.label}
              </span>
              {showPercentage && (
                <span className="text-sm font-medium text-gray-900">
                  {segment.percentage.toFixed(1)}%
                </span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SimplePieChart;
