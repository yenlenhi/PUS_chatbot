'use client';

import React, { useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from 'recharts';

interface InteractiveLineChartProps {
  data: Array<{ date: string; value: number }>;
  color?: string;
  title?: string;
  height?: number;
  showBrush?: boolean;
  allowZoom?: boolean;
}

export default function InteractiveLineChart({
  data,
  color = '#9333ea',
  title,
  height = 300,
  showBrush = true,
  allowZoom = true,
}: InteractiveLineChartProps) {
  const [zoomDomain, setZoomDomain] = useState<[number, number] | null>(null);

  // Transform data for recharts
  const chartData = data.map((item) => ({
    name: item.date,
    value: item.value,
  }));

  const handleZoom = (domain: any) => {
    if (allowZoom && domain) {
      setZoomDomain([domain.startIndex, domain.endIndex]);
    }
  };

  const handleResetZoom = () => {
    setZoomDomain(null);
  };

  return (
    <div className="w-full">
      {title && (
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-gray-700">{title}</h3>
          {zoomDomain && (
            <button
              onClick={handleResetZoom}
              className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded transition-colors"
            >
              Reset Zoom
            </button>
          )}
        </div>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 20, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickMargin={8}
          />
          <YAxis
            tick={{ fontSize: 11, fill: '#6b7280' }}
            tickMargin={8}
            width={40}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              fontSize: '12px',
            }}
            labelStyle={{ fontWeight: 600, color: '#374151' }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={{ fill: color, r: 4 }}
            activeDot={{ r: 6, strokeWidth: 0 }}
            animationDuration={500}
            name={title || 'Giá trị'}
          />
          {showBrush && (
            <Brush
              dataKey="name"
              height={30}
              stroke={color}
              fill="#f9fafb"
              onChange={handleZoom}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
