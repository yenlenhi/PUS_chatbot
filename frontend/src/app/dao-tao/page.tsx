'use client';

import React from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  GraduationCap, BookOpen, Award, Users, Clock, FileText,
  ArrowRight, ChevronRight, Target, Lightbulb, Globe,
  Shield, Code, Scale, Search, Network, Brain, Briefcase,
  MessageCircle, CheckCircle2, Star
} from 'lucide-react';
import { ADMISSION_PROGRAMS, SCHOOL_INFO } from '@/data/constants';

// Hệ đào tạo
const TRAINING_LEVELS = [
  {
    level: 'Đại học',
    duration: '4 năm',
    degree: 'Cử nhân',
    description: 'Đào tạo cử nhân các ngành về an ninh, có trình độ chuyên môn cao, bản lĩnh chính trị vững vàng',
    icon: GraduationCap,
    color: 'from-blue-500 to-indigo-600',
    shadowColor: 'shadow-blue-500/30'
  },
  {
    level: 'Thạc sĩ',
    duration: '2 năm',
    degree: 'Thạc sĩ',
    description: 'Chương trình đào tạo chuyên sâu cho cán bộ có kinh nghiệm trong lĩnh vực an ninh',
    icon: Award,
    color: 'from-purple-500 to-violet-600',
    shadowColor: 'shadow-purple-500/30'
  },
  {
    level: 'Tiến sĩ',
    duration: '3-4 năm',
    degree: 'Tiến sĩ',
    description: 'Đào tạo chuyên gia nghiên cứu hàng đầu trong lĩnh vực an ninh quốc gia',
    icon: BookOpen,
    color: 'from-amber-500 to-orange-600',
    shadowColor: 'shadow-amber-500/30'
  }
];

// Chi tiết các ngành (bổ sung từ WEBSITE_CONTENT.md)
const PROGRAM_DETAILS = [
  {
    name: 'An ninh chính trị',
    code: '7229001',
    description: 'Đào tạo cán bộ có khả năng bảo vệ an ninh chính trị nội bộ, an ninh văn hóa - tư tưởng',
    icon: Shield,
    color: 'from-red-500 to-rose-600'
  },
  {
    name: 'An ninh kinh tế',
    code: '7229002',
    description: 'Chuyên sâu về phòng chống tội phạm kinh tế, bảo vệ an ninh kinh tế quốc gia',
    icon: Briefcase,
    color: 'from-emerald-500 to-teal-600'
  },
  {
    name: 'An ninh mạng',
    code: '7480201',
    description: 'Đào tạo kỹ sư/cử nhân chuyên về an toàn thông tin, phòng chống tội phạm công nghệ cao',
    icon: Code,
    color: 'from-cyan-500 to-blue-600'
  },
  {
    name: 'Điều tra hình sự',
    code: '7380107',
    description: 'Trang bị kiến thức, kỹ năng điều tra, phá án, tố tụng hình sự',
    icon: Search,
    color: 'from-orange-500 to-amber-600'
  },
  {
    name: 'Quản lý nhà nước về ANTT',
    code: '7340406',
    description: 'Đào tạo cán bộ quản lý hành chính về trật tự xã hội, cư trú, giao thông',
    icon: Scale,
    color: 'from-violet-500 to-purple-600'
  },
  {
    name: 'Tình báo',
    code: '7229003',
    description: 'Đào tạo nghiệp vụ tình báo chuyên sâu, bảo vệ an ninh quốc gia',
    icon: Network,
    color: 'from-slate-600 to-gray-700'
  }
];

// Phương pháp đào tạo
const TRAINING_METHODS = [
  {
    title: 'Lý thuyết kết hợp thực hành',
    description: 'Chương trình học cân bằng giữa kiến thức nền tảng và kỹ năng thực tế',
    icon: BookOpen
  },
  {
    title: 'Thực tập thực chiến',
    description: 'Sinh viên được tham gia thực tập tại các đơn vị an ninh thực tế',
    icon: Target
  },
  {
    title: 'Công nghệ hiện đại',
    description: 'Ứng dụng công nghệ thông tin và phương pháp giảng dạy tiên tiến',
    icon: Lightbulb
  },
  {
    title: 'Hợp tác quốc tế',
    description: 'Liên kết với các trường đại học uy tín trong và ngoài nước',
    icon: Globe
  }
];

