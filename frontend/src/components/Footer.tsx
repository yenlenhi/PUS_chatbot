import React from 'react';
import Link from 'next/link';
import { MapPin, Phone, Mail, Globe, Facebook, Youtube, MessageCircle, Settings, ShieldCheck } from 'lucide-react';
import { SCHOOL_INFO } from '@/data/constants';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white pt-16 pb-8 border-t-4 border-red-700">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-12 mb-12">
          {/* Thông tin trường */}
          <div className="space-y-6">
            <div className="flex items-center gap-3">
              <ShieldCheck className="w-10 h-10 text-red-600" />
              <div>
                <h3 className="text-lg font-bold leading-tight text-white">
                  ĐẠI HỌC<br />
                  <span className="text-red-500">AN NINH NHÂN DÂN</span>
                </h3>
              </div>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Cơ sở đào tạo cán bộ an ninh chất lượng cao, trung tâm nghiên cứu khoa học và tham mưu chiến lược uy tín của lực lượng Công an nhân dân.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-blue-600 hover:text-white transition-all duration-300">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-red-600 hover:text-white transition-all duration-300">
                <Youtube className="w-5 h-5" />
              </a>
              <a href={SCHOOL_INFO.contact.website} target="_blank" className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center text-gray-400 hover:bg-green-600 hover:text-white transition-all duration-300">
                <Globe className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Liên kết nhanh */}
          <div>
            <h4 className="text-lg font-bold mb-6 text-white border-l-4 border-red-600 pl-3">Liên kết nhanh</h4>
            <ul className="space-y-3 font-medium">
              {[
                { label: 'Giới thiệu', href: '/gioi-thieu' },
                { label: 'Đào tạo', href: '/dao-tao' },
                { label: 'Tuyển sinh', href: '/tuyen-sinh' },
                { label: 'Nghiên cứu khoa học', href: '/nghien-cuu' },
                { label: 'Tin tức & Sự kiện', href: '/tin-tuc' },
              ].map((item, index) => (
                <li key={index}>
                  <Link href={item.href} className="text-gray-400 hover:text-red-500 hover:translate-x-1 transition-all duration-200 inline-block">
                    {item.label}
                  </Link>
                </li>
              ))}
              <li>
                <Link href="/chat-bot" className="text-yellow-500 hover:text-yellow-400 transition-colors duration-200 flex items-center gap-2">
                  <MessageCircle className="w-4 h-4" />
                  Hỏi đáp AI
                </Link>
              </li>
            </ul>
          </div>

          {/* Thông tin liên hệ */}
          <div>
            <h4 className="text-lg font-bold mb-6 text-white border-l-4 border-red-600 pl-3">Liên hệ</h4>
            <div className="space-y-4 text-sm text-gray-400">
              <div className="flex items-start gap-3 group">
                <MapPin className="w-5 h-5 text-red-600 mt-0.5 group-hover:animate-bounce" />
                <p className="group-hover:text-white transition-colors">{SCHOOL_INFO.contact.address}</p>
              </div>
              <div className="flex items-center gap-3 group">
                <Phone className="w-5 h-5 text-red-600 group-hover:rotate-12 transition-transform" />
                <p className="group-hover:text-white transition-colors">{SCHOOL_INFO.contact.phone}</p>
              </div>
              <div className="flex items-center gap-3 group">
                <Mail className="w-5 h-5 text-red-600 group-hover:scale-110 transition-transform" />
                <p className="group-hover:text-white transition-colors">{SCHOOL_INFO.contact.email}</p>
              </div>
              <div className="flex items-center gap-3 group">
                <Globe className="w-5 h-5 text-red-600 group-hover:spin-slow" />
                <a href={`https://${SCHOOL_INFO.contact.website}`} target="_blank" rel="noopener noreferrer" className="group-hover:text-white transition-colors">
                  {SCHOOL_INFO.contact.website}
                </a>
              </div>
            </div>
          </div>

          {/* Bản đồ / Giờ làm việc */}
          <div>
            <h4 className="text-lg font-bold mb-6 text-white border-l-4 border-red-600 pl-3">Giờ làm việc</h4>
            <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
              <div className="space-y-3 text-sm">
                <div className="flex justify-between items-center pb-2 border-b border-gray-700">
                  <span className="text-gray-400">Thứ 2 - Thứ 6</span>
                  <span className="text-white font-medium">7:30 - 17:00</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Thứ 7</span>
                  <span className="text-white font-medium">7:30 - 11:30</span>
                </div>
                <div className="flex justify-between items-center pt-2 text-red-400 text-xs italic">
                  <span>Chủ nhật</span>
                  <span>Nghỉ</span>
                </div>
              </div>
            </div>

            <div className="mt-6 flex gap-2">
              <div className="h-1 flex-1 bg-red-600 rounded-full opacity-20"></div>
              <div className="h-1 flex-1 bg-yellow-500 rounded-full opacity-20"></div>
              <div className="h-1 flex-1 bg-blue-600 rounded-full opacity-20"></div>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-800 pt-8 mt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-500 text-sm text-center md:text-left">
              © {new Date().getFullYear()} {SCHOOL_INFO.name.vietnamese}. All rights reserved.
            </p>
            <div className="flex items-center gap-6">
              <Link href="/privacy" className="text-gray-500 hover:text-white text-sm transition-colors">Bảo mật</Link>
              <Link href="/terms" className="text-gray-500 hover:text-white text-sm transition-colors">Điều khoản</Link>
              <Link href="/admin" className="text-gray-600 hover:text-red-500 text-sm transition-colors flex items-center gap-1 bg-gray-800 px-3 py-1 rounded-full">
                <Settings className="w-3 h-3" />
                <span>Quản trị</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
