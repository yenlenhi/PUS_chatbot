'use client';

import React from 'react';
import { Target, Eye } from 'lucide-react';
import { SCHOOL_INFO } from '@/data/constants';

const MissionVision = () => {
    return (
        <section className="py-20 bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 overflow-hidden relative border-t border-red-100">
            {/* Ambient Background Elements */}
            <div className="absolute top-0 left-0 w-full h-full overflow-hidden opacity-20 pointer-events-none">
                <div className="absolute -top-24 -left-24 w-96 h-96 bg-red-200 rounded-full blur-3xl"></div>
                <div className="absolute top-1/2 right-0 w-96 h-96 bg-yellow-200 rounded-full blur-3xl"></div>
            </div>

            <div className="container mx-auto px-4 relative z-10">
                {/* Section Header */}
                <div className="text-center mb-16">
                    <div className="inline-block px-6 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-red-200 shadow-sm mb-4">
                        <span className="text-red-800 text-sm font-bold tracking-widest uppercase">Sứ Mệnh & Tầm Nhìn</span>
                    </div>
                    <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
                        Định Hướng <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-yellow-600">Phát Triển</span>
                    </h2>
                    <div className="w-24 h-1 bg-gradient-to-r from-red-600 to-yellow-500 mx-auto rounded-full"></div>
                </div>

                {/* Two Column Layout */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12">

                    {/* Mission Column */}
                    <div className="group">
                        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-300 border border-red-100 h-full flex flex-col">
                            {/* Icon Header */}
                            <div className="flex items-center gap-4 mb-6">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-red-600 rounded-2xl rotate-6 opacity-20 group-hover:rotate-12 transition-transform duration-300"></div>
                                    <div className="w-16 h-16 bg-gradient-to-br from-red-600 to-red-700 rounded-2xl flex items-center justify-center relative z-10 shadow-lg">
                                        <Target className="w-8 h-8 text-white" />
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs font-bold text-red-600 uppercase tracking-wider mb-1">Mission</div>
                                    <h3 className="text-2xl font-black text-gray-900">Sứ Mệnh</h3>
                                </div>
                            </div>

                            {/* Divider */}
                            <div className="w-full h-px bg-gradient-to-r from-red-200 via-red-300 to-transparent mb-6"></div>

                            {/* Content */}
                            <div className="flex-1">
                                <p className="text-gray-700 leading-relaxed text-lg font-medium">
                                    {SCHOOL_INFO.mission}
                                </p>
                            </div>

                            {/* Bottom Accent */}
                            <div className="mt-6 pt-6 border-t border-red-100">
                                <div className="flex items-center gap-2 text-red-600 text-sm font-bold">
                                    <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></div>
                                    <span>Kiến Tạo Tương Lai</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Vision Column */}
                    <div className="group">
                        <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-300 border border-yellow-100 h-full flex flex-col">
                            {/* Icon Header */}
                            <div className="flex items-center gap-4 mb-6">
                                <div className="relative">
                                    <div className="absolute inset-0 bg-yellow-500 rounded-2xl -rotate-6 opacity-20 group-hover:-rotate-12 transition-transform duration-300"></div>
                                    <div className="w-16 h-16 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-2xl flex items-center justify-center relative z-10 shadow-lg">
                                        <Eye className="w-8 h-8 text-white" />
                                    </div>
                                </div>
                                <div>
                                    <div className="text-xs font-bold text-yellow-600 uppercase tracking-wider mb-1">Vision 2030</div>
                                    <h3 className="text-2xl font-black text-gray-900">Tầm Nhìn</h3>
                                </div>
                            </div>

                            {/* Divider */}
                            <div className="w-full h-px bg-gradient-to-r from-yellow-200 via-yellow-300 to-transparent mb-6"></div>

                            {/* Content */}
                            <div className="flex-1">
                                <p className="text-gray-700 leading-relaxed text-lg font-medium">
                                    {SCHOOL_INFO.vision}
                                </p>
                            </div>

                            {/* Bottom Accent */}
                            <div className="mt-6 pt-6 border-t border-yellow-100">
                                <div className="flex items-center gap-2 text-yellow-600 text-sm font-bold">
                                    <div className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></div>
                                    <span>Vươn Tầm Quốc Tế</span>
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </section>
    );
};

export default MissionVision;
