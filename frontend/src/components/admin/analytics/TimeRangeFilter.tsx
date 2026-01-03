'use client';

import React, { useState } from 'react';
import { Calendar, ChevronDown } from 'lucide-react';
import { TimeRange, AnalyticsFilter } from '@/types/analytics';
import { getTimeRangeLabel } from '@/services/analytics';
import { useLanguage } from '@/i18n/LanguageContext';

interface TimeRangeFilterProps {
  value: TimeRange;
  onChange: (filter: AnalyticsFilter) => void;
  className?: string;
}

const TimeRangeFilter: React.FC<TimeRangeFilterProps> = ({
  value,
  onChange,
  className = '',
}) => {
  const { t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [showCustom, setShowCustom] = useState(false);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const options: { value: TimeRange; label: string }[] = [
    { value: 'L7D', label: t('last7Days') },
    { value: 'MTD', label: t('lastMonth') },
    { value: 'YTD', label: t('yearToDate') },
    { value: 'custom', label: t('custom') },
  ];

  const handleSelect = (timeRange: TimeRange) => {
    if (timeRange === 'custom') {
      setShowCustom(true);
    } else {
      onChange({ timeRange });
      setIsOpen(false);
      setShowCustom(false);
    }
  };

  const handleCustomApply = () => {
    if (startDate && endDate) {
      onChange({
        timeRange: 'custom',
        startDate,
        endDate,
      });
      setIsOpen(false);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-1.5 sm:py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:bg-gray-50 transition-colors focus:outline-none focus:ring-2 focus:ring-red-500"
      >
        <Calendar className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-500" />
        <span className="text-xs sm:text-sm font-medium text-gray-700 truncate max-w-[100px] sm:max-w-none">
          {getTimeRangeLabel(value)}
        </span>
        <ChevronDown className={`w-3.5 h-3.5 sm:w-4 sm:h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-10"
            onClick={() => {
              setIsOpen(false);
              setShowCustom(false);
            }}
          />

          {/* Dropdown */}
          <div className="absolute right-0 mt-2 w-56 sm:w-64 bg-white rounded-lg shadow-lg border border-gray-200 z-20">
            {!showCustom ? (
              <div className="py-1">
                {options.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleSelect(option.value)}
                    className={`w-full px-4 py-2 text-left text-sm hover:bg-red-50 transition-colors ${
                      value === option.value
                        ? 'bg-red-50 text-red-600 font-medium'
                        : 'text-gray-700'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-4 space-y-4">
                <h4 className="font-medium text-gray-900">Chọn khoảng thời gian</h4>
                <div className="space-y-3">
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Từ ngày</label>
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-600 mb-1">Đến ngày</label>
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-red-500"
                    />
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => setShowCustom(false)}
                    className="flex-1 px-3 py-2 text-sm text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                  >
                    Hủy
                  </button>
                  <button
                    onClick={handleCustomApply}
                    disabled={!startDate || !endDate}
                    className="flex-1 px-3 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
                  >
                    Áp dụng
                  </button>
                </div>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

export default TimeRangeFilter;
