'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { X, ChevronUp, FileText, ExternalLink, Copy, Check, Eye } from 'lucide-react';
import type { SourceReference } from '@/types';

// Mobile Bottom Sheet for Sources
interface MobileSourceDrawerProps {
    isOpen: boolean;
    onClose: () => void;
    sources: SourceReference[];
    onViewDocument: (filename: string, page?: number) => void;
}

export const MobileSourceDrawer: React.FC<MobileSourceDrawerProps> = ({
    isOpen,
    onClose,
    sources,
    onViewDocument,
}) => {
    const [dragY, setDragY] = useState(0);
    const [isDragging, setIsDragging] = useState(false);
    const [copiedId, setCopiedId] = useState<string | null>(null);

    // Reset drag when closed
    useEffect(() => {
        if (!isOpen) setDragY(0);
    }, [isOpen]);

    const handleDragStart = (e: React.TouchEvent | React.MouseEvent) => {
        setIsDragging(true);
    };

    const handleDragMove = (e: React.TouchEvent | React.MouseEvent) => {
        if (!isDragging) return;
        const clientY = 'touches' in e ? e.touches[0].clientY : e.clientY;
        const newDragY = Math.max(0, clientY - 100);
        setDragY(newDragY);
    };

    const handleDragEnd = () => {
        setIsDragging(false);
        // If dragged more than 150px down, close
        if (dragY > 150) {
            onClose();
        }
        setDragY(0);
    };

    const handleCopy = async (text: string, id: string) => {
        await navigator.clipboard.writeText(text);
        setCopiedId(id);
        setTimeout(() => setCopiedId(null), 2000);
    };

    const getConfidenceColor = (score: number) => {
        if (score >= 0.9) return 'bg-green-500';
        if (score >= 0.8) return 'bg-yellow-500';
        return 'bg-orange-500';
    };

    const getConfidenceLabel = (score: number) => {
        if (score >= 0.9) return 'Rất phù hợp';
        if (score >= 0.8) return 'Phù hợp';
        return 'Tham khảo';
    };

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="md:hidden fixed inset-0 bg-black/50 z-40 transition-opacity"
                onClick={onClose}
            />

            {/* Bottom Sheet */}
            <div
                className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-3xl shadow-2xl max-h-[80vh] transition-transform duration-300 ease-out"
                style={{ transform: `translateY(${dragY}px)` }}
            >
                {/* Drag Handle */}
                <div
                    className="flex justify-center py-3 cursor-grab active:cursor-grabbing"
                    onTouchStart={handleDragStart}
                    onTouchMove={handleDragMove}
                    onTouchEnd={handleDragEnd}
                    onMouseDown={handleDragStart}
                    onMouseMove={handleDragMove}
                    onMouseUp={handleDragEnd}
                >
                    <div className="w-12 h-1.5 bg-gray-300 rounded-full" />
                </div>

                {/* Header */}
                <div className="flex items-center justify-between px-4 pb-3 border-b border-gray-100">
                    <div className="flex items-center gap-2">
                        <FileText className="w-5 h-5 text-red-600" />
                        <h3 className="font-semibold text-gray-900">
                            Tài liệu tham khảo
                        </h3>
                        <span className="bg-red-100 text-red-700 text-xs font-medium px-2 py-0.5 rounded-full">
                            {sources.length}
                        </span>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                    >
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Sources List */}
                <div className="overflow-y-auto max-h-[60vh] p-4 space-y-3">
                    {sources.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <FileText className="w-12 h-12 mx-auto mb-2 opacity-30" />
                            <p>Chưa có tài liệu tham khảo</p>
                        </div>
                    ) : (
                        sources.map((source, idx) => (
                            <div
                                key={source.chunk_id || idx}
                                className="bg-gray-50 rounded-xl p-4 border border-gray-100 hover:border-red-200 transition-colors"
                            >
                                {/* Source Header */}
                                <div className="flex items-start justify-between mb-2">
                                    <div className="flex-1 min-w-0">
                                        <h4 className="font-medium text-gray-900 text-sm truncate">
                                            {source.heading || source.filename || 'Tài liệu'}
                                        </h4>
                                        {source.page_number && (
                                            <p className="text-xs text-gray-500 mt-0.5">
                                                Trang {source.page_number}
                                            </p>
                                        )}
                                    </div>
                                    {/* Confidence Badge */}
                                    <div className="flex items-center gap-1 ml-2">
                                        <div className={`w-2 h-2 rounded-full ${getConfidenceColor(source.relevance_score || 0)}`} />
                                        <span className="text-xs font-medium text-gray-600">
                                            {Math.round((source.relevance_score || 0) * 100)}%
                                        </span>
                                    </div>
                                </div>

                                {/* Source Content Preview */}
                                {source.content_snippet && (
                                    <p className="text-xs text-gray-600 line-clamp-3 mb-3">
                                        {source.content_snippet.substring(0, 200)}...
                                    </p>
                                )}

                                {/* Action Buttons */}
                                <div className="flex gap-2">
                                    <button
                                        onClick={() => onViewDocument(source.filename || '', source.page_number || undefined)}
                                        className="flex-1 flex items-center justify-center gap-1.5 py-2 px-3 bg-red-600 hover:bg-red-700 text-white text-xs font-medium rounded-lg transition-colors"
                                    >
                                        <Eye className="w-3.5 h-3.5" />
                                        Xem PDF
                                    </button>
                                    <button
                                        onClick={() => handleCopy(source.content_snippet || '', source.chunk_id || String(idx))}
                                        className="flex items-center justify-center gap-1.5 py-2 px-3 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-medium rounded-lg transition-colors"
                                    >
                                        {copiedId === (source.chunk_id || String(idx)) ? (
                                            <Check className="w-3.5 h-3.5 text-green-600" />
                                        ) : (
                                            <Copy className="w-3.5 h-3.5" />
                                        )}
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Safe area padding for notched phones */}
                <div className="h-6 bg-white" />
            </div>
        </>
    );
};

