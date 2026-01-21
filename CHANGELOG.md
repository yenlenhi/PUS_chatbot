# Changelog

All notable changes to the PUS Chatbot project will be documented in this file.

## [2026-01-21]

### Changed
- **Complete UI Redesign** for 6 main pages with premium design system:
  - `/gioi-thieu` - 🔴 Red theme: Timeline, Mission/Vision, Achievements
  - `/tuyen-sinh` - 🟢 Green theme: 3 Admission methods, 6 Programs, Requirements
  - `/nghien-cuu` - 🟣 Violet theme: AI Chatbot showcase, Tech stack
  - `/lien-he` - 🟠 Orange theme: Contact cards, Google Maps, Form
  - `/dao-tao` - 🔵 Blue theme: 3 Training levels, 6 Programs with codes
  - `/tin-tuc` - 🌸 Rose theme: Featured news, Grid layout

### Added
- Premium UI components: gradient backgrounds, glassmorphism, hover animations
- Accurate content from `WEBSITE_CONTENT.md` and `constants.ts`
- Thumbnail-only filter for news page (no placeholder images)

### Fixed
- `HistoryTimeline.tsx` - Color scheme changed from blue/purple → red/yellow
- `NewsSectionLive.tsx` - Added premium gradient header with badge + styled icons

### Chat Bot UI Premium Upgrade
- **12+ New Animations**: messageEntrance, typingBounce, goldRingPulse, shimmer, inputGlow, cardFloat, fabBounce, onlinePulse
- **Message Bubbles**: Slide-in animations (left for bot, right for user)
- **Bot Avatar**: Gold ring pulse when thinking, always-on status pulse
- **Input Bar**: Glassmorphism styling, focus glow effect, send button ripple
- **Suggested Questions**: Staggered entrance animation, hover float effect
- **Mobile**: Safe area padding utilities
- Login, Dashboard, Chat History, Documents, Attachments - no changes needed

---

## [2026-01-20]

### Added
- **Google Search Grounding** for real-time information
  - Automatically detects queries about current affairs (hiệu trưởng, tin tức, sự kiện)
  - Uses Gemini's Google Search tool to get up-to-date information
  - Supports Vietnamese with and without diacritics
  - Config: `ENABLE_GOOGLE_SEARCH_GROUNDING=true`

### Changed
- Updated `gemini_service.py` with `_needs_realtime_info()` helper function
- Updated `settings.py` with new configuration option

---

## [2026-01-18]

### Fixed
- Removed SourceFAB button on mobile to prevent overlap with chat input
- Fixed double submission in attachment upload using ref lock
- Fixed form hallucination by injecting attachments into stream context

### Changed
- Redesigned attachment mobile list with card layout

---

## [2026-01-17]

### Added
- Admin Dashboard Data Export (Excel format)
- Chat streaming implementation

### Fixed
- PgBouncer database connection error
- Image upload proxy configuration
