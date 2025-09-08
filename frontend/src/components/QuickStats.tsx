import React from 'react';
import { Users, GraduationCap, BookOpen, Award } from 'lucide-react';

const QuickStats = () => {
  const stats = [
    {
      icon: Users,
      number: "15,000+",
      label: "Sinh viên",
      color: "text-blue-600"
    },
    {
      icon: GraduationCap,
      number: "800+",
      label: "Giảng viên",
      color: "text-green-600"
    },
    {
      icon: BookOpen,
      number: "25+",
      label: "Ngành đào tạo",
      color: "text-purple-600"
    },
    {
      icon: Award,
      number: "98%",
      label: "Tỷ lệ việc làm",
      color: "text-red-600"
    }
  ];

  return (
    <div className="bg-white py-12">
      <div className="container mx-auto px-4">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Trường Đại học An ninh Nhân dân trong con số
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Những con số ấn tượng thể hiện sự phát triển và chất lượng đào tạo của nhà trường
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => {
            const IconComponent = stat.icon;
            return (
              <div key={index} className="text-center p-6 bg-gray-50 rounded-lg hover:shadow-lg transition-shadow duration-200">
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-white shadow-md mb-4 ${stat.color}`}>
                  <IconComponent className="w-8 h-8" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stat.number}
                </div>
                <div className="text-gray-600 font-medium">
                  {stat.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default QuickStats;
