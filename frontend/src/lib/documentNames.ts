/**
 * Display name mapping for known documents.
 * Keys are normalized: extension stripped, underscores→spaces, lowercased.
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
  "7db18 t04 thong bao tuyen sinh thac si tien si 2025":
                                           "Thông báo tuyển sinh Thạc sĩ, Tiến sĩ 2025",
  "7db18 t04-thong bao tuyen sinh thac si, tien si 2025":
                                           "Thông báo tuyển sinh Thạc sĩ, Tiến sĩ 2025",
  "thong bao xet tuyen bo sung chi tieu tuyen sinh dai hoc van bang 2 tuyen moi trong cand nam 2025":
                                           "Thông báo xét tuyển bổ sung VB2 trong CAND 2025",
  "thông báo xét tuyển bổ sung chỉ tiêu tuyển sinh đại học văn bằng 2 tuyển mới trong cand năm 2025.docx":
                                           "Thông báo xét tuyển bổ sung VB2 trong CAND 2025",

  // ── Kế hoạch tuyển sinh ──────────────────────────────────────────────────
  "ke hoach tuyen sinh dai hoc chinh quy tuyen moi 2025":
                                           "Kế hoạch tuyển sinh ĐH chính quy 2025",
  "ke hoach tuyen sinh vb2 tuyen moi 2025":
                                           "Kế hoạch tuyển sinh Văn bằng 2 tuyển mới 2025",

  // ── Hướng dẫn ────────────────────────────────────────────────────────────
  "d4096 huong dan tuyen sinh cand nam 2025":
                                           "Hướng dẫn tuyển sinh CAND năm 2025",

  // ── Công văn ─────────────────────────────────────────────────────────────
  "79e39 cong van so 269":                 "Công văn số 269",

  // ── Quyết định ───────────────────────────────────────────────────────────
  "qd 3470":                               "Quyết định số 3470",
  "qd 1231":                               "Quyết định số 1231",
  "qd 838 nhcht":                          "Quyết định số 838 (NHCHT)",

  // ── Quy chế / Thông tư ───────────────────────────────────────────────────
  "quy che dao tao dai hoc":               "Quy chế đào tạo đại học",
  "du thao thong tu ve qlhv":              "Dự thảo Thông tư về quản lý học viên",
  "thong tu 50 ve tuyen sinh":             "Thông tư 50 về tuyển sinh",

  // ── Đề án / Sổ tay / Giới thiệu ─────────────────────────────────────────
  "de an tuyen sinh 2023":                 "Đề án tuyển sinh 2023",
  "so tay bdcl 2025 t04":                  "Sổ tay Bảo đảm chất lượng 2025",
  "gioi thieu":                            "Giới thiệu trường",
};

/**
 * Normalise a raw filename to a map lookup key:
 *  1. Strip file extension
 *  2. Replace underscores and hyphens with spaces
 *  3. Collapse multiple spaces
 *  4. Lowercase + trim
 */
function normalizeKey(filename: string): string {
  return filename
    .replace(/\.[^/.]+$/, "")       // strip extension
    .replace(/[_-]/g, " ")          // _ or - → space
    .replace(/\s+/g, " ")           // collapse spaces
    .toLowerCase()
    .trim();
}

/**
 * Smart fallback when no mapping entry exists.
 *  - Strips leading hash prefix like "0e4e0_", "7db18_"
 *  - Strips leading month/code prefix like "T04_", "T04-"
 *  - Replaces _/- with spaces
 *  - Title-cases each word
 */
function smartFallback(filename: string): string {
  return filename
    .replace(/\.[^/.]+$/, "")               // strip extension
    .replace(/^[a-f0-9]{5}[_\s]/i, "")     // strip 5-char hash prefix: "0e4e0_"
    .replace(/^T\d{2}[_\s-]/i, "")         // strip month code: "T04_", "T04-"
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
