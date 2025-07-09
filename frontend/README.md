# Frontend Chatbot Tư Vấn Tuyển Sinh

Frontend Next.js cho hệ thống chatbot tư vấn tuyển sinh của Trường Đại học An ninh Nhân dân.

## Tính năng

### 🤖 Chat Interface
- Giao diện chat thân thiện và dễ sử dụng
- Hiển thị tin nhắn với avatar và timestamp
- Typing indicator khi bot đang trả lời
- Hiển thị độ tin cậy và nguồn tham khảo của câu trả lời

### 💬 Conversation Management
- Lưu trữ lịch sử cuộc hội thoại trong localStorage
- Sidebar hiển thị danh sách cuộc hội thoại
- Tạo cuộc hội thoại mới
- Xóa cuộc hội thoại không cần thiết
- Tự động tạo tiêu đề cho cuộc hội thoại

### 📱 Responsive Design
- Tối ưu cho cả desktop và mobile
- Sidebar có thể thu gọn trên mobile
- Auto-resize textarea
- Smooth animations và transitions

### 🎯 User Experience
- Câu hỏi mẫu cho người dùng mới
- Placeholder suggestions
- Error handling với thông báo rõ ràng
- Loading states và feedback

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
