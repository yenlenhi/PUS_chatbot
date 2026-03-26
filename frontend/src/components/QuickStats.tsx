'use client';

import React from 'react';
import { Award, Calendar, GraduationCap, Users } from 'lucide-react';
import TrafficStatsCard from './TrafficStatsCard';

const QUICK_STATS = [
  {
    value: '1963',
    label: 'Năm thành lập',
    sublabel: 'Hơn 60 năm lịch sử',
    icon: Calendar,
    color: 'from-red-700 to-red-500',
  },
  {
    value: '6',
    label: 'Ngành đào tạo',
    sublabel: 'Chuyên môn an ninh',
    icon: GraduationCap,
    color: 'from-amber-500 to-orange-500',
  },
  {
    value: 'GS, PGS, TS',
    label: 'Đội ngũ giảng viên',
    sublabel: 'Trình độ chuyên sâu',
    icon: Award,
    color: 'from-emerald-600 to-green-500',
  },
  {
    value: 'Hàng ngàn',
    label: 'Học viên, sinh viên',
    sublabel: 'Đào tạo nhiều hệ',
    icon: Users,
    color: 'from-sky-600 to-indigo-600',
  },
];

const QuickStats = () => {
  return (
    <section className="relative border-t border-gray-100 bg-[radial-gradient(circle_at_top_left,_rgba(254,242,242,0.85),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(219,234,254,0.75),_transparent_32%),linear-gradient(180deg,_#ffffff_0%,_#f8fafc_100%)] py-16">
      <div className="container mx-auto px-4">
        <div className="grid gap-8 xl:grid-cols-[minmax(0,1.5fr)_380px]">
          <div>
            <div className="mb-8 flex max-w-2xl flex-col gap-3">
              <span className="inline-flex w-fit items-center rounded-full border border-red-100 bg-white/80 px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-red-700 shadow-sm">
                Tổng quan nhanh
              </span>
              <h2 className="text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
                Những con số định hình hệ thống tư vấn của trường
              </h2>
              <p className="text-base leading-7 text-slate-600">
                Khu vực này được đặt ngay dưới banner để người dùng thấy cùng lúc quy mô đào tạo và mức độ hoạt động thực tế của hệ thống.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
              {QUICK_STATS.map((stat) => (
                <div
                  key={stat.label}
                  className="group relative overflow-hidden rounded-[28px] border border-white/80 bg-white/90 p-6 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_60px_rgba(15,23,42,0.12)]"
                >
                  <div className={`absolute inset-x-0 top-0 h-1 bg-gradient-to-r ${stat.color}`} />
                  <div className={`absolute -right-8 -top-8 h-24 w-24 rounded-full bg-gradient-to-br ${stat.color} opacity-10 blur-2xl transition-transform duration-300 group-hover:scale-110`} />

                  <div className={`mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br ${stat.color} shadow-lg shadow-slate-200`}>
                    <stat.icon className="h-7 w-7 text-white" />
                  </div>

                  <div className="text-2xl font-black tracking-tight text-slate-900 md:text-3xl">
                    {stat.value}
                  </div>
                  <div className="mt-2 text-base font-semibold text-slate-800">
                    {stat.label}
                  </div>
                  <div className="mt-1 text-sm text-slate-500">
                    {stat.sublabel}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="xl:pt-12">
            <TrafficStatsCard />
          </div>
        </div>
      </div>
    </section>
  );
};

export default QuickStats;
