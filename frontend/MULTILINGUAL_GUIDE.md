# Multi-Language Support for Admin Panel

## ✨ Tính năng đa ngôn ngữ / Multi-Language Feature

Admin panel giờ đây hỗ trợ **2 ngôn ngữ**:
- 🇻🇳 **Tiếng Việt** (Vietnamese)
- 🇬🇧 **Tiếng Anh** (English)

## 🚀 Cách sử dụng / How to Use

### Chuyển đổi ngôn ngữ / Switch Language

1. Tìm nút **VI/EN** ở góc trên bên phải header (bên cạnh nút "Trang chủ")
2. Click vào nút để chuyển đổi giữa Tiếng Việt và Tiếng Anh
3. Ngôn ngữ được lưu tự động trong trình duyệt

### Các phần được dịch / Translated Sections

✅ **Navigation**
- Dashboard
- Lịch sử chat / Chat History
- Tài liệu / Documents
- Phản hồi người dùng / User Feedback

✅ **Dashboard Metrics**
- Tổng người dùng / Total Users
- Tổng tin nhắn / Total Messages
- Tổng tài liệu / Total Documents
- Token Usage
- Chi phí ước tính / Estimated Cost
- và nhiều hơn nữa...

✅ **Time Filters**
- 7 ngày qua / Last 7 Days
- Tháng này / Last Month
- Năm nay / Year to Date
- Tùy chỉnh / Custom

✅ **Common UI Elements**
- Buttons (Làm mới / Refresh, Đăng xuất / Logout)
- Loading states
- Error messages

## 🛠️ Implementation Details

### File Structure

```
frontend/src/
├── i18n/
│   ├── translations.ts       # All translations
│   ├── LanguageContext.tsx   # Context provider
│   └── LanguageSwitcher.tsx  # UI component
├── app/admin/
│   └── layout.tsx            # Wrapped with LanguageProvider
└── components/admin/
    ├── AdminLayout.tsx       # Uses translations
    └── AdminSidebar.tsx      # Uses translations
```

### Usage in Components

```tsx
import { useLanguage } from '@/i18n/LanguageContext';

function MyComponent() {
  const { t, language, setLanguage } = useLanguage();
  
  return (
    <div>
      <h1>{t('dashboard')}</h1>
      <p>{t('overview')}</p>
    </div>
  );
}
```

### Adding New Translations

1. Open `src/i18n/translations.ts`
2. Add new key to both `vi` and `en` objects:

```typescript
export const translations = {
  vi: {
    // ... existing translations
    newKey: 'Giá trị tiếng Việt',
  },
  en: {
    // ... existing translations
    newKey: 'English value',
  },
};
```

3. Use in component:
```tsx
{t('newKey')}
```

## 🎨 Language Switcher Button

- **Icon**: Languages icon from lucide-react
- **Display**: Shows current language (VI or EN)
- **Position**: Top right header, next to Home button
- **Style**: White background with hover effect
- **Tooltip**: Shows language switch hint

## 💾 Persistence

- Language preference is saved in **localStorage**
- Key: `adminLanguage`
- Automatically loads on page refresh
- Default: Vietnamese (vi)

## 🔧 Technical Stack

- **React Context API** for state management
- **localStorage** for persistence
- **TypeScript** for type safety
- **Lucide React** for icons

## 📝 Translation Coverage

### Fully Translated
- ✅ Navigation menu
- ✅ Header buttons
- ✅ Dashboard tabs
- ✅ Time range filters
- ✅ Common UI text
- ✅ Sidebar menu items

### Partially Translated (Data-dependent)
- ⚠️ Chart data labels (depends on API)
- ⚠️ Dynamic content from backend
- ⚠️ User-generated content

## 🚧 Future Improvements

- [ ] Add more languages (Chinese, Japanese, etc.)
- [ ] Translate chart tooltips
- [ ] Translate error messages
- [ ] Date/time formatting based on locale
- [ ] Number formatting (1,000 vs 1.000)
- [ ] Currency formatting based on locale

## 🐛 Known Issues

- Dashboard CSS @apply warnings (cosmetic, doesn't affect functionality)
- Some dynamic chart labels may remain in original language

## 📞 Support

If you need to add more translations or languages, contact the development team.
