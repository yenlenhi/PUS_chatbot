'use client';

import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, MessageSquare, ThumbsDown, ThumbsUp } from 'lucide-react';
import { submitFeedback } from '@/services/feedback';
import type { FeedbackRating } from '@/types/feedback';

interface ForcedFeedbackModalProps {
  isOpen: boolean;
  conversationId: string;
  messageId: string;
  query: string;
  answer: string;
  chunkIds?: number[];
  onSubmitted: () => void;
}

const ratingOptions: Array<{
  value: FeedbackRating;
  label: string;
  description: string;
  icon: React.ReactNode;
  activeClass: string;
}> = [
  {
    value: 'positive',
    label: 'Hài lòng',
    description: 'Câu trả lời hữu ích và đúng nhu cầu.',
    icon: <ThumbsUp className="h-4 w-4" />,
    activeClass: 'border-green-500 bg-green-50 text-green-700',
  },
  {
    value: 'neutral',
    label: 'Tạm ổn',
    description: 'Có ích một phần nhưng vẫn cần cải thiện.',
    icon: <CheckCircle2 className="h-4 w-4" />,
    activeClass: 'border-amber-500 bg-amber-50 text-amber-700',
  },
  {
    value: 'negative',
    label: 'Chưa tốt',
    description: 'Thông tin chưa đúng hoặc chưa giải quyết được câu hỏi.',
    icon: <ThumbsDown className="h-4 w-4" />,
    activeClass: 'border-red-500 bg-red-50 text-red-700',
  },
];

const ForcedFeedbackModal: React.FC<ForcedFeedbackModalProps> = ({
  isOpen,
  conversationId,
  messageId,
  query,
  answer,
  chunkIds = [],
  onSubmitted,
}) => {
  const [rating, setRating] = useState<FeedbackRating | null>(null);
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) {
      setRating(null);
      setComment('');
      setError(null);
      setIsSubmitting(false);
      return;
    }

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      document.body.style.overflow = previousOverflow;
    };
  }, [isOpen]);

  const handleSubmit = async () => {
    if (!rating || !comment.trim() || isSubmitting) {
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      await submitFeedback({
        conversation_id: conversationId,
        message_id: messageId,
        query,
        answer,
        rating,
        comment: comment.trim(),
        chunk_ids: chunkIds,
        session_id: conversationId,
      });

      onSubmitted();
    } catch (submitError) {
      console.error('Forced feedback submission failed:', submitError);
      setError('Không thể gửi đánh giá lúc này. Vui lòng thử lại.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!isOpen) {
    return null;
  }

  const canSubmit = Boolean(rating && comment.trim()) && !isSubmitting;

  return (
    <div className="fixed inset-0 z-[120] flex items-end justify-center bg-slate-950/70 p-3 backdrop-blur-sm sm:items-center sm:p-6">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="forced-feedback-title"
        className="flex max-h-[calc(100vh-1.5rem)] w-full max-w-lg flex-col overflow-hidden rounded-t-3xl bg-white shadow-2xl sm:max-h-[90vh] sm:rounded-3xl"
      >
        <div className="border-b border-slate-200 bg-gradient-to-r from-red-600 to-red-700 px-4 py-4 text-white sm:px-6">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-2xl bg-white/15 p-2">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div className="min-w-0">
              <h2 id="forced-feedback-title" className="text-base font-semibold sm:text-lg">
                Đánh giá trải nghiệm chat
              </h2>
              <p className="mt-1 text-sm text-red-50">
                Sau 3 tin nhắn đầu, bạn cần gửi đánh giá một lần để giúp nhà trường cải thiện chatbot.
              </p>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-4 py-4 sm:px-6 sm:py-5">
          <div>
            <p className="text-sm font-semibold text-slate-900">
              Mức đánh giá
            </p>
            <div className="mt-3 grid grid-cols-1 gap-3">
              {ratingOptions.map((option) => {
                const isActive = rating === option.value;

                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setRating(option.value)}
                    className={`min-h-[52px] rounded-2xl border px-4 py-3 text-left transition-all ${
                      isActive
                        ? option.activeClass
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="mt-0.5">{option.icon}</span>
                      <span className="min-w-0">
                        <span className="block text-sm font-semibold">{option.label}</span>
                        <span className="mt-1 block text-sm leading-5 opacity-90">{option.description}</span>
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-4">
            <label htmlFor="forced-feedback-comment" className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <MessageSquare className="h-4 w-4 text-red-600" />
              Nội dung đánh giá
            </label>
            <textarea
              id="forced-feedback-comment"
              value={comment}
              onChange={(event) => setComment(event.target.value)}
              placeholder="Hãy cho biết chatbot trả lời đúng hay sai ở điểm nào, còn thiếu thông tin gì, hoặc cần cải thiện điều gì."
              className="mt-3 min-h-[132px] w-full rounded-2xl border border-slate-300 px-4 py-3 text-sm leading-6 text-slate-800 outline-none transition focus:border-red-500 focus:ring-2 focus:ring-red-200"
              disabled={isSubmitting}
            />
          </div>

          {error && (
            <div className="mt-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}
        </div>

        <div className="shrink-0 border-t border-slate-200 bg-slate-50 px-4 py-4 pb-[calc(1rem+env(safe-area-inset-bottom))] sm:px-6">
          <button
            type="button"
            onClick={handleSubmit}
            disabled={!canSubmit}
            className="flex min-h-[48px] w-full items-center justify-center gap-2 rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Đang gửi đánh giá...
              </>
            ) : (
              'Gửi đánh giá và tiếp tục'
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ForcedFeedbackModal;
