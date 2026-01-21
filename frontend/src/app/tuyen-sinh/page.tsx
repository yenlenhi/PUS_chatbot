'use client';

import React from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  Calendar, GraduationCap, FileCheck, Users, Clock,
  CheckCircle2, Award, Heart, Eye, Ruler, FileText,
  Phone, Mail, MessageCircle, ArrowRight, Sparkles,
  ClipboardCheck, Stethoscope, Brain, UserCheck,
  ChevronRight
} from 'lucide-react';
import { ADMISSION_PROGRAMS, IMPORTANT_DATES, SCHOOL_INFO } from '@/data/constants';

// Phương thức xét tuyển từ WEBSITE_CONTENT.md
const ADMISSION_METHODS = [
  {
    id: 1,
    title: 'Xét tuyển thẳng',
    description: 'Xét tuyển thẳng theo quy chế của Bộ Giáo dục và Đào tạo',
    icon: Award,
    color: 'from-amber-500 to-orange-500',
    shadowColor: 'shadow-amber-500/30',
    details: ['Thí sinh xuất sắc', 'Đạt giải quốc gia', 'Theo quy chế Bộ GD&ĐT']
  },
  {
    id: 2,
    title: 'Kết hợp chứng chỉ ngoại ngữ',
    description: 'Xét tuyển kết hợp chứng chỉ ngoại ngữ quốc tế (IELTS, TOEFL, ...)',
    icon: FileCheck,
    color: 'from-blue-500 to-indigo-500',
    shadowColor: 'shadow-blue-500/30',
    details: ['IELTS từ 5.5+', 'TOEFL iBT từ 65+', 'Hoặc tương đương']
  },
  {
    id: 3,
    title: 'Thi đánh giá năng lực',
    description: 'Xét tuyển dựa trên kết quả thi tốt nghiệp THPT kết hợp bài thi đánh giá năng lực của Bộ Công an',
    icon: Brain,
    color: 'from-emerald-500 to-teal-500',
    shadowColor: 'shadow-emerald-500/30',
    details: ['Điểm thi THPT', 'Bài thi năng lực BCA', 'Điểm tổng hợp']
  }
];

// Quy trình xét tuyển
const ADMISSION_PROCESS = [
  {
    step: 1,
    title: 'Đăng ký xét tuyển',
    description: 'Nộp hồ sơ trực tuyến hoặc trực tiếp tại trường',
    icon: ClipboardCheck
  },
  {
    step: 2,
    title: 'Kiểm tra sức khỏe',
    description: 'Khám sức khỏe tại bệnh viện theo quy định',
    icon: Stethoscope
  },
  {
    step: 3,
    title: 'Thi đánh giá năng lực',
    description: 'Thi kiến thức cơ bản và năng lực chuyên môn',
    icon: Brain
  },
  {
    step: 4,
    title: 'Xét duyệt hồ sơ',
    description: 'Kiểm tra lý lịch và phẩm chất chính trị',
    icon: UserCheck
  }
];

// Điều kiện xét tuyển
const REQUIREMENTS = {
  general: [
    { icon: Users, text: 'Công dân Việt Nam, có đủ sức khỏe theo quy định' },
    { icon: Heart, text: 'Có phẩm chất chính trị, đạo đức tốt' },
    { icon: GraduationCap, text: 'Tốt nghiệp THPT hoặc tương đương' },
    { icon: Calendar, text: 'Tuổi từ 17 đến 21 (tính đến 31/12/2025)' }
  ],
  specific: [
    { icon: Ruler, text: 'Chiều cao nam ≥ 1.65m, nữ ≥ 1.55m' },
    { icon: Eye, text: 'Thị lực hai mắt ≥ 8/10' },
    { icon: Heart, text: 'Không có tiền sử bệnh tâm thần, truyền nhiễm' },
    { icon: FileText, text: 'Lý lịch bản thân và gia đình rõ ràng' }
  ]
};

