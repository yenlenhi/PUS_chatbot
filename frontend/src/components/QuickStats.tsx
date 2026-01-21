'use client';

import React from 'react';
import { Calendar, GraduationCap, Users, Award } from 'lucide-react';

const QUICK_STATS = [
    {
        value: '1963',
        label: 'Năm thành lập',
        sublabel: 'Hơn 60 năm lịch sử',
        icon: Calendar,
        color: 'from-red-600 to-red-700'
    },
    {
        value: '6',
        label: 'Ngành đào tạo',
        sublabel: 'Chuyên môn an ninh',
        icon: GraduationCap,
        color: 'from-yellow-500 to-orange-500'
    },
    {
        value: 'GS, PGS, TS',
        label: 'Đội ngũ giảng viên',
        sublabel: 'Trình độ cao',
        icon: Award,
        color: 'from-green-600 to-emerald-600'
    },
    {
        value: 'Hàng ngàn',
        label: 'Sinh viên',
        sublabel: 'Các hệ đào tạo',
        icon: Users,
        color: 'from-blue-600 to-indigo-600'
    }
];

const QuickStats = () => {
    return (
        <section className="py-16 bg-white border-t border-gray-100">
            <div className="container mx-auto px-4">
                {/* Stats Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                    {QUICK_STATS.map((stat, index) => (
                        <div
                            key={index}
                            className="group relative bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-1 overflow-hidden"
                        >
                            {/* Background Gradient on Hover */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${stat.color} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>

                            {/* Icon */}
                            <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                                <stat.icon className="w-6 h-6 text-white" />
                            </div>

                            {/* Value */}
                            <div className="text-2xl lg:text-3xl font-black text-gray-900 mb-1">
                                {stat.value}
                            </div>

                            {/* Label */}
                            <div className="text-sm font-bold text-gray-700 mb-1">
                                {stat.label}
                            </div>

                            {/* Sublabel */}
                            <div className="text-xs text-gray-500">
                                {stat.sublabel}
                            </div>

                            {/* Decorative corner */}
                            <div className={`absolute bottom-0 right-0 w-16 h-16 bg-gradient-to-br ${stat.color} opacity-5 rounded-tl-full`}></div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

export default QuickStats;
