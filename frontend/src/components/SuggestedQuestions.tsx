import React from 'react';
import { ArrowRight, MessageCircle } from 'lucide-react';

interface SuggestedQuestionsProps {
  questions: string[];
  onQuestionClick: (question: string) => void;
  isLoading?: boolean;
  language?: 'vi' | 'en';
}

const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onQuestionClick,
  isLoading = false,
  language = 'vi'
}) => {
  if (isLoading) {
    return (
      <div className="mt-4 space-y-2">
        <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
          <MessageCircle className="w-4 h-4" />
          <span>{language === 'vi' ? 'Câu hỏi gợi ý...' : 'Suggested questions...'}</span>
        </div>
        {Array.from({ length: 3 }).map((_, index) => (
          <div
            key={index}
            className="p-3 bg-gray-50 rounded-lg border border-gray-200 animate-pulse"
          >
            <div className="h-4 bg-gray-300 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!questions || questions.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-center gap-2 text-sm text-gray-500 mb-3">
        <MessageCircle className="w-4 h-4" />
        <span>{language === 'vi' ? 'Câu hỏi gợi ý' : 'Suggested questions'}</span>
      </div>
      
      {questions.slice(0, 3).map((question, index) => (
        <button
          key={index}
          onClick={() => onQuestionClick(question)}
          className="group flex items-center justify-between w-full p-3 text-left text-sm bg-white hover:bg-gray-50 rounded-lg border border-gray-200 hover:border-gray-300 transition-all duration-200 shadow-sm hover:shadow-md"
        >
          <span className="flex-1 text-gray-700 pr-3">
            {question}
          </span>
          <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-gray-600 transition-colors duration-200 flex-shrink-0" />
        </button>
      ))}
    </div>
  );
};

export default SuggestedQuestions;