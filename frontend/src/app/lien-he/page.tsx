'use client';

import React from 'react';
import Layout from '@/components/Layout';
import Link from 'next/link';
import {
  MapPin, Phone, Mail, Clock, Globe, Facebook, Youtube,
  MessageCircle, Send, Building2, Users, BookOpen,
  GraduationCap, ArrowRight, ExternalLink, Headphones
} from 'lucide-react';
import { SCHOOL_INFO } from '@/data/constants';

// Thông tin phòng ban
const DEPARTMENTS = [
  {
    name: 'Phòng Đào tạo',
    phone: '0283.896.3883',
    email: 'daotao@dhannd.edu.vn',
    icon: GraduationCap,
    color: 'from-blue-500 to-indigo-600'
  },
  {
    name: 'Phòng Tuyển sinh',
    phone: '0283.896.3883',
    email: 'tuyensinh@dhannd.edu.vn',
    icon: Users,
    color: 'from-emerald-500 to-teal-600'
  },
  {
    name: 'Phòng Công tác sinh viên',
    phone: '0283.896.3883',
    email: 'ctsv@dhannd.edu.vn',
    icon: Users,
    color: 'from-purple-500 to-violet-600'
  },
  {
    name: 'Phòng Khoa học Công nghệ',
    phone: '0283.896.3883',
    email: 'khcn@dhannd.edu.vn',
    icon: BookOpen,
    color: 'from-rose-500 to-pink-600'
  }
];

// Quick Links
const QUICK_LINKS = [
  { title: 'Giới thiệu', href: '/gioi-thieu', icon: Building2, color: 'from-red-500 to-rose-600' },
  { title: 'Đào tạo', href: '/dao-tao', icon: BookOpen, color: 'from-blue-500 to-indigo-600' },
  { title: 'Tuyển sinh', href: '/tuyen-sinh', icon: GraduationCap, color: 'from-emerald-500 to-teal-600' },
  { title: 'Nghiên cứu', href: '/nghien-cuu', icon: BookOpen, color: 'from-purple-500 to-violet-600' }
];

