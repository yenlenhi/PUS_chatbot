'use client';

import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, MessageSquare, X, Check } from 'lucide-react';
import { submitFeedback } from '@/services/feedback';
import type { FeedbackRating } from '@/types/feedback';

interface FeedbackButtonsProps {
  conversationId: string;
  messageId: string;
  query: string;
  answer: string;
  chunkIds?: number[];
  className?: string;
}

const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  conversationId,
  messageId,
  query,
  answer,
  chunkIds = [],
  className = '',
}) => {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [showComment, setShowComment] = useState(false);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRating = async (selectedRating: FeedbackRating) => {
    if (submitted || isSubmitting) return;

    setRating(selectedRating);
    setError(null);

    // If negative, show comment box first
    if (selectedRating === 'negative') {
      setShowComment(true);
      return;
    }

    // For positive/neutral, submit immediately
    await submitFeedbackData(selectedRating, '');
  };

  const submitFeedbackData = async (feedbackRating: FeedbackRating, feedbackComment: string) => {
    setIsSubmitting(true);
    setError(null);

    try {
      await submitFeedback({
        conversation_id: conversationId,
        message_id: messageId,
        query,
        answer,
        rating: feedbackRating,
        comment: feedbackComment || undefined,
        chunk_ids: chunkIds,
      });

      setSubmitted(true);
      setShowComment(false);
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError('Không thể gửi phản hồi. Vui lòng thử lại.');
      setRating(null);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitWithComment = async () => {
    if (!rating || isSubmitting) return;
    await submitFeedbackData(rating, comment);
  };

  const handleCancelComment = () => {
    setShowComment(false);
    setComment('');
    setRating(null);
  };

  if (submitted) {
    return (
      <div className={`flex items-center gap-2 text-sm text-green-600 ${className}`}>
        <Check className="w-4 h-4" />
        <span>Cảm ơn phản hồi của bạn!</span>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-500">Câu trả lời này có hữu ích không?</span>
        
        <button
          onClick={() => handleRating('positive')}
          disabled={isSubmitting}
          className={`p-1.5 rounded-md transition-colors ${
            rating === 'positive'
              ? 'bg-green-100 text-green-600'
              : 'hover:bg-gray-100 text-gray-400 hover:text-green-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          title="Hữu ích"
        >
          <ThumbsUp className="w-4 h-4" />
        </button>

        <button
          onClick={() => handleRating('negative')}
          disabled={isSubmitting}
          className={`p-1.5 rounded-md transition-colors ${
            rating === 'negative'
              ? 'bg-red-100 text-red-600'
              : 'hover:bg-gray-100 text-gray-400 hover:text-red-600'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
          title="Không hữu ích"
        >
          <ThumbsDown className="w-4 h-4" />
        </button>

        {!showComment && (
          <button
            onClick={() => setShowComment(true)}
            disabled={isSubmitting}
            className="p-1.5 rounded-md hover:bg-gray-100 text-gray-400 hover:text-blue-600 transition-colors disabled:opacity-50"
            title="Để lại nhận xét"
          >
            <MessageSquare className="w-4 h-4" />
          </button>
        )}
      </div>

      {error && (
        <p className="text-xs text-red-500 mt-1">{error}</p>
      )}

      {showComment && (
        <div className="mt-2 space-y-2">
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Cho chúng tôi biết lý do bạn không hài lòng..."
            className="w-full p-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
            rows={2}
            disabled={isSubmitting}
          />
          <div className="flex gap-2">
            <button
              onClick={handleSubmitWithComment}
              disabled={isSubmitting || !rating}
              className="px-3 py-1 text-xs bg-red-600 text-white rounded-md hover:bg-red-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center gap-1"
              title={!rating ? 'Vui lòng chọn đánh giá trước' : isSubmitting ? 'Đang gửi...' : 'Gửi phản hồi'}
            >
              {isSubmitting ? (
                <>
                  <span className="inline-block animate-spin rounded-full h-3 w-3 border-b-2 border-white"></span>
                  Đang gửi...
                </>
              ) : (
                'Gửi phản hồi'
              )}
            </button>
            <button
              onClick={handleCancelComment}
              disabled={isSubmitting}
              className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 transition-colors flex items-center gap-1"
            >
              <X className="w-3 h-3" />
              Hủy
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackButtons;
