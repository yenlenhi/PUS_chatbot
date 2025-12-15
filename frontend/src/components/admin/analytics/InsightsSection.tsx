'use client';

import React from 'react';
import { LucideIcon } from 'lucide-react';

interface InsightsSectionProps {
  title: string;
  icon: LucideIcon;
  iconColor?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

const InsightsSection: React.FC<InsightsSectionProps> = ({
  title,
  icon: Icon,
  iconColor = 'text-red-600',
  children,
  action,
  className = '',
}) => {
  return (
    <div className={`bg-white rounded-xl shadow-md border border-gray-200 overflow-hidden ${className}`}>
      <div className="flex items-center justify-between px-5 py-3.5 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
        <div className="flex items-center space-x-2.5">
          <div className={`p-1.5 rounded-lg bg-red-50`}>
            <Icon className={`w-4 h-4 ${iconColor}`} />
          </div>
          <h3 className="text-base font-semibold text-gray-900">{title}</h3>
        </div>
        {action && <div>{action}</div>}
      </div>
      <div className="p-4">{children}</div>
    </div>
  );
};

export default InsightsSection;