export default function LienHe() {
  return (
    <Layout>
      {/* Hero Section - Orange/Amber Theme */}
      <section className="relative bg-gradient-to-br from-orange-500 via-amber-600 to-yellow-600 text-white overflow-hidden">
        {/* Background Decorations */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-white/10 rounded-full blur-3xl"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-orange-400/20 rounded-full blur-3xl"></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-yellow-400/10 rounded-full blur-3xl"></div>
        </div>

        <div className="container mx-auto px-4 py-20 relative z-10">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-full mb-6">
              <Headphones className="w-4 h-4 text-yellow-300" />
              <span className="text-sm font-bold text-yellow-200 uppercase tracking-wider">Hỗ trợ 24/7</span>
            </div>

            {/* Title */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-black mb-6 leading-tight">
              Liên Hệ
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-200 to-white">
                Với Chúng Tôi
              </span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg md:text-xl text-orange-100 max-w-2xl mx-auto leading-relaxed mb-10">
              Chúng tôi sẵn sàng hỗ trợ và giải đáp mọi thắc mắc của bạn.
              Liên hệ ngay để được tư vấn chi tiết!
            </p>

            {/* CTA */}
            <div className="flex flex-wrap gap-4 justify-center">
              <Link
                href="/chat-bot"
                className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-orange-600 font-bold rounded-full hover:bg-yellow-300 hover:text-orange-700 transition-all duration-300 shadow-lg hover:shadow-xl hover:-translate-y-1"
              >
                <MessageCircle className="w-5 h-5" />
                Chat với AI 24/7
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href={`tel:${SCHOOL_INFO.contact.phone}`}
                className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-bold rounded-full border border-white/30 hover:bg-white/20 transition-all duration-300"
              >
                <Phone className="w-5 h-5" />
                Gọi ngay
              </a>
            </div>
          </div>
        </div>

        {/* Bottom Wave */}
        <div className="absolute bottom-0 left-0 right-0 h-16 bg-gradient-to-t from-[#f9fafb] to-transparent"></div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-orange-100 border border-orange-200 shadow-sm mb-4">
              <span className="text-orange-800 text-sm font-bold tracking-widest uppercase">Thông tin liên hệ</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Kết Nối <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-amber-600">Ngay</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-orange-600 to-amber-500 mx-auto rounded-full"></div>
          </div>

          {/* Contact Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {/* Address */}
            <div className="group bg-gradient-to-br from-orange-50 to-amber-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-orange-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-amber-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-orange-500/30 group-hover:scale-110 transition-transform">
                <MapPin className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Địa chỉ</h3>
              <p className="text-gray-600 leading-relaxed">
                {SCHOOL_INFO.contact.address}
              </p>
            </div>

            {/* Phone */}
            <div className="group bg-gradient-to-br from-blue-50 to-indigo-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-blue-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-blue-500/30 group-hover:scale-110 transition-transform">
                <Phone className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Điện thoại</h3>
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium">Tổng đài:</span> {SCHOOL_INFO.contact.phone}
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">Fax:</span> {SCHOOL_INFO.contact.phone}
                </p>
              </div>
            </div>

            {/* Email */}
            <div className="group bg-gradient-to-br from-purple-50 to-violet-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-purple-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-violet-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-purple-500/30 group-hover:scale-110 transition-transform">
                <Mail className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Email</h3>
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium">Chung:</span> {SCHOOL_INFO.contact.email}
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">Tuyển sinh:</span> tuyensinh@dhannd.edu.vn
                </p>
              </div>
            </div>

            {/* Working Hours */}
            <div className="group bg-gradient-to-br from-emerald-50 to-teal-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-emerald-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-emerald-500/30 group-hover:scale-110 transition-transform">
                <Clock className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Giờ làm việc</h3>
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-medium">T2 - T6:</span> 8:00 - 17:00
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">T7:</span> 8:00 - 12:00
                </p>
                <p className="text-gray-600">
                  <span className="font-medium">CN:</span> Nghỉ
                </p>
              </div>
            </div>

            {/* Website */}
            <div className="group bg-gradient-to-br from-red-50 to-rose-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-red-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-red-500 to-rose-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-red-500/30 group-hover:scale-110 transition-transform">
                <Globe className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Website</h3>
              <a
                href={`https://${SCHOOL_INFO.contact.website}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-red-600 hover:text-red-700 font-medium"
              >
                {SCHOOL_INFO.contact.website}
                <ExternalLink className="w-4 h-4" />
              </a>
            </div>

            {/* Social Media */}
            <div className="group bg-gradient-to-br from-cyan-50 to-blue-50 rounded-3xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border border-cyan-100 hover:-translate-y-2">
              <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-blue-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-cyan-500/30 group-hover:scale-110 transition-transform">
                <MessageCircle className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Mạng xã hội</h3>
              <div className="flex items-center gap-4">
                <a href="#" className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                  <Facebook className="w-4 h-4" />
                  <span className="text-sm font-medium">Facebook</span>
                </a>
                <a href="#" className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                  <Youtube className="w-4 h-4" />
                  <span className="text-sm font-medium">Youtube</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Departments Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-gray-100 border-t border-gray-200">
        <div className="container mx-auto px-4">
          {/* Section Header */}
          <div className="text-center mb-16">
            <div className="inline-block px-6 py-2 rounded-full bg-white border border-gray-200 shadow-sm mb-4">
              <span className="text-gray-800 text-sm font-bold tracking-widest uppercase">Các phòng ban</span>
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-gray-900 mb-4">
              Liên Hệ <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-600 to-orange-600">Trực Tiếp</span>
            </h2>
            <div className="w-24 h-1 bg-gradient-to-r from-amber-600 to-orange-500 mx-auto rounded-full"></div>
          </div>

          {/* Department Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {DEPARTMENTS.map((dept, index) => (
              <div key={index} className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 border border-gray-100 hover:-translate-y-2">
                {/* Icon */}
                <div className={`w-14 h-14 bg-gradient-to-br ${dept.color} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-transform`}>
                  <dept.icon className="w-7 h-7 text-white" />
                </div>

                {/* Name */}
                <h3 className="text-lg font-bold text-gray-900 mb-4">{dept.name}</h3>

                {/* Contact Info */}
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span>{dept.phone}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="truncate">{dept.email}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Map & Contact Form */}
      <section className="py-20 bg-white border-t border-gray-100">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
            {/* Map */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl flex items-center justify-center">
                  <MapPin className="w-5 h-5 text-white" />
                </div>
                Bản đồ
              </h3>
              <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl overflow-hidden shadow-lg border border-gray-200">
                <iframe
                  src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3918.2311711946396!2d106.75892181533428!3d10.871222660289!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3175276398969f7b%3A0x9672b7efd0893fc4!2zVHLGsOG7nW5nIMSQ4bqhaSBo4buNYyBBbiBuaW5oIE5ow6JuIGTDom4!5e0!3m2!1svi!2s!4v1705830000000!5m2!1svi!2s"
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  allowFullScreen
                  loading="lazy"
                  referrerPolicy="no-referrer-when-downgrade"
                  className="w-full h-full"
                ></iframe>
              </div>
              <p className="text-sm text-gray-500 mt-3 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Nhấn vào bản đồ để xem đường đi chi tiết
              </p>
            </div>

            {/* Contact Form */}
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl flex items-center justify-center">
                  <Send className="w-5 h-5 text-white" />
                </div>
                Gửi tin nhắn
              </h3>
              <form className="bg-gradient-to-br from-orange-50 to-amber-50 rounded-2xl p-8 shadow-lg border border-orange-100">
                <div className="space-y-5">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      Họ và tên *
                    </label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                      placeholder="Nhập họ tên của bạn"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                      placeholder="Nhập email của bạn"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      Số điện thoại
                    </label>
                    <input
                      type="tel"
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
                      placeholder="Nhập số điện thoại"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">
                      Nội dung *
                    </label>
                    <textarea
                      rows={4}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all resize-none"
                      placeholder="Nhập nội dung tin nhắn"
                    ></textarea>
                  </div>
                  <button
                    type="submit"
                    className="w-full flex items-center justify-center gap-2 px-6 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold rounded-xl hover:from-orange-600 hover:to-amber-600 transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    <Send className="w-5 h-5" />
                    Gửi tin nhắn
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="py-16 bg-gradient-to-r from-orange-600 via-amber-600 to-yellow-600 text-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Khám phá thêm</h2>
            <p className="text-orange-200">Tìm hiểu chi tiết về các hoạt động của Nhà trường</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            {QUICK_LINKS.map((link, index) => (
              <Link
                key={index}
                href={link.href}
                className="group flex flex-col items-center gap-3 p-6 bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 hover:bg-white/20 transition-all duration-300"
              >
                <div className={`w-14 h-14 bg-gradient-to-br ${link.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform`}>
                  <link.icon className="w-7 h-7 text-white" />
                </div>
                <span className="font-bold text-white">{link.title}</span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* AI CTA */}
      <section className="py-12 bg-gradient-to-r from-gray-900 to-gray-800">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6 max-w-4xl mx-auto">
            <div className="text-center md:text-left">
              <h3 className="text-2xl font-bold text-white mb-2">Cần hỗ trợ nhanh?</h3>
              <p className="text-gray-400">Chat với AI chatbot để được tư vấn 24/7</p>
            </div>
            <Link
              href="/chat-bot"
              className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-orange-500 to-amber-500 text-white font-bold rounded-full hover:from-orange-600 hover:to-amber-600 transition-all duration-300 shadow-lg hover:shadow-xl"
            >
              <MessageCircle className="w-5 h-5" />
              Chat ngay với AI
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </div>
        </div>
      </section>
    </Layout>
  );
}