// Floating Action Button for opening sources on mobile
interface SourceFABProps {
    sourceCount: number;
    onClick: () => void;
}

export const SourceFAB: React.FC<SourceFABProps> = ({ sourceCount, onClick }) => {
    if (sourceCount === 0) return null;

    return (
        <button
            onClick={onClick}
            className="md:hidden fixed bottom-24 right-4 z-30 flex items-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-3 rounded-full shadow-lg shadow-red-500/30 transition-all hover:scale-105 active:scale-95"
        >
            <FileText className="w-5 h-5" />
            <span className="font-medium text-sm">{sourceCount}</span>
            <ChevronUp className="w-4 h-4" />
        </button>
    );
};

// Suggested Questions Chips
interface SuggestedQuestionsProps {
    questions: string[];
    onSelect: (question: string) => void;
    loading?: boolean;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
    questions,
    onSelect,
    loading = false,
}) => {
    if (loading) {
        return (
            <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
                {[1, 2, 3].map((i) => (
                    <div key={i} className="h-9 w-32 bg-gray-100 rounded-full animate-pulse flex-shrink-0" />
                ))}
            </div>
        );
    }

    if (questions.length === 0) return null;

    return (
        <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide snap-x">
            {questions.slice(0, 5).map((question, idx) => (
                <button
                    key={idx}
                    onClick={() => onSelect(question)}
                    className="flex-shrink-0 snap-start px-4 py-2 bg-gradient-to-r from-red-50 to-orange-50 hover:from-red-100 hover:to-orange-100 text-red-700 text-sm font-medium rounded-full border border-red-200 hover:border-red-300 transition-all hover:shadow-md whitespace-nowrap"
                >
                    {question.length > 40 ? question.substring(0, 40) + '...' : question}
                </button>
            ))}
        </div>
    );
};

// Quick Actions Bar for messages
interface QuickActionsProps {
    onCopy: () => void;
    onSpeak: () => void;
    onShare?: () => void;
    isCopied: boolean;
    isSpeaking: boolean;
}

export const QuickActions: React.FC<QuickActionsProps> = ({
    onCopy,
    onSpeak,
    onShare,
    isCopied,
    isSpeaking,
}) => {
    return (
        <div className="flex items-center gap-1 mt-2">
            <button
                onClick={onCopy}
                className={`flex items-center gap-1 px-2.5 py-1.5 text-xs rounded-lg transition-all ${isCopied
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 hover:bg-gray-200 text-gray-600'
                    }`}
            >
                {isCopied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{isCopied ? 'Đã chép' : 'Sao chép'}</span>
            </button>
        </div>
    );
};

export default MobileSourceDrawer;
