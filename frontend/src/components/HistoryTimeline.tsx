'use client';

import React from 'react';
import { HISTORY_MILESTONES } from '@/data/constants';
import { Calendar } from 'lucide-react';

const HistoryTimeline = () => {
    return (
        <section className="py-20 bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 relative overflow-hidden border-t border-red-100">
            {/* Decorative Background */}
            <div className="absolute top-0 left-0 w-full h-full opacity-20 pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-red-200 rounded-full blur-3xl"></div>
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-yellow-200 rounded-full blur-3xl"></div>
            </div>

            <div className="container mx-auto px-4 relative z-10">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <div className="inline-block px-6 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-red-200 shadow-sm mb-4">
                        <span className="text-red-800 text-sm font-bold tracking-widest uppercase">Lịch sử hình thành</span>
                    </div>
                    <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
                        Những Mốc Son <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-yellow-600">Hào Hùng</span>
                    </h2>
                    <div className="w-24 h-1 bg-gradient-to-r from-red-600 to-yellow-500 mx-auto rounded-full"></div>
                </div>

                {/* Horizontal Timeline */}
                <div className="relative">
                    {/* Connecting Line */}
                    <div className="absolute top-12 left-0 right-0 h-1 bg-gradient-to-r from-red-200 via-orange-300 to-yellow-200 rounded-full hidden md:block"></div>

                    {/* Timeline Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 lg:gap-4">
                        {HISTORY_MILESTONES.map((milestone, index) => (
                            <div key={index} className="group relative">
                                {/* Connector Dot */}
                                <div className="hidden md:flex absolute top-10 left-1/2 -translate-x-1/2 w-6 h-6 bg-white rounded-full border-4 border-red-600 group-hover:border-yellow-500 transition-all duration-300 z-20 shadow-lg">
                                    <div className="absolute inset-0 rounded-full bg-red-600 group-hover:bg-yellow-500 animate-pulse opacity-20"></div>
                                </div>

                                {/* Card */}
                                <div className="mt-20 md:mt-24 bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 border border-red-100 group-hover:border-yellow-200 group-hover:-translate-y-2 h-full">
                                    {/* Year Badge */}
                                    <div className="flex items-center justify-center mb-4">
                                        <div className="relative">
                                            <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-yellow-500 rounded-xl rotate-3 opacity-20 group-hover:rotate-6 transition-transform duration-300"></div>
                                            <div className="relative bg-gradient-to-br from-red-600 to-yellow-500 text-white px-4 py-2 rounded-xl shadow-lg">
                                                <div className="flex items-center gap-2">
                                                    <Calendar className="w-4 h-4" />
                                                    <span className="text-xl font-black">{milestone.year}</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    {/* Event Description */}
                                    <div className="text-center">
                                        <p className="text-gray-700 font-medium leading-relaxed text-sm">
                                            {milestone.event}
                                        </p>
                                    </div>

                                    {/* Bottom Accent */}
                                    <div className="mt-4 pt-4 border-t border-red-100">
                                        <div className="flex items-center justify-center gap-1">
                                            <div className="w-1 h-1 rounded-full bg-red-600"></div>
                                            <div className="w-2 h-2 rounded-full bg-yellow-500 group-hover:animate-pulse"></div>
                                            <div className="w-1 h-1 rounded-full bg-orange-600"></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Bottom Note */}
                <div className="mt-12 text-center">
                    <p className="text-gray-600 text-sm italic">
                        Hơn <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-yellow-600">60 năm</span> xây dựng và phát triển
                    </p>
                </div>
            </div>
        </section>
    );
};

export default HistoryTimeline;
