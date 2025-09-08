# Website Trường Đại học An ninh Nhân dân

Website chính thức của Trường Đại học An ninh Nhân dân được xây dựng bằng Next.js 15 và Tailwind CSS.

## Tính năng chính

- **Responsive Design**: Tương thích với mọi thiết bị (desktop, tablet, mobile)
- **Header với Logo**: Logo trường và tên bằng tiếng Việt/Anh
- **Navigation Menu**: Menu điều hướng với các mục chính
- **Banner Slideshow**: Hiển thị tin tức và sự kiện quan trọng
- **News Section**: Khu vực tin tức với sidebar
- **Quick Stats**: Thống kê nhanh về trường
- **Footer**: Thông tin liên hệ và liên kết
- **Chatbot AI**: Nút chat floating với AI tư vấn tuyển sinh 24/7

### 🤖 Tính năng Chatbot
- Giao diện chat thân thiện, dễ sử dụng
- Nút floating luôn hiển thị ở góc phải màn hình
- Tích hợp AI để trả lời câu hỏi về tuyển sinh
- Câu hỏi gợi ý cho người dùng mới
- Responsive trên mọi thiết bị
- Kết nối với backend RAG system

## Công nghệ sử dụng

- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Fetch API** - HTTP requests
- **localStorage** - Lưu trữ conversation history

## Cài đặt và chạy

### Prerequisites
- Node.js 18+
- npm hoặc yarn

### Cài đặt dependencies
```bash
npm install
```

### Chạy development server
```bash
npm run dev
```

Frontend sẽ chạy tại: http://localhost:3000

### Build cho production
```bash
npm run build
npm start
```

## Cấu hình

### Environment Variables
Tạo file `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

Frontend tích hợp với backend API:

- `POST /api/v1/chat` - Gửi tin nhắn chat
- `GET /api/v1/health` - Kiểm tra trạng thái server
- `POST /api/v1/search` - Tìm kiếm tài liệu

## Cấu trúc thư mục

```
frontend/
├── src/
│   ├── app/                 # Next.js App Router
│   ├── components/         # React components
│   ├── hooks/              # Custom hooks
│   ├── services/           # API services
│   └── types/              # TypeScript types
├── public/                 # Static files
└── .env.local             # Environment variables
```
