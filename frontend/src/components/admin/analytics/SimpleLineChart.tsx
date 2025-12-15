'use client';

import React from 'react';

interface SimpleLineChartProps {
  data: { label: string; value: number }[];
  height?: number;
  showPoints?: boolean;
  showLabels?: boolean;
  showGrid?: boolean;
  color?: string;
  fillColor?: string;
  className?: string;
}

const SimpleLineChart: React.FC<SimpleLineChartProps> = ({
  data,
  height = 180,
  showPoints = true,
  showLabels = true,
  showGrid = true,
  color = '#dc2626',
  fillColor = 'rgba(220, 38, 38, 0.1)',
  className = '',
}) => {
  if (data.length === 0) return null;

  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const minValue = Math.min(...data.map((d) => d.value), 0);
  const range = maxValue - minValue || 1;
  
  const padding = 10;
  const chartHeight = height - padding * 2;
  const chartWidth = 100;

  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * 100;
    const y = ((maxValue - d.value) / range) * 100;
    return { x, y, value: d.value, label: d.label };
  });

  const pathD = points
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`)
    .join(' ');

  const areaD = `${pathD} L ${100} ${100} L ${0} ${100} Z`;

  return (
    <div className={`w-full ${className}`}>
      <svg
        viewBox="0 0 100 100"
        className="w-full"
        style={{ height: `${height}px`, maxHeight: '240px' }}
        preserveAspectRatio="none"
      >
        {/* Grid lines */}
        {showGrid && (
          <g className="text-gray-200">
            {[0, 25, 50, 75, 100].map((y) => (
              <line
                key={y}
                x1="0"
                y1={y}
                x2="100"
                y2={y}
                stroke="currentColor"
                strokeWidth="0.5"
                strokeDasharray="2,2"
              />
            ))}
          </g>
        )}

        {/* Area fill */}
        <path d={areaD} fill={fillColor} />

        {/* Line */}
        <path
          d={pathD}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Points */}
        {showPoints &&
          points.map((p, i) => (
            <g key={i} className="group">
              <circle
                cx={p.x}
                cy={p.y}
                r="4"
                fill="white"
                stroke={color}
                strokeWidth="2"
                className="transition-all duration-200 hover:r-6"
              />
              {/* Tooltip */}
              <g className="opacity-0 group-hover:opacity-100 transition-opacity">
                <rect
                  x={p.x - 15}
                  y={p.y - 25}
                  width="30"
                  height="18"
                  fill="rgba(0,0,0,0.8)"
                  rx="3"
                />
                <text
                  x={p.x}
                  y={p.y - 12}
                  textAnchor="middle"
                  fill="white"
                  fontSize="8"
                  fontWeight="bold"
                >
                  {p.value.toLocaleString()}
                </text>
              </g>
            </g>
          ))}
      </svg>

      {/* Labels */}
      {showLabels && (
        <div className="flex justify-between mt-2 px-1">
          {data.map((d, i) => (
            <span
              key={i}
              className="text-xs text-gray-500 truncate"
              style={{ maxWidth: `${100 / data.length}%` }}
              title={d.label}
            >
              {d.label}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export default SimpleLineChart;
