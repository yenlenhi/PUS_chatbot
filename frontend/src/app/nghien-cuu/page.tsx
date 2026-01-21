'use client';

import React from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  Brain, MessageSquare, Search, Zap, BookOpen, Users,
  Sparkles, Shield, Globe, Database, Server, Code,
  ArrowRight, ChevronRight, Star, CheckCircle2,
  Cpu, Network, FileSearch, MessageCirclePlus,
  GraduationCap, Lightbulb, FlaskConical
} from 'lucide-react';
import { SCHOOL_INFO } from '@/data/constants';

// Tính năng chính của hệ thống
const MAIN_FEATURES = [
  {
    icon: Brain,
    title: 'AI Conversation',
    description: 'Trò chuyện tự nhiên với AI, hiểu ngữ cảnh và ghi nhớ lịch sử hội thoại',
    color: 'from-violet-500 to-purple-600',
    shadowColor: 'shadow-violet-500/30'
  },
  {
    icon: FileSearch,
    title: 'Tìm kiếm Thông minh',
    description: 'Tìm kiếm semantic dựa trên ý nghĩa, không chỉ từ khóa đơn thuần',
    color: 'from-emerald-500 to-teal-600',
    shadowColor: 'shadow-emerald-500/30'
  },
  {
    icon: MessageCirclePlus,
    title: 'Câu hỏi Gợi ý',
    description: 'Tự động đề xuất câu hỏi phổ biến dựa trên ngữ cảnh hội thoại',
    color: 'from-blue-500 to-indigo-600',
    shadowColor: 'shadow-blue-500/30'
  },
  {
    icon: Zap,
    title: 'Phản hồi Nhanh',
    description: 'Thời gian phản hồi dưới 3 giây với hỗ trợ streaming realtime',
    color: 'from-amber-500 to-orange-600',
    shadowColor: 'shadow-amber-500/30'
  },
  {
    icon: BookOpen,
    title: 'Đa dạng Nguồn',
    description: 'Tích hợp thông tin từ văn bản, PDF, hình ảnh và tài liệu chính thống',
    color: 'from-rose-500 to-pink-600',
    shadowColor: 'shadow-rose-500/30'
  },
  {
    icon: Shield,
    title: 'Bảo mật Cao',
    description: 'Dữ liệu mã hóa, tuân thủ quy định bảo mật và quyền riêng tư',
    color: 'from-cyan-500 to-blue-600',
    shadowColor: 'shadow-cyan-500/30'
  }
];

// Tech Stack
const TECH_STACK = [
  { category: 'Frontend', techs: ['Next.js', 'React', 'TypeScript'], icon: Code, color: 'from-blue-500 to-indigo-500' },
  { category: 'Backend', techs: ['Python', 'FastAPI'], icon: Server, color: 'from-green-500 to-emerald-500' },
  { category: 'AI Model', techs: ['Gemini Pro', 'GPT-4'], icon: Brain, color: 'from-purple-500 to-violet-500' },
  { category: 'Database', techs: ['PostgreSQL', 'Supabase'], icon: Database, color: 'from-cyan-500 to-blue-500' },
  { category: 'Vector DB', techs: ['pgvector', 'Embeddings'], icon: Network, color: 'from-pink-500 to-rose-500' },
  { category: 'Deployment', techs: ['Railway', 'Docker'], icon: Cpu, color: 'from-orange-500 to-amber-500' }
];

// Hướng dẫn sử dụng
const USAGE_STEPS = [
  { step: 1, title: 'Truy cập Chatbot', description: 'Nhấn vào "Hỏi đáp AI" hoặc biểu tượng chat ở góc màn hình' },
  { step: 2, title: 'Đặt Câu hỏi', description: 'Nhập câu hỏi về tuyển sinh, đào tạo, học phí, điều kiện...' },
  { step: 3, title: 'Xem Gợi ý', description: 'Nhấn vào câu hỏi được đề xuất để khám phá thêm thông tin' },
  { step: 4, title: 'Đánh giá', description: 'Like/Dislike câu trả lời để giúp cải thiện hệ thống' }
];

// Nhóm tác giả
const TEAM_MEMBERS = [
  { name: 'VŨ QUỐC HƯNG', class: 'VB2 D5', role: 'Trưởng nhóm', color: 'from-blue-500 to-indigo-600' },
  { name: 'TRƯƠNG VĂN KHẢI', class: 'VB2 D5', role: 'Thành viên', color: 'from-emerald-500 to-teal-600' },
  { name: 'NGUYỄN HỮU TẤN DŨNG', class: 'D32C', role: 'Thành viên', color: 'from-purple-500 to-violet-600' }
];

