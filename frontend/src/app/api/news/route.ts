import { NextResponse } from 'next/server';

// Tin tức mẫu từ trang DHANND - do trang web có cơ chế bảo vệ chống scraping
// Trong thực tế, bạn có thể cập nhật dữ liệu này định kỳ hoặc dùng puppeteer/playwright
const NEWS_DATA = {
  mainNews: [
    {
      id: 1,
      title: "Hội nghị thông báo quyết định của Ban Thường vụ Đảng ủy Công an Trung ương về công tác cán bộ",
      excerpt: "Ngày 12/12/2024, Trường Đại học An ninh nhân dân tổ chức Hội nghị thông báo quyết định của Ban Thường vụ Đảng ủy Công an Trung ương, Bộ trưởng Bộ Công an về công tác cán bộ...",
      date: "12/12/2024",
      image: "/images/news/hoi-nghi-can-bo.jpg",
      category: "TIN TỨC",
      source: "dhannd.bocongan.gov.vn",
      url: "https://dhannd.bocongan.gov.vn/tin-tuc"
    },
    {
      id: 2,
      title: "Nền tảng pháp lý thúc đẩy khoa học, công nghệ, đổi mới sáng tạo và chuyển đổi số trong Công an nhân dân",
      excerpt: "Luật Khoa học và Công nghệ năm 2013 đã tạo nền tảng pháp lý quan trọng cho việc phát triển khoa học công nghệ trong lĩnh vực an ninh quốc gia, góp phần nâng cao năng lực công nghệ...",
      date: "10/12/2024",
      image: "/images/news/khoa-hoc-cong-nghe.jpg",
      category: "NGHIÊN CỨU",
      source: "dhannd.bocongan.gov.vn",
      url: "https://dhannd.bocongan.gov.vn/tin-tuc"
    },
    {
      id: 3,
      title: "Kết quả thi đánh giá năng lực tuyển sinh năm 2024",
      excerpt: "Trường Đại học An ninh Nhân dân công bố kết quả thi đánh giá năng lực tuyển sinh năm 2024. Thí sinh có thể tra cứu kết quả trên hệ thống...",
      date: "08/12/2024",
      image: "/images/news/tuyen-sinh.jpg",
      category: "TUYỂN SINH",
      source: "dhannd.bocongan.gov.vn",
      url: "https://dhannd.bocongan.gov.vn/tuyen-sinh"
    },
    {
      id: 4,
      title: "Lễ khai giảng năm học 2024-2025 và đón nhận sinh viên khóa mới",
      excerpt: "Sáng ngày 05/09/2024, Trường Đại học An ninh nhân dân long trọng tổ chức Lễ khai giảng năm học mới 2024-2025 và đón nhận sinh viên khóa mới nhập học...",
      date: "05/12/2024",
      image: "/images/news/khai-giang.jpg",
      category: "SỰ KIỆN",
      source: "dhannd.bocongan.gov.vn",
      url: "https://dhannd.bocongan.gov.vn/su-kien"
    }
  ],
  sidebarNews: [
    {
      id: 5,
      title: "Trường Đại học An ninh nhân dân tổ chức trao tặng căn hộ tình nghĩa cho cán bộ, chiến sĩ",
      date: "11/12/2024",
      category: "TIN TỨC",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 6,
      title: "Công đoàn Trường Đại học An ninh nhân dân tổ chức Hội thi nấu ăn chào mừng ngày 20/10",
      date: "10/12/2024",
      category: "HOẠT ĐỘNG",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 7,
      title: "Lễ trao bằng tốt nghiệp cho sinh viên khóa 2020-2024",
      date: "09/12/2024",
      category: "ĐÀO TẠO",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 8,
      title: "Hội nghị tổng kết công tác năm 2024 và triển khai nhiệm vụ năm 2025",
      date: "08/12/2024",
      category: "HỘI NGHỊ",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 9,
      title: "Chương trình học bổng khuyến khích học tập cho sinh viên xuất sắc năm học 2024-2025",
      date: "07/12/2024",
      category: "HỌC BỔNG",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 10,
      title: "Hội thảo khoa học quốc tế về an ninh mạng và bảo mật thông tin",
      date: "06/12/2024",
      category: "KHOA HỌC",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 11,
      title: "Thông báo tuyển sinh sau đại học năm 2025",
      date: "05/12/2024",
      category: "TUYỂN SINH",
      source: "dhannd.bocongan.gov.vn"
    },
    {
      id: 12,
      title: "Kế hoạch đào tạo, bồi dưỡng cán bộ năm 2025",
      date: "04/12/2024",
      category: "ĐÀO TẠO",
      source: "dhannd.bocongan.gov.vn"
    }
  ],
  lastUpdated: new Date().toISOString()
};

export async function GET() {
  try {
    // Trả về dữ liệu tin tức
    return NextResponse.json({
      success: true,
      data: NEWS_DATA,
      message: "Tin tức từ Trường Đại học An ninh Nhân dân"
    });
  } catch (error) {
    console.error('Error fetching news:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch news' },
      { status: 500 }
    );
  }
}
