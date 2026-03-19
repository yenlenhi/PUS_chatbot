# Tối Ưu UI Thống Nhất Toàn Bộ Website

## Goal
Tạo design system thống nhất cho toàn bộ website PSU Chatbot. Hiện tại mỗi trang dùng color scheme khác nhau (gioi-thieu=đỏ, tuyen-sinh=xanh lá, dao-tao=xanh dương, nghien-cuu=tím, lien-he=cam, tin-tuc=hồng) gây cảm giác rời rạc. Cần thống nhất về **1 bảng màu chủ đạo** xuyên suốt, giữ nguyên 100% nội dung.

> ⚠️ **KHÔNG THAY ĐỔI** bất kỳ thông tin/nội dung nào trên website.

## Design Audit (Hiện trạng)

| Thành phần | Hiện tại | Vấn đề |
|---|---|---|
| **Header** | `bg-red-800` top bar + `bg-yellow-400` main | ✅ OK — đặc trưng trường |
| **Navigation** | `bg-green-700` | ❌ Lạc tông với Header đỏ-vàng |
| **Footer** | `bg-gray-900` + `border-red-700` | ✅ OK |
| **Giới thiệu Hero** | `from-red-700 to-red-900` | ⚠️ Mỗi trang 1 màu khác nhau |
| **Tuyển sinh Hero** | `from-emerald-600 to-cyan-800` | ⚠️ |
| **Đào tạo Hero** | `from-blue-600 to-indigo-800` | ⚠️ |
| **Nghiên cứu Hero** | `from-violet-500 to-purple-600` | ⚠️ |
| **Liên hệ Hero** | `from-orange-500 to-...` | ⚠️ |
| **Tin tức Hero** | `from-rose-500 to-...` | ⚠️ |
| **Section headers** | Mỗi chỗ 1 gradient khác nhau | ❌ Không nhất quán |
| **globals.css** | 707 dòng, animation trùng lặp | ❌ Cần dọn dẹp |

## Quyết Định Thiết Kế (Cần User Xác Nhận)

### Bảng màu thống nhất đề xuất

Dựa trên bản sắc Trường ĐHANND (Bộ Công An), đề xuất **bảng màu Đỏ - Vàng - Xanh đậm**:

| Token | Giá trị | Dùng cho |
|---|---|---|
| `--primary` | `#B91C1C` (red-700) | Hero backgrounds, CTA buttons, accents |
| `--primary-dark` | `#7F1D1D` (red-900) | Hero gradient end, dark sections |
| `--accent` | `#EAB308` (yellow-500) | Highlights, badges, active states |
| `--accent-light` | `#FEF3C7` (amber-100) | Badge backgrounds |
| `--secondary` | `#1E3A5F` (navy) | Navigation, sub-headers |
| `--surface` | `#F9FAFB` (gray-50) | Page backgrounds |
| `--surface-alt` | `#FEF2F2` (red-50) | Alt section backgrounds |

### Thay đổi cụ thể

**Navigation:** `bg-green-700` → `bg-[#1E3A5F]` (navy đậm) — hợp với Header đỏ-vàng hơn green

**Tất cả Hero Sections:** Thống nhất dùng gradient `from-red-800 via-red-900 to-[#1E3A5F]` — 1 style duy nhất, chỉ thay badge + title text

**Section Headers:** Thống nhất pattern:
- Badge: `bg-red-100 border-red-200 text-red-800` (bỏ hàng chục biến thể)
- Gradient text: `from-red-600 to-amber-600` (thay vì mỗi section 1 gradient)
- Divider: `from-red-600 to-amber-500`

**Cards & Buttons:** Icon containers thống nhất `from-red-600 to-red-700`, CTA buttons dùng `bg-red-700 hover:bg-red-800`

## Tasks

- [x] Task 1: Thêm CSS custom properties vào `globals.css` (design tokens) + dọn duplicate animations → ✅ Done
- [x] Task 2: Đổi `Navigation.tsx` từ green-700 → navy `bg-[#1E3A5F]` → ✅ Done
- [x] Task 3: Thống nhất Hero section `gioi-thieu/page.tsx` → gradient đỏ-navy → ✅ Done
- [x] Task 4: Thống nhất Hero + section headers `tuyen-sinh/page.tsx` → ✅ Done
- [x] Task 5: Thống nhất Hero + section headers `dao-tao/page.tsx` → ✅ Done
- [x] Task 6: Thống nhất Hero + section headers `nghien-cuu/page.tsx` → ✅ Done
- [x] Task 7: Thống nhất Hero + section headers `lien-he/page.tsx` → ✅ Done
- [x] Task 8: Thống nhất Hero + section headers `tin-tuc/page.tsx` → ✅ Done
- [x] Task 9: Build production `npm run build` → ✅ Passed (0 errors, 32 pages)
- [ ] Task 10: Visual test toàn bộ trang trên browser → Cần anh kiểm tra

## Verification Plan

### Automated
```bash
cd frontend && npm run build
```
Build phải thành công với 0 errors.

### Visual (Browser)
Mở từng trang và kiểm tra:
1. Home (`/`) — Banner, QuickStats, MissionVision, HistoryTimeline, NewsSection
2. `/gioi-thieu` — Hero đỏ-navy, sections thống nhất
3. `/tuyen-sinh` — Hero cùng tone, cards cùng style
4. `/dao-tao` — Hero cùng tone
5. `/nghien-cuu` — Hero cùng tone
6. `/lien-he` — Hero cùng tone
7. `/tin-tuc` — Hero cùng tone
8. Navigation — Navy color trên tất cả trang
9. Mobile responsive — Menu, hero, cards hiển thị tốt

### Manual (User)
Sau khi deploy, anh kiểm tra xem tone màu đã đồng nhất chưa, có bị "nhàm" không.

## Done When
- [ ] Tất cả 7 trang public có cùng bảng màu chủ đạo (đỏ-vàng-navy)
- [ ] Navigation đổi từ green → navy
- [ ] Section headers dùng chung 1 gradient pattern
- [ ] `npm run build` thành công
- [ ] Nội dung website KHÔNG thay đổi