// Lĩnh vực nghiên cứu của trường (từ WEBSITE_CONTENT.md)
const RESEARCH_FIELDS = [
  { name: 'Khoa học An ninh', icon: Shield },
  { name: 'Luật học', icon: BookOpen },
  { name: 'Xây dựng lực lượng CAND', icon: Users },
  { name: 'Khoa học lãnh đạo, chỉ huy', icon: GraduationCap }
];

export default function NghienCuu() {
  return (
    <Layout>
      {/* Hero Section - Purple/Violet Theme */}
      <section className="relative bg-gradient-to-br from-violet-700 via-purple-800 to-indigo-900 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-pink-400/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-violet-400/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
          {/* Animated grid background */}
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxjaXJjbGUgY3g9IjIwIiBjeT0iMjAiIHI9IjEiIGZpbGw9InJnYmEoMjU1LDI1NSwyNTUsMC4xKSIvPjwvZz48L3N2Zz4=')] opacity-30"></div>
        </div>

        <div className="container mx-auto px-4 py-24 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
              <FlaskConical className="w-4 h-4 text-pink-400" />
              <span className="text-sm font-bold text-pink-300 uppercase tracking-wider">Nghiên cứu & Phát triển</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Hệ Thống AI Chatbot
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-pink-400 to-violet-300">
                Hỗ Trợ Tuyển Sinh
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-purple-200 max-w-2xl mx-auto leading-relaxed mb-10">
              Ứng dụng công nghệ RAG (Retrieval-Augmented Generation) và mô hình ngôn ngữ lớn (LLM)
              để tự động hóa và nâng cao chất lượng tư vấn tuyển sinh
            </p>

            {/* Stats */}
            <div className="flex flex-wrap justify-center gap-8 mb-10">
              <div className="text-center">
                <div className="text-5xl font-black text-pink-400">v2.0</div>
                <div className="text-purple-300 text-sm font-medium">Phiên bản</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-pink-400">1000+</div>
                <div className="text-purple-300 text-sm font-medium">Trang tài liệu</div>
              </div>
              <div className="text-center">
                <div className="text-5xl font-black text-pink-400">95%+</div>
                <div className="text-purple-300 text-sm font-medium">Độ chính xác</div>
              </div>
            </div>

            {/* CTA */}
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                href="/chat-bot"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-700 font-bold rounded-full hover:bg-pink-400 hover:text-white transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                <MessageSquare className="w-5 h-5" />
                Trải nghiệm ngay
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Tính năng chính */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-violet-100 border border-violet-200 shadow-sm mb-4">
              <span className="text-violet-800 text-sm font-bold tracking-widest uppercase">Tính năng</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Công Nghệ <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600">Tiên Tiến</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-violet-600 to-purple-500 mx-auto rounded-full"></div>
          </div>

          {/* Feature Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {MAIN_FEATURES.map((feature, index) => (
              <div key={index} className="group bg-white rounded-3xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
                {/* Icon */}
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg ${feature.shadowColor} group-hover:scale-110 transition-transform`}>
                  <feature.icon className="w-8 h-8 text-white" />
                </div>

                {/* Content */}
                <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Hướng dẫn sử dụng */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100 border-t border-gray-200">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-white border border-gray-200 shadow-sm mb-4">
              <span className="text-gray-800 text-sm font-bold tracking-widest uppercase">Hướng dẫn</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Cách <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600">Sử Dụng</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-purple-600 to-pink-500 mx-auto rounded-full"></div>
          </div>

          {/* Steps */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {USAGE_STEPS.map((item) => (
              <div key={item.step} className="group relative">
                {/* Arrow connector */}
                {item.step < 4 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <ChevronRight className="w-6 h-6 text-purple-300" />
                  </div>
                )}

                <div className="bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-2 h-full">
                  {/* Step Number */}
                  <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-violet-600 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-500/30 mb-4 group-hover:scale-110 transition-transform">
                    <span className="text-2xl font-black text-white">{item.step}</span>
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

      {/* Tech Stack */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-indigo-100 border border-indigo-200 shadow-sm mb-4">
              <span className="text-indigo-800 text-sm font-bold tracking-widest uppercase">Công nghệ</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Tech <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-blue-600">Stack</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-indigo-600 to-blue-500 mx-auto rounded-full"></div>
          </div>

          {/* Tech Cards */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {TECH_STACK.map((tech, index) => (
              <div key={index} className="group bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl p-6 border border-gray-200 hover:shadow-lg transition-all duration-300 hover:-translate-y-1 text-center">
                <div className={`w-12 h-12 bg-gradient-to-br ${tech.color} rounded-xl flex items-center justify-center mb-4 mx-auto shadow-lg group-hover:scale-110 transition-transform`}>
                  <tech.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="font-bold text-gray-900 mb-2">{tech.category}</h3>
                <div className="space-y-1">
                  {tech.techs.map((t, i) => (
                    <div key={i} className="text-xs text-gray-500">{t}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Lĩnh vực nghiên cứu của Trường */}
      <section className="py-20 bg-gradient-to-br from-violet-50 to-purple-50 border-t border-violet-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left - Info */}
            <div>
              <div className="inline-block px-6 py-2 rounded-full bg-white border border-violet-200 shadow-sm mb-6">
                <span className="text-violet-800 text-sm font-bold tracking-widest uppercase">Nghiên cứu khoa học</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-black text-gray-900 mb-6">
                Trung Tâm Nghiên Cứu
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-violet-600 to-purple-600">
                  Chiến Lược
                </span>
              </h2>
              <p className="text-gray-600 leading-relaxed mb-8">
                Trường Đại học An ninh Nhân dân là trung tâm nghiên cứu chiến lược uy tín của Bộ Công an,
                mở rộng quan hệ hợp tác nghiên cứu và trao đổi học thuật với các trường đại học Cảnh sát/An ninh
                trong khu vực và quốc tế.
              </p>

              {/* Research Fields */}
              <div className="grid grid-cols-2 gap-4">
                {RESEARCH_FIELDS.map((field, index) => (
                  <div key={index} className="flex items-center gap-3 p-4 bg-white rounded-xl shadow-sm border border-violet-100">
                    <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center">
                      <field.icon className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-medium text-gray-800 text-sm">{field.name}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Right - Journal */}
            <div className="bg-white rounded-3xl p-8 shadow-xl border border-violet-100">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-gradient-to-br from-violet-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <BookOpen className="w-8 h-8 text-white" />
                </div>
                <div>
                  <div className="text-xs font-bold text-violet-600 uppercase tracking-wider">Xuất bản định kỳ</div>
                  <h3 className="text-xl font-black text-gray-900">Tạp chí Khoa học</h3>
                </div>
              </div>
              <p className="text-gray-600 leading-relaxed mb-6">
                Tạp chí Khoa học An ninh nhân dân là ấn phẩm khoa học chính thức của Nhà trường,
                công bố các công trình nghiên cứu, bài báo khoa học của giảng viên, nghiên cứu sinh
                và cộng tác viên trong lĩnh vực an ninh, luật học và khoa học liên quan.
              </p>
              <div className="flex items-center gap-2 text-violet-600 font-bold">
                <Globe className="w-5 h-5" />
                <span>Hợp tác quốc tế rộng rãi</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Nhóm tác giả */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-pink-100 border border-pink-200 shadow-sm mb-4">
              <span className="text-pink-800 text-sm font-bold tracking-widest uppercase">Đội ngũ phát triển</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Nhóm <span className="text-transparent bg-clip-text bg-gradient-to-r from-pink-600 to-rose-600">Tác Giả</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-pink-600 to-rose-500 mx-auto rounded-full"></div>
          </div>

          {/* Team Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {TEAM_MEMBERS.map((member, index) => (
              <div key={index} className="group text-center">
                <div className="bg-gradient-to-br from-gray-50 to-gray-100 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
                  {/* Avatar */}
                  <div className={`w-20 h-20 bg-gradient-to-br ${member.color} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform`}>
                    <Users className="w-10 h-10 text-white" />
                  </div>

                  {/* Info */}
                  <h3 className="text-lg font-bold text-gray-900 mb-1">{member.name}</h3>
                  <p className="text-gray-500 text-sm mb-3">Lớp: {member.class}</p>

                  {/* Role Badge */}
                  <div className={`inline-flex items-center gap-1 px-3 py-1 bg-gradient-to-r ${member.color} text-white text-xs font-bold rounded-full`}>
                    <Sparkles className="w-3 h-3" />
                    <span>{member.role}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-violet-700 via-purple-700 to-indigo-800 text-white">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Sẵn sàng trải nghiệm?
            </h2>
            <p className="text-purple-200 mb-10 text-lg">
              Bắt đầu trò chuyện với AI chatbot để được tư vấn thông tin tuyển sinh 24/7
            </p>

            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                href="/chat-bot"
                className="group inline-flex items-center gap-2 px-10 py-5 bg-white text-purple-700 font-bold rounded-full hover:bg-pink-400 hover:text-white transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1 text-lg"
              >
                <MessageSquare className="w-6 h-6" />
                Chat với AI ngay
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>

            {/* Contact Info */}
            <div className="mt-12 pt-8 border-t border-white/20">
              <p className="text-purple-300 mb-4">Hỗ trợ kỹ thuật</p>
              <div className="flex flex-wrap gap-6 justify-center text-sm">
                <span className="text-white">{SCHOOL_INFO.contact.email}</span>
                <span className="text-purple-400">|</span>
                <span className="text-white">{SCHOOL_INFO.contact.phone}</span>
                <span className="text-purple-400">|</span>
                <span className="text-white">24/7 (AI tự động)</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
}
