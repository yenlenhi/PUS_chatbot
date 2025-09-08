import React from 'react';
import { MapPin, Phone, Mail, Globe, Facebook, Youtube } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-800 text-white">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Thông tin trường */}
          <div>
            <h3 className="text-xl font-bold mb-4 text-yellow-400">
              TRƯỜNG ĐẠI HỌC AN NINH NHÂN DÂN
            </h3>
            <p className="text-gray-300 mb-4">
              Cơ sở đào tạo cán bộ an ninh chất lượng cao, đáp ứng yêu cầu bảo vệ an ninh quốc gia trong tình hình mới.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-blue-400 hover:text-blue-300">
                <Facebook className="w-6 h-6" />
              </a>
              <a href="#" className="text-red-400 hover:text-red-300">
                <Youtube className="w-6 h-6" />
              </a>
              <a href="#" className="text-blue-500 hover:text-blue-400">
                <Globe className="w-6 h-6" />
              </a>
            </div>
          </div>

          {/* Liên kết nhanh */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-yellow-400">Liên kết nhanh</h4>
            <ul className="space-y-2">
              <li>
                <a href="/gioi-thieu" className="text-gray-300 hover:text-white transition-colors duration-200">
                  Giới thiệu
                </a>
              </li>
              <li>
                <a href="/dao-tao" className="text-gray-300 hover:text-white transition-colors duration-200">
                  Đào tạo
                </a>
              </li>
              <li>
                <a href="/tuyen-sinh" className="text-gray-300 hover:text-white transition-colors duration-200">
                  Tuyển sinh
                </a>
              </li>
              <li>
                <a href="/nghien-cuu" className="text-gray-300 hover:text-white transition-colors duration-200">
                  Nghiên cứu khoa học
                </a>
              </li>
              <li>
                <a href="/tin-tuc" className="text-gray-300 hover:text-white transition-colors duration-200">
                  Tin tức
                </a>
              </li>
            </ul>
          </div>

          {/* Thông tin liên hệ */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-yellow-400">Thông tin liên hệ</h4>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-yellow-400 mt-1 flex-shrink-0" />
                <div>
                  <p className="text-gray-300">
                    125 Trần Phú, Văn Quán, Hà Đông, Hà Nội
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Phone className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                <p className="text-gray-300">024.3854.2222</p>
              </div>
              <div className="flex items-center space-x-3">
                <Mail className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                <p className="text-gray-300">info@psu.edu.vn</p>
              </div>
              <div className="flex items-center space-x-3">
                <Globe className="w-5 h-5 text-yellow-400 flex-shrink-0" />
                <p className="text-gray-300">www.psu.edu.vn</p>
              </div>
            </div>
          </div>

          {/* Bản đồ hoặc thông tin bổ sung */}
          <div>
            <h4 className="text-lg font-semibold mb-4 text-yellow-400">Vị trí</h4>
            <div className="w-full h-32 bg-gray-700 rounded-lg flex items-center justify-center">
              <div className="text-center text-gray-400">
                <MapPin className="w-8 h-8 mx-auto mb-2" />
                <p className="text-sm">Bản đồ vị trí trường</p>
              </div>
            </div>
            <div className="mt-4">
              <h5 className="font-semibold text-yellow-400 mb-2">Giờ làm việc</h5>
              <p className="text-gray-300 text-sm">
                Thứ 2 - Thứ 6: 7:30 - 17:00<br />
                Thứ 7: 7:30 - 11:30
              </p>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-700 mt-8 pt-6">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2025 Trường Đại học An ninh Nhân dân. Tất cả quyền được bảo lưu.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <a href="/privacy" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
                Chính sách bảo mật
              </a>
              <a href="/terms" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
                Điều khoản sử dụng
              </a>
              <a href="/sitemap" className="text-gray-400 hover:text-white text-sm transition-colors duration-200">
                Sơ đồ trang web
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