// Điểm nổi bật
const HIGHLIGHTS = [
  { label: 'Quy mô sinh viên', value: 'Hàng ngàn', sublabel: 'học viên các hệ' },
  { label: 'Đội ngũ giảng viên', value: 'GS, PGS, TS', sublabel: 'đầu ngành' },
  { label: 'Ngành đào tạo', value: '6', sublabel: 'chuyên ngành' },
  { label: 'Thời gian đào tạo', value: '4 năm', sublabel: 'bậc đại học' }
];

export default function DaoTao() {
  return (
    <Layout>
      {/* Hero Section - Blue/Sky Theme */}
      <section className="relative bg-gradient-to-br from-blue-600 via-sky-700 to-indigo-800 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-cyan-400/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
              <GraduationCap className="w-4 h-4 text-cyan-300" />
              <span className="text-sm font-bold text-cyan-200 uppercase tracking-wider">Đào tạo chất lượng cao</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Chương Trình
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-white">
                Đào Tạo
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-blue-100 max-w-2xl mx-auto leading-relaxed mb-10">
              Đào tạo nguồn nhân lực chất lượng cao cho lực lượng Công an nhân dân với
              chương trình chuẩn quốc gia và phương pháp giảng dạy hiện đại
            </p>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
              {HIGHLIGHTS.map((item, index) => (
                <div key={index} className="bg-white/10 backdrop-blur-sm rounded-2xl p-4 border border-white/20">
                  <div className="text-3xl font-black text-cyan-300">{item.value}</div>
                  <div className="text-blue-200 text-sm font-medium">{item.sublabel}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Hệ đào tạo */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-blue-100 border border-blue-200 shadow-sm mb-4">
              <span className="text-blue-800 text-sm font-bold tracking-widest uppercase">Hệ đào tạo</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              03 Bậc <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-sky-600">Đào Tạo</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-blue-600 to-sky-500 mx-auto rounded-full"></div>
          </div>

          {/* Level Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {TRAINING_LEVELS.map((level, index) => (
              <div key={index} className="group bg-white rounded-3xl p-8 shadow-xl hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
                {/* Icon */}
                <div className={`w-16 h-16 bg-gradient-to-br ${level.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg ${level.shadowColor} group-hover:scale-110 transition-transform`}>
                  <level.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{level.level}</h3>

                {/* Info Tags */}
                <div className="flex gap-2 mb-4">
                  <span className="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600">
                    {level.duration}
                  </span>
                  <span className="px-3 py-1 bg-blue-100 rounded-full text-sm text-blue-700 font-medium">
                    {level.degree}
                  </span>
                </div>

                <p className="text-gray-600 leading-relaxed">{level.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Các ngành đào tạo */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100 border-t border-gray-200">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-white border border-gray-200 shadow-sm mb-4">
              <span className="text-gray-800 text-sm font-bold tracking-widest uppercase">Ngành đào tạo</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              06 Ngành <span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-600 to-indigo-600">Chuyên Môn</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-sky-600 to-indigo-500 mx-auto rounded-full"></div>
          </div>

          {/* Program Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {PROGRAM_DETAILS.map((program, index) => (
              <div key={index} className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-14 h-14 bg-gradient-to-br ${program.color} rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                    <program.icon className="w-7 h-7 text-white" />
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-bold text-gray-400 uppercase">Mã ngành</div>
                    <div className="text-lg font-black text-blue-600">{program.code}</div>
                  </div>
                </div>

                {/* Name */}
                <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-700 transition-colors">
                  {program.name}
                </h3>

                {/* Description */}
                <p className="text-gray-600 text-sm leading-relaxed mb-4">{program.description}</p>

                {/* Tags */}
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium">4 năm</span>
                  <span className="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-medium">Cử nhân</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Phương pháp đào tạo */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-indigo-100 border border-indigo-200 shadow-sm mb-4">
              <span className="text-indigo-800 text-sm font-bold tracking-widest uppercase">Phương pháp</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Đào Tạo <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600">Toàn Diện</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-indigo-600 to-purple-500 mx-auto rounded-full"></div>
          </div>

          {/* Method Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {TRAINING_METHODS.map((method, index) => (
              <div key={index} className="group text-center p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100 hover:shadow-lg transition-all duration-300 hover:-translate-y-2">
                <div className="w-14 h-14 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg group-hover:scale-110 transition-transform">
                  <method.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{method.title}</h3>
                <p className="text-gray-600 text-sm">{method.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Đội ngũ giảng viên */}
      <section className="py-20 bg-gradient-to-br from-blue-50 to-sky-50 border-t border-blue-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
            {/* Left - Info */}
            <div>
              <div className="inline-block px-6 py-2 rounded-full bg-white border border-blue-200 shadow-sm mb-6">
                <span className="text-blue-800 text-sm font-bold tracking-widest uppercase">Đội ngũ giảng viên</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-black text-gray-900 mb-6">
                Trình Độ Cao,
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-sky-600">
                  Tâm Huyết
                </span>
              </h2>
              <p className="text-gray-600 leading-relaxed mb-8">
                Đội ngũ giảng viên của Nhà trường bao gồm nhiều Giáo sư, Phó Giáo sư, Tiến sĩ
                đầu ngành trong các lĩnh vực an ninh, luật học và khoa học xã hội.
                Tất cả đều có kinh nghiệm thực tiễn phong phú và tâm huyết với nghề.
              </p>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-3 p-4 bg-white rounded-xl shadow-sm border border-blue-100">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-sky-600 rounded-lg flex items-center justify-center">
                    <Star className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">Giáo sư, PGS</div>
                    <div className="text-sm text-gray-500">Đầu ngành</div>
                  </div>
                </div>
                <div className="flex items-center gap-3 p-4 bg-white rounded-xl shadow-sm border border-blue-100">
                  <div className="w-10 h-10 bg-gradient-to-br from-sky-500 to-indigo-600 rounded-lg flex items-center justify-center">
                    <Award className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">Tiến sĩ</div>
                    <div className="text-sm text-gray-500">Chuyên môn sâu</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right - Features */}
            <div className="bg-white rounded-3xl p-8 shadow-xl border border-blue-100">
              <h3 className="text-xl font-bold text-gray-900 mb-6">Điểm nổi bật</h3>
              <div className="space-y-4">
                {[
                  'Kinh nghiệm thực tiễn phong phú trong lĩnh vực an ninh',
                  'Nghiên cứu khoa học đạt tầm quốc gia và quốc tế',
                  'Tâm huyết, trách nhiệm với sự nghiệp đào tạo',
                  'Cập nhật kiến thức mới, phương pháp hiện đại',
                  'Hướng dẫn sinh viên tận tình, chu đáo'
                ].map((item, idx) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-blue-50 rounded-xl">
                    <CheckCircle2 className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
                    <span className="text-gray-700">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-700 via-sky-700 to-indigo-800 text-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-5xl mx-auto">
            {/* Left */}
            <div>
              <h2 className="text-3xl font-bold mb-4">Quan tâm đến chương trình đào tạo?</h2>
              <p className="text-blue-200 mb-6">
                Liên hệ ngay để được tư vấn chi tiết về các ngành đào tạo và điều kiện tuyển sinh
              </p>
              <div className="flex items-center gap-4">
                <Link
                  href="/tuyen-sinh"
                  className="group inline-flex items-center gap-2 px-6 py-3 bg-white text-blue-700 font-bold rounded-full hover:bg-cyan-300 hover:text-blue-800 transition-all duration-300 shadow-lg"
                >
                  <GraduationCap className="w-5 h-5" />
                  Tuyển sinh 2025
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/chat-bot"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white font-bold rounded-full border border-white/30 hover:bg-white/20 transition-all duration-300"
                >
                  <MessageCircle className="w-5 h-5" />
                  Hỏi AI
                </Link>
              </div>
            </div>

            {/* Right - Contact */}
            <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20">
              <h3 className="text-xl font-bold mb-4">Liên hệ Phòng Đào tạo</h3>
              <div className="space-y-3">
                <p className="flex items-center gap-3 text-blue-100">
                  <span className="font-medium text-white">Hotline:</span>
                  {SCHOOL_INFO.contact.phone}
                </p>
                <p className="flex items-center gap-3 text-blue-100">
                  <span className="font-medium text-white">Email:</span>
                  daotao@dhannd.edu.vn
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
