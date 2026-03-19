/**
 * Display name mapping for known documents.
 * Keys are normalized: extension stripped, underscores/hyphens→spaces, lowercased.
 * Add new entries here whenever a new document is uploaded.
 */
const DOCUMENT_NAME_MAP: Record<string, string> = {
  // ── Điểm chuẩn ──────────────────────────────────────────────────────────
  "0e4e0 744 p3":                          "Điểm chuẩn T04 năm 2025",
  "diem chuan t04 2025":                   "Điểm chuẩn T04 năm 2025",

  // ── Thông báo tuyển sinh ─────────────────────────────────────────────────
  "thongbaotuyensinh2025":                 "Thông báo tuyển sinh 2025",
  "tuyen sinh 2025":                       "Thông báo tuyển sinh 2025",
  "thong bao chieu sinh tuyen sinh":       "Thông báo chiêu sinh tuyển sinh",
  "thong bao chieu sinh tuyen sinh ai hoc 2025":
                                           "Thông báo chiêu sinh tuyển sinh Đại học 2025",
  "7db18 t04 thong bao tuyen sinh thac si tien si 2025":
                                           "Thông báo tuyển sinh Thạc sĩ, Tiến sĩ 2025",
  // comma-variant produced by normalizeKey when filename contains ", "
  "7db18 t04 thong bao tuyen sinh thac si, tien si 2025":
                                           "Thông báo tuyển sinh Thạc sĩ, Tiến sĩ 2025",
  "thong bao xet tuyen bo sung chi tieu tuyen sinh dai hoc van bang 2 tuyen moi trong cand nam 2025":
                                           "Thông báo xét tuyển bổ sung VB2 trong CAND 2025",
  "thông báo xét tuyển bổ sung chỉ tiêu tuyển sinh đại học văn bằng 2 tuyển mới trong cand năm 2025.docx":
                                           "Thông báo xét tuyển bổ sung VB2 trong CAND 2025",
  "thong bao iem chuan xet trung tuyen phuong thuc 2 ky thi vb2ca nam 2025":
                                           "Thông báo điểm chuẩn xét trúng tuyển PT2 (Kỳ thi VB2CA) 2025",
  "thong bao iem trung tuyen ai hoc chinh quy tuyen moi nam 2025":
                                           "Thông báo điểm trúng tuyển ĐH Chính quy Tuyển mới 2025",

  // ── Kế hoạch tuyển sinh ──────────────────────────────────────────────────
  "ke hoach tuyen sinh dai hoc chinh quy tuyen moi 2025":
                                           "Kế hoạch tuyển sinh ĐH chính quy 2025",
  "ke hoach tuyen sinh vb2 tuyen moi 2025":
                                           "Kế hoạch tuyển sinh Văn bằng 2 tuyển mới 2025",

  // ── Hướng dẫn ────────────────────────────────────────────────────────────
  "d4096 huong dan tuyen sinh cand nam 2025":
                                           "Hướng dẫn tuyển sinh CAND năm 2025",

  // ── Tuyển sinh 2026 (file mới) ───────────────────────────────────────────
  "tuyen sinh 2026":                       "Tuyển sinh 2026",
  "tuyen_sinh_2026":                       "Tuyển sinh 2026",
  "thong bao tuyen sinh 2026":             "Thông báo tuyển sinh 2026",
  "ke hoach tuyen sinh 2026":              "Kế hoạch tuyển sinh 2026",

  // ── Công văn ─────────────────────────────────────────────────────────────
  "79e39 cong van so 269":                 "Công văn số 269",

  // ── Quyết định ───────────────────────────────────────────────────────────
  "qd 3470":                               "Quyết định số 3470",
  "qd 1231":                               "Quyết định số 1231",
  "qd 838 nhcht":                          "Quyết định số 838 (NHCHT)",

  // ── Quy chế / Thông tư ───────────────────────────────────────────────────
  "quy che dao tao dai hoc":               "Quy chế đào tạo đại học",
  "quy_che_dao_tao_dai_hoc":               "Quy chế đào tạo đại học",
  "du thao thong tu ve qlhv":              "Dự thảo Thông tư về quản lý học viên",
  "thong tu 50 ve tuyen sinh":             "Thông tư 50 về tuyển sinh",
  // variant: stored in DB as chapter-label "30.3. Thong Tu 50"
  "30.3. thong tu 50":                     "Thông tư 50 về tuyển sinh",

  // ── Luật ─────────────────────────────────────────────────────────────────
  "luat giao duc dai hoc":                 "Luật Giáo dục Đại học",

  // ── Đề án / Sổ tay / Giới thiệu ─────────────────────────────────────────
  "de an tuyen sinh 2023":                 "Đề án tuyển sinh 2023",
  "so tay bdcl 2025 t04":                  "Sổ tay Bảo đảm chất lượng 2025",
  "gioi thieu":                            "Giới thiệu trường",

  // ── Nghiên cứu / Lịch sử ────────────────────────────────────────────────
  // (tên file bị mất dấu tiếng Việt khi xử lý)
  "ang lanh ao tuyet oi truc tiep toan dien ve moi mat oi voi luc luong cand":
                                           "Đảng lãnh đạo tuyệt đối, toàn diện đối với lực lượng CAND",
  "nhung ong gop quan trong cua luc luong cong an nhan dan trong chien dich ien bien phu":
                                           "Những đóng góp của lực lượng CAND trong Chiến dịch Điện Biên Phủ",
};

/**
 * Normalise a raw filename to a map lookup key:
 *  1. Strip compound extensions (.docx.pdf, .doc.pdf, etc.)
 *  2. Strip remaining file extension
 *  3. Replace underscores and hyphens with spaces
 *  4. Collapse multiple spaces
 *  5. Lowercase + trim
 */
function normalizeKey(filename: string): string {
  return filename
    .replace(/\.(docx?|xlsx?|pptx?)\.pdf$/i, "")  // strip compound: .docx.pdf → ""
    .replace(/\.[^/.]+$/, "")                       // strip remaining extension
    .replace(/[_-]/g, " ")                          // _ or - → space
    .replace(/\s+/g, " ")                           // collapse spaces
    .toLowerCase()
    .trim();
}

/**
 * Smart fallback when no mapping entry exists.
 *  - Strips compound extensions (.docx.pdf)
 *  - Strips leading hash prefix like "0e4e0_", "7db18_"
 *  - Strips leading month/code prefix like "T04_", "T04-"
 *  - Replaces _/- with spaces
 *  - Title-cases each word
 */
function smartFallback(filename: string): string {
  return filename
    .replace(/\.(docx?|xlsx?|pptx?)\.pdf$/i, "")  // strip compound extensions
    .replace(/\.[^/.]+$/, "")                       // strip remaining extension
    .replace(/^[a-f0-9]{5}[_\s]/i, "")             // strip 5-char hash prefix: "0e4e0_"
    .replace(/^T\d{2}[_\s-]/i, "")                 // strip month code: "T04_", "T04-"
    .replace(/[_-]/g, " ")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/\b\w/g, (l) => l.toUpperCase());
}

/**
 * Returns a human-readable display name for a document filename.
 * Checks the mapping table first; falls back to smart parsing.
 */
export function getDocumentDisplayName(filename: string): string {
  const key = normalizeKey(filename);
  return DOCUMENT_NAME_MAP[key] ?? smartFallback(filename);
}