export default function TuyenSinh() {
  return (
    <Layout>
      {/* Hero Section - Green/Teal Theme (khác với gioi-thieu) */}
      <section className="relative bg-gradient-to-br from-emerald-600 via-teal-700 to-cyan-800 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-yellow-400/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-emerald-400/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6 animate-pulse">
              <Sparkles className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-bold text-yellow-400 uppercase tracking-wider">Tuyển sinh 2025</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Chào Mừng Bạn Đến Với
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-lime-300">
                Kỳ Tuyển Sinh 2025
              </span>
            </h1>

            {/* Stats Highlight */}
            <div className="flex flex-wrap justify-center gap-8 mb-10">
              <div className="text-center">
                <div className="text-5xl font-black text-yellow-400">~800</div>
                <div className="text-teal-200 text-sm font-medium">Chỉ tiêu dự kiến</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-yellow-400">6</div>
                <div className="text-teal-200 text-sm font-medium">Ngành đào tạo</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-yellow-400">3</div>
                <div className="text-teal-200 text-sm font-medium">Phương thức xét tuyển</div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4 justify-center">
              <button className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-teal-700 font-bold rounded-full hover:bg-yellow-400 hover:text-teal-800 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1">
                <FileCheck className="w-5 h-5" />
                Đăng ký xét tuyển
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
              <Link
                href="/chat-bot"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-bold rounded-full border border-white/30 hover:bg-white/20 transition-all duration-300"
              >
                <MessageCircle className="w-5 h-5" />
                Hỏi AI tư vấn
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Phương thức xét tuyển - NEW Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-emerald-100 border border-emerald-200 shadow-sm mb-4">
              <span className="text-emerald-800 text-sm font-bold tracking-widest uppercase">Phương thức xét tuyển</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              03 Phương Thức <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-600">Xét Tuyển</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-emerald-600 to-teal-500 mx-auto rounded-full"></div>
          </div>

          {/* Methods Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {ADMISSION_METHODS.map((method) => (
              <div key={method.id} className="group relative">
                <div className="bg-white rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2 h-full flex flex-col">
                  {/* Icon */}
                  <div className={`w-16 h-16 bg-gradient-to-br ${method.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg ${method.shadowColor} group-hover:scale-110 transition-transform`}>
                    <method.icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Number Badge */}
                  <div className="absolute top-6 right-6 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                    <span className="text-lg font-black text-gray-400">0{method.id}</span>
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-gray-900 mb-3">{method.title}</h3>
                  <p className="text-gray-600 mb-4 flex-1">{method.description}</p>

                  {/* Details */}
                  <div className="space-y-2 pt-4 border-t border-gray-100">
                    {method.details.map((detail, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm text-gray-600">
                        <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                        <span>{detail}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline Mốc thời gian - Horizontal Stepper Style */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100 border-t border-gray-200">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-white border border-gray-200 shadow-sm mb-4">
              <span className="text-gray-800 text-sm font-bold tracking-widest uppercase">Lịch tuyển sinh</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Các Mốc <span className="text-transparent bg-clip-text bg-gradient-to-r from-teal-600 to-cyan-600">Thời Gian</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-teal-600 to-cyan-500 mx-auto rounded-full"></div>
          </div>

          {/* Timeline Stepper */}
          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute top-16 left-0 right-0 h-1 bg-gradient-to-r from-emerald-200 via-teal-300 to-cyan-200 rounded-full hidden lg:block"></div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-6">
              {IMPORTANT_DATES.map((item, index) => (
                <div key={index} className="group relative">
                  {/* Connector Dot */}
                  <div className="hidden lg:flex absolute top-14 left-1/2 -translate-x-1/2 w-8 h-8 bg-white rounded-full border-4 border-teal-500 group-hover:border-cyan-500 transition-all duration-300 z-20 shadow-lg items-center justify-center">
                    <div className="w-3 h-3 rounded-full bg-teal-500 group-hover:bg-cyan-500 animate-pulse"></div>
                  </div>

                  {/* Card */}
                  <div className="mt-4 lg:mt-24 bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 group-hover:border-teal-200 group-hover:-translate-y-2">
                    {/* Step Number */}
                    <div className="flex items-center justify-between mb-4">
                      <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-cyan-500 rounded-xl flex items-center justify-center shadow-md">
                        <span className="text-white font-bold">{index + 1}</span>
                      </div>
                      <Calendar className="w-5 h-5 text-gray-400" />
                    </div>

                    {/* Date */}
                    <div className="text-lg font-black text-teal-600 mb-2">
                      {item.date}
                    </div>

                    {/* Event */}
                    <p className="text-gray-700 font-medium text-sm">
                      {item.event}
                    </p>

                    {/* Status Badge */}
                    <div className="mt-4 pt-4 border-t border-gray-100">
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 text-amber-700 text-xs font-bold rounded-full">
                        <Clock className="w-3 h-3" />
                        Sắp diễn ra
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Ngành đào tạo - Cards Grid */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-cyan-100 border border-cyan-200 shadow-sm mb-4">
              <span className="text-cyan-800 text-sm font-bold tracking-widest uppercase">Ngành đào tạo</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              06 Ngành <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-600 to-blue-600">Đào Tạo</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-cyan-600 to-blue-500 mx-auto rounded-full"></div>
          </div>

          {/* Program Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ADMISSION_PROGRAMS.map((program, index) => (
              <div key={index} className="group bg-gradient-to-br from-white to-gray-50 rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:border-cyan-200 hover:-translate-y-2">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:scale-110 transition-transform">
                    <GraduationCap className="w-7 h-7 text-white" />
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-gray-400 uppercase">Mã ngành</div>
                    <div className="text-lg font-black text-cyan-600">{program.code}</div>
                  </div>
                </div>

                {/* Name */}
                <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-cyan-700 transition-colors">
                  {program.name}
                </h3>

                {/* Info Grid */}
                <div className="grid grid-cols-3 gap-3 mb-4">
                  <div className="text-center p-3 bg-gray-100 rounded-xl">
                    <div className="text-lg font-black text-gray-900">{program.quota}</div>
                    <div className="text-xs text-gray-500">Chỉ tiêu</div>
                  </div>
                  <div className="text-center p-3 bg-gray-100 rounded-xl">
                    <div className="text-lg font-black text-gray-900">{program.duration}</div>
                    <div className="text-xs text-gray-500">Thời gian</div>
                  </div>
                  <div className="text-center p-3 bg-gray-100 rounded-xl">
                    <div className="text-sm font-bold text-gray-900">{program.degree}</div>
                    <div className="text-xs text-gray-500">Bằng cấp</div>
                  </div>
                </div>

                {/* CTA */}
                <button className="w-full flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white font-bold rounded-xl hover:from-cyan-600 hover:to-blue-700 transition-all duration-300 group-hover:shadow-lg">
                  Xem chi tiết
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Điều kiện xét tuyển */}
      <section className="py-20 bg-gradient-to-br from-teal-50 to-cyan-50 border-t border-teal-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Điều kiện chung */}
            <div className="bg-white rounded-3xl p-8 shadow-xl border border-teal-100">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 bg-gradient-to-br from-teal-500 to-teal-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <CheckCircle2 className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-xs font-bold text-teal-600 uppercase tracking-wider">Bắt buộc</div>
                  <h3 className="text-2xl font-black text-gray-900">Điều kiện chung</h3>
                </div>
              </div>
              <div className="space-y-4">
                {REQUIREMENTS.general.map((req, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 bg-teal-50 rounded-xl border border-teal-100">
                    <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm flex-shrink-0">
                      <req.icon className="w-5 h-5 text-teal-600" />
                    </div>
                    <p className="text-gray-700 font-medium pt-2">{req.text}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Điều kiện riêng */}
            <div className="bg-white rounded-3xl p-8 shadow-xl border border-cyan-100">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-14 h-14 bg-gradient-to-br from-cyan-500 to-blue-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <FileText className="w-7 h-7 text-white" />
                </div>
                <div>
                  <div className="text-xs font-bold text-cyan-600 uppercase tracking-wider">Đặc thù</div>
                  <h3 className="text-2xl font-black text-gray-900">Điều kiện riêng</h3>
                </div>
              </div>
              <div className="space-y-4">
                {REQUIREMENTS.specific.map((req, idx) => (
                  <div key={idx} className="flex items-start gap-4 p-4 bg-cyan-50 rounded-xl border border-cyan-100">
                    <div className="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm flex-shrink-0">
                      <req.icon className="w-5 h-5 text-cyan-600" />
                    </div>
                    <p className="text-gray-700 font-medium pt-2">{req.text}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quy trình xét tuyển */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-indigo-100 border border-indigo-200 shadow-sm mb-4">
              <span className="text-indigo-800 text-sm font-bold tracking-widest uppercase">Quy trình</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              04 Bước <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Xét Tuyển</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-indigo-600 to-purple-500 mx-auto rounded-full"></div>
          </div>

          {/* Process Steps */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {ADMISSION_PROCESS.map((item) => (
              <div key={item.step} className="group relative">
                {/* Arrow connector (hidden on last item) */}
                {item.step < 4 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <ChevronRight className="w-6 h-6 text-indigo-300" />
                  </div>
                )}

                <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl p-6 border border-indigo-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-2 h-full">
                  {/* Step Number */}
                  <div className="w-12 h-12 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg shadow-indigo-500/30 mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-xl font-black text-white">{item.step}</span>
                  </div>

                  {/* Icon */}
                  <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center mb-4 shadow-sm">
                    <item.icon className="w-6 h-6 text-indigo-600" />
                  </div>

                  {/* Content */}
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                  <p className="text-gray-600 text-sm">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact & CTA Section */}
      <section className="py-16 bg-gradient-to-r from-emerald-700 via-teal-700 to-cyan-800 text-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left - Contact Info */}
            <div>
              <h2 className="text-3xl font-bold mb-6">Hỗ trợ tuyển sinh</h2>
              <p className="text-teal-200 mb-8">
                Liên hệ ngay với chúng tôi để được tư vấn chi tiết về tuyển sinh năm 2025
              </p>

              <div className="space-y-4">
                <div className="flex items-center gap-4 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <Phone className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-teal-200 text-sm">Hotline</div>
                    <div className="font-bold text-lg">{SCHOOL_INFO.contact.phone}</div>
                  </div>
                </div>

                <div className="flex items-center gap-4 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
                  <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                    <Mail className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <div className="text-teal-200 text-sm">Email</div>
                    <div className="font-bold text-lg">{SCHOOL_INFO.contact.email}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right - CTA */}
            <div className="bg-white/10 backdrop-blur-sm rounded-3xl p-8 border border-white/20">
              <h3 className="text-2xl font-bold mb-4">Sẵn sàng đăng ký?</h3>
              <p className="text-teal-200 mb-6">
                Đừng bỏ lỡ cơ hội trở thành sinh viên của Trường Đại học An ninh Nhân dân
              </p>

              <div className="space-y-3">
                <button className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-white text-teal-700 font-bold rounded-xl hover:bg-yellow-400 hover:text-teal-800 transition-all duration-300 shadow-lg">
                  <FileCheck className="w-5 h-5" />
                  Đăng ký xét tuyển online
                </button>
                <button className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-white/20 text-white font-bold rounded-xl border border-white/30 hover:bg-white/30 transition-all duration-300">
                  <FileText className="w-5 h-5" />
                  Tải hồ sơ mẫu
                </button>
                <Link
                  href="/chat-bot"
                  className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-yellow-400 to-orange-400 text-gray-900 font-bold rounded-xl hover:from-yellow-500 hover:to-orange-500 transition-all duration-300 shadow-lg"
                >
                  <MessageCircle className="w-5 h-5" />
                  Chat với AI tư vấn
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
