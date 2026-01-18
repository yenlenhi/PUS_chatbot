'use client';

import React from 'react';
import { Bot } from 'lucide-react';

/**
 * Typing Indicator Component - Shows animated dots when bot is preparing response
 */
export const TypingIndicator = () => {
    return (
        <div className="flex justify-start animate-fadeIn">
            <div className="bg-gray-100 text-gray-800 p-4 rounded-lg max-w-[85%] shadow-sm">
                <div className="flex items-center space-x-3">
                    <Bot className="w-5 h-5 text-red-600" />
                    <div className="flex items-center space-x-2">
                        <span className="text-sm text-gray-500">Đang suy nghĩ</span>
                        <div className="flex space-x-1">
                            <div className="w-2 h-2 bg-red-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                            <div className="w-2 h-2 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                            <div className="w-2 h-2 bg-red-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

/**
 * Message Skeleton Component - Shows placeholder while loading content
 */
export const MessageSkeleton = ({ status }: { status?: string }) => {
    return (
        <div className="flex justify-start animate-fadeIn">
            <div className="bg-gray-100 text-gray-800 p-4 rounded-lg max-w-[85%] shadow-sm w-full">
                <div className="flex items-start space-x-3">
                    <Bot className="w-5 h-5 text-red-600 flex-shrink-0" />
                    <div className="flex-1 space-y-3">
                        {/* Status indicator */}
                        {status && (
                            <div className="flex items-center space-x-2 text-sm text-red-600 font-medium mb-2">
                                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
                                <span>{status}</span>
                            </div>
                        )}

                        {/* Skeleton lines */}
                        <div className="space-y-2.5 animate-pulse">
                            <div className="h-3 bg-gray-200 rounded-full w-3/4"></div>
                            <div className="h-3 bg-gray-200 rounded-full w-full"></div>
                            <div className="h-3 bg-gray-200 rounded-full w-5/6"></div>
                            <div className="h-3 bg-gray-200 rounded-full w-2/3"></div>
                        </div>

                        {/* Source skeleton */}
                        <div className="mt-3 pt-3 border-t border-gray-200 space-y-2 animate-pulse">
                            <div className="h-2.5 bg-gray-200 rounded-full w-1/4"></div>
                            <div className="flex space-x-2">
                                <div className="h-6 bg-gray-200 rounded w-24"></div>
                                <div className="h-6 bg-gray-200 rounded w-28"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

/**
 * Processing Steps Component - Shows current processing stage
 */
export const ProcessingSteps = ({ currentStep }: { currentStep: string }) => {
    const steps = [
        { key: 'search', label: 'Tìm kiếm tài liệu', icon: '🔍' },
        { key: 'analyze', label: 'Phân tích ngữ cảnh', icon: '🧠' },
        { key: 'generate', label: 'Tạo câu trả lời', icon: '✍️' },
    ];

    // Map status messages to step keys
    const getActiveStep = () => {
        if (currentStep.includes('tìm kiếm') || currentStep.includes('Đang tìm')) return 'search';
        if (currentStep.includes('phân tích') || currentStep.includes('context')) return 'analyze';
        if (currentStep.includes('tạo') || currentStep.includes('soạn') || currentStep.includes('trả lời')) return 'generate';
        return 'search';
    };

    const activeStep = getActiveStep();

    return (
        <div className="flex justify-start animate-fadeIn">
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg max-w-[85%] shadow-sm border border-gray-200">
                <div className="flex items-start space-x-3">
                    <Bot className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                        <p className="text-sm font-medium text-gray-700 mb-3">Đang xử lý câu hỏi của bạn...</p>
                        <div className="space-y-2">
                            {steps.map((step, index) => {
                                const isActive = step.key === activeStep;
                                const isPast = steps.findIndex(s => s.key === activeStep) > index;

                                return (
                                    <div
                                        key={step.key}
                                        className={`flex items-center space-x-2 text-sm transition-all duration-300 ${isActive ? 'text-red-600 font-medium' :
                                                isPast ? 'text-green-600' : 'text-gray-400'
                                            }`}
                                    >
                                        <span className="w-5 text-center">
                                            {isPast ? '✅' : isActive ? (
                                                <span className="inline-block animate-spin">⏳</span>
                                            ) : step.icon}
                                        </span>
                                        <span>{step.label}</span>
                                        {isActive && (
                                            <div className="flex space-x-0.5 ml-1">
                                                <div className="w-1 h-1 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                                <div className="w-1 h-1 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                                <div className="w-1 h-1 bg-red-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                            </div>
                                        )}
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default { TypingIndicator, MessageSkeleton, ProcessingSteps };
