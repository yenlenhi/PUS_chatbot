'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';

// Color palette for charts
const COLORS = [
  '#dc2626', // red-600
  '#2563eb', // blue-600
  '#16a34a', // green-600
  '#ca8a04', // yellow-600
  '#9333ea', // purple-600
  '#0891b2', // cyan-600
  '#ea580c', // orange-600
  '#db2777', // pink-600
];

export interface ChartData {
  type: 'bar' | 'line' | 'pie' | 'area';
  title?: string;
  data: Array<Record<string, string | number>>;
  xKey?: string;
  yKeys?: string[];
  labels?: string[];
  description?: string;
}

interface ChartRendererProps {
  chartData: ChartData;
  className?: string;
}

const ChartRenderer: React.FC<ChartRendererProps> = ({ chartData, className = '' }) => {
  const { type, title, data, xKey = 'name', yKeys = ['value'], description } = chartData;

  if (!data || data.length === 0) {
    return null;
  }

  const renderChart = () => {
    switch (type) {
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey} 
                tick={{ fontSize: 12 }} 
                stroke="#6b7280"
              />
              <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              {yKeys.map((key, index) => (
                <Bar 
                  key={key} 
                  dataKey={key} 
                  fill={COLORS[index % COLORS.length]}
                  radius={[4, 4, 0, 0]}
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case 'line':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey} 
                tick={{ fontSize: 12 }} 
                stroke="#6b7280"
              />
              <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              {yKeys.map((key, index) => (
                <Line 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={COLORS[index % COLORS.length]}
                  strokeWidth={2}
                  dot={{ fill: COLORS[index % COLORS.length], strokeWidth: 2 }}
                  activeDot={{ r: 6 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case 'area':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey={xKey} 
                tick={{ fontSize: 12 }} 
                stroke="#6b7280"
              />
              <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              {yKeys.map((key, index) => (
                <Area 
                  key={key} 
                  type="monotone" 
                  dataKey={key} 
                  stroke={COLORS[index % COLORS.length]}
                  fill={COLORS[index % COLORS.length]}
                  fillOpacity={0.3}
                  strokeWidth={2}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>
        );

      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${((percent ?? 0) * 100).toFixed(0)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey={yKeys[0] || 'value'}
                nameKey={xKey}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: '#fff', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }} 
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
            </PieChart>
          </ResponsiveContainer>
        );

      default:
        return <p className="text-gray-500 text-sm">Loại biểu đồ không được hỗ trợ</p>;
    }
  };

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 my-3 ${className}`}>
      {title && (
        <h4 className="text-sm font-semibold text-gray-800 mb-2 text-center">{title}</h4>
      )}
      {renderChart()}
      {description && (
        <p className="text-xs text-gray-500 mt-2 text-center italic">{description}</p>
      )}
    </div>
  );
};

export default ChartRenderer;
