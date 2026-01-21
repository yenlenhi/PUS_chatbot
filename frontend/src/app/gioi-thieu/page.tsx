'use client';

import React from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  Users, Award, BookOpen, Target, Eye, Calendar,
  MapPin, Phone, Mail, Globe, Building2, ArrowRight,
  GraduationCap, Shield, ExternalLink
} from 'lucide-react';
import { SCHOOL_INFO, HISTORY_MILESTONES } from '@/data/constants';

export default function GioiThieu() {
  return (
    <Layout>
      {/* Hero Section - Premium Design */}
      <section className="relative bg-gradient-to-br from-red-700 via-red-800 to-red-900 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-yellow-500/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-red-500/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-white/5 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
              <Building2 className="w-4 h-4 text-yellow-400" />
              <span className="text-sm font-medium text-yellow-400 uppercase tracking-wider">Trực thuộc Bộ Công an</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Trường Đại học
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-200">
                An ninh Nhân dân
              </span>
            </h1>

            {/* English Name */}
            <p className="text-lg md:text-xl text-red-200 font-medium mb-8">
              People's Security University
            </p>

            {/* Description */}
            <p className="text-lg text-red-100 max-w-2xl mx-auto leading-relaxed mb-10">
              Cơ sở đào tạo cán bộ an ninh chất lượng cao, trung tâm nghiên cứu khoa học
              và tham mưu chiến lược uy tín của lực lượng Công an nhân dân Việt Nam.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                href="/tuyen-sinh"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-red-700 font-bold rounded-full hover:bg-yellow-400 hover:text-red-800 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                <GraduationCap className="w-5 h-5" />
                Thông tin tuyển sinh
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/chat-bot"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-bold rounded-full border border-white/30 hover:bg-white/20 transition-all duration-300"
              >
                <Shield className="w-5 h-5" />
                Hỏi đáp AI
              </Link>
            </div>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Quick Info Cards */}
      <section className="py-12 -mt-8 relative z-20">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Address */}
            <div className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-1">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg shadow-red-500/30 group-hover:scale-110 transition-transform">
                  <MapPin className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Địa chỉ</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">{SCHOOL_INFO.contact.address}</p>
                </div>
              </div>
            </div>

            {/* Phone */}
            <div className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-1">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Hotline</h3>
                  <p className="text-sm text-gray-600">{SCHOOL_INFO.contact.phone}</p>
                </div>
              </div>
            </div>

            {/* Email */}
            <div className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-1">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/30 group-hover:scale-110 transition-transform">
                  <Mail className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Email</h3>
                  <p className="text-sm text-gray-600">{SCHOOL_INFO.contact.email}</p>
                </div>
              </div>
            </div>

            {/* Website */}
            <div className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-1">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform">
                  <Globe className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 mb-1">Website</h3>
                  <a
                    href={`https://${SCHOOL_INFO.contact.website}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                  >
                    {SCHOOL_INFO.contact.website}
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Vision Section */}
      <section className="py-20 bg-gradient-to-br from-red-50 via-orange-50 to-yellow-50 overflow-hidden relative border-t border-red-100">
        {/* Ambient Background */}
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
            {/* Mission */}
            <div className="group">
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-300 border border-red-100 h-full flex flex-col">
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
                <div className="w-full h-px bg-gradient-to-r from-red-200 via-red-300 to-transparent mb-6"></div>
                <div className="flex-1">
                  <p className="text-gray-700 leading-relaxed text-lg font-medium">
                    {SCHOOL_INFO.mission}
                  </p>
                </div>
                <div className="mt-6 pt-6 border-t border-red-100">
                  <div className="flex items-center gap-2 text-red-600 text-sm font-bold">
                    <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse"></div>
                    <span>Kiến Tạo Tương Lai</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Vision */}
            <div className="group">
              <div className="bg-white/90 backdrop-blur-sm rounded-3xl p-8 md:p-10 shadow-xl hover:shadow-2xl transition-all duration-300 border border-yellow-100 h-full flex flex-col">
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
                <div className="w-full h-px bg-gradient-to-r from-yellow-200 via-yellow-300 to-transparent mb-6"></div>
                <div className="flex-1">
                  <p className="text-gray-700 leading-relaxed text-lg font-medium">
                    {SCHOOL_INFO.vision}
                  </p>
                </div>
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

      {/* History Timeline Section */}
      <section className="py-20 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 relative overflow-hidden border-t border-blue-100">
        {/* Decorative Background */}
        <div className="absolute top-0 left-0 w-full h-full opacity-20 pointer-events-none">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-200 rounded-full blur-3xl"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-200 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 relative z-10">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-white/80 backdrop-blur-sm border border-blue-200 shadow-sm mb-4">
              <span className="text-blue-800 text-sm font-bold tracking-widest uppercase">Lịch sử hình thành</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Những Mốc Son <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Hào Hùng</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-blue-600 to-purple-500 mx-auto rounded-full"></div>
          </div>

          {/* Timeline */}
          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute top-12 left-0 right-0 h-1 bg-gradient-to-r from-blue-200 via-indigo-300 to-purple-200 rounded-full hidden md:block"></div>

            {/* Timeline Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 lg:gap-4">
              {HISTORY_MILESTONES.map((milestone, index) => (
                <div key={index} className="group relative">
                  {/* Connector Dot */}
                  <div className="hidden md:flex absolute top-10 left-1/2 -translate-x-1/2 w-6 h-6 bg-white rounded-full border-4 border-blue-600 group-hover:border-purple-600 transition-all duration-300 z-20 shadow-lg">
                    <div className="absolute inset-0 rounded-full bg-blue-600 group-hover:bg-purple-600 animate-pulse opacity-20"></div>
                  </div>

                  {/* Card */}
                  <div className="mt-4 md:mt-24 bg-white/90 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 border border-blue-100 group-hover:border-purple-200 group-hover:-translate-y-2 h-full">
                    {/* Year Badge */}
                    <div className="flex items-center justify-center mb-4">
                      <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl rotate-3 opacity-20 group-hover:rotate-6 transition-transform duration-300"></div>
                        <div className="relative bg-gradient-to-br from-blue-600 to-purple-600 text-white px-4 py-2 rounded-xl shadow-lg">
                          <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            <span className="text-xl font-black">{milestone.year}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Event */}
                    <div className="text-center">
                      <p className="text-gray-700 font-medium leading-relaxed text-sm">
                        {milestone.event}
                      </p>
                    </div>

                    {/* Bottom Accent */}
                    <div className="mt-4 pt-4 border-t border-blue-100">
                      <div className="flex items-center justify-center gap-1">
                        <div className="w-1 h-1 rounded-full bg-blue-600"></div>
                        <div className="w-2 h-2 rounded-full bg-purple-600 group-hover:animate-pulse"></div>
                        <div className="w-1 h-1 rounded-full bg-indigo-600"></div>
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
              Hơn <span className="font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">60 năm</span> xây dựng và phát triển
            </p>
          </div>
        </div>
      </section>

      {/* Achievements Section */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-gray-100 border border-gray-200 shadow-sm mb-4">
              <span className="text-gray-800 text-sm font-bold tracking-widest uppercase">Thành tựu</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Nổi Bật <span className="text-transparent bg-clip-text bg-gradient-to-r from-red-600 to-red-700">Và Tự Hào</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-red-600 to-red-500 mx-auto rounded-full"></div>
          </div>

          {/* Achievement Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Quality */}
            <div className="group bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-8 border border-yellow-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-yellow-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-yellow-500/30 group-hover:scale-110 transition-transform">
                <Award className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Chất lượng đào tạo</h3>
              <p className="text-gray-600">Đạt chuẩn kiểm định chất lượng giáo dục quốc gia</p>
            </div>

            {/* Research */}
            <div className="group bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border border-blue-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-blue-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-500/30 group-hover:scale-110 transition-transform">
                <BookOpen className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Nghiên cứu khoa học</h3>
              <p className="text-gray-600">Hàng trăm công trình nghiên cứu được công bố</p>
            </div>

            {/* Faculty */}
            <div className="group bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-8 border border-green-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-green-400 to-green-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-green-500/30 group-hover:scale-110 transition-transform">
                <Users className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Đội ngũ giảng viên</h3>
              <p className="text-gray-600">Trình độ cao, nhiều GS, PGS, TS đầu ngành</p>
            </div>

            {/* Strategic */}
            <div className="group bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-8 border border-red-200 hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
              <div className="w-14 h-14 bg-gradient-to-br from-red-400 to-red-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-red-500/30 group-hover:scale-110 transition-transform">
                <Target className="w-7 h-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Tham mưu chiến lược</h3>
              <p className="text-gray-600">Trung tâm tham mưu uy tín của Bộ Công an</p>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links Section */}
      <section className="py-16 bg-gradient-to-r from-gray-900 to-gray-800 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Khám phá thêm</h2>
            <p className="text-gray-400">Tìm hiểu chi tiết về các hoạt động của Nhà trường</p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link href="/dao-tao" className="group flex items-center gap-4 p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 hover:border-white/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center">
                <GraduationCap className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-white group-hover:text-blue-400 transition-colors">Đào tạo</h3>
                <p className="text-sm text-gray-400">Chương trình đào tạo</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all ml-auto" />
            </Link>

            <Link href="/tuyen-sinh" className="group flex items-center gap-4 p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 hover:border-white/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-xl flex items-center justify-center">
                <Users className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-white group-hover:text-red-400 transition-colors">Tuyển sinh</h3>
                <p className="text-sm text-gray-400">Thông tin tuyển sinh</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all ml-auto" />
            </Link>

            <Link href="/nghien-cuu" className="group flex items-center gap-4 p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 hover:border-white/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center">
                <BookOpen className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-white group-hover:text-purple-400 transition-colors">Nghiên cứu</h3>
                <p className="text-sm text-gray-400">Hoạt động nghiên cứu</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all ml-auto" />
            </Link>

            <Link href="/lien-he" className="group flex items-center gap-4 p-6 bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 hover:bg-white/10 hover:border-white/30 transition-all duration-300">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center">
                <Phone className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-white group-hover:text-green-400 transition-colors">Liên hệ</h3>
                <p className="text-sm text-gray-400">Thông tin liên hệ</p>
              </div>
              <ArrowRight className="w-5 h-5 text-gray-500 group-hover:text-white group-hover:translate-x-1 transition-all ml-auto" />
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
}
