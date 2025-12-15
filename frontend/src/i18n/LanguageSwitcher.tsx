'use client';

import React from 'react';
import { useLanguage } from './LanguageContext';

const LanguageSwitcher: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <div className="flex items-center bg-gray-100 rounded-lg p-1">
      <button
        onClick={() => setLanguage('vi')}
        className={`px-2.5 py-1.5 text-xs font-semibold rounded-md transition-all duration-200 ${
          language === 'vi'
            ? 'bg-red-600 text-white shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        }`}
        title="Tiếng Việt"
      >
        VI
      </button>
      <button
        onClick={() => setLanguage('en')}
        className={`px-2.5 py-1.5 text-xs font-semibold rounded-md transition-all duration-200 ${
          language === 'en'
            ? 'bg-blue-600 text-white shadow-sm'
            : 'text-gray-600 hover:text-gray-900'
        }`}
        title="English"
      >
        EN
      </button>
    </div>
  );
};

export default LanguageSwitcher;
