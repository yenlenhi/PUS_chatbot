'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';

interface InteractiveBarChartProps {
  data: Array<{ label: string; value: number }>;
  color?: string;
  title?: string;
  height?: number;
  horizontal?: boolean;
  gradientColors?: string[];
}

export default function InteractiveBarChart({
  data,
  color = '#ef4444',
  title,
  height = 300,
  horizontal = false,
  gradientColors,
}: InteractiveBarChartProps) {
  // Transform data for recharts
  const chartData = data.map((item) => ({
    name: item.label,
    value: item.value,
  }));

  // Generate gradient colors if not provided
  const colors = gradientColors || [
    '#ef4444',
    '#f97316',
    '#f59e0b',
    '#eab308',
    '#84cc16',
    '#22c55e',
    '#10b981',
  ];

  return (
    <div className="w-full">
      {title && (
        <h3 className="text-sm font-semibold text-gray-700 mb-3">{title}</h3>
      )}
      <ResponsiveContainer width="100%" height={height}>
        <BarChart
          data={chartData}
          layout={horizontal ? 'vertical' : 'horizontal'}
          margin={{ top: 5, right: 20, left: horizontal ? 60 : 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          {horizontal ? (
            <>
              <XAxis type="number" tick={{ fontSize: 11, fill: '#6b7280' }} />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11, fill: '#6b7280' }}
                width={80}
              />
            </>
          ) : (
            <>
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
            </>
          )}
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              fontSize: '12px',
            }}
            labelStyle={{ fontWeight: 600, color: '#374151' }}
            cursor={{ fill: 'rgba(0, 0, 0, 0.05)' }}
          />
          <Legend
            wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }}
          />
          <Bar
            dataKey="value"
            fill={color}
            radius={[4, 4, 0, 0]}
            animationDuration={500}
            name={title || 'Giá trị'}
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={colors[index % colors.length]}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
