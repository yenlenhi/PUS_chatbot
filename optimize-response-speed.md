# Optimize Chatbot Response Speed

## Goal
Giảm thời gian trả lời từ **40-58 giây** xuống **~15-20 giây** bằng cách loại bỏ các bước lãng phí và tối ưu pipeline.

## Timing Breakdown (từ log thực tế)

| Bước | Thời gian | Vấn đề |
|------|-----------|--------|
| Normalization | 2-3s | ❌ **Luôn fail** (MAX_TOKENS) → lãng phí hoàn toàn |
| Memory context | 15-25s | ❌ **#1 bottleneck** — tạo embedding + query DB |
| Query rewrite | 5s | ⚠️ Sync Gemini call, cần thiết nhưng chậm |
| Hybrid search | <1s | ✅ OK |
| Reranking | 11-12s | ❌ **#2 bottleneck** — CPU-heavy trên Railway |
| Gemini response | 11-14s | ⚠️ Inherent, streaming giúp UX |
| **TOTAL** | **40-58s** | |

## Tasks

- [x] Task 1: Tắt normalization (`ENABLE_GEMINI_NORMALIZATION=False` trong settings) → **Tiết kiệm 2-3s** → Verify: log không còn "Normalizing query"
- [x] Task 2: Giảm rerank chunks từ 20 → 10 tại `_rerank_chunks()` → **Tiết kiệm ~6s** → Verify: log "Reranked 10 chunks"
- [x] Task 3: Skip memory search cho conversation mới (turn ≤ 2) tại `async_rag_service.py` → **Tiết kiệm 15-25s cho câu đầu** → Verify: log không còn gap lớn trước hybrid search
- [x] Task 4: Chuyển query rewrite sang async (`generate_response_async`) thay vì sync → **Tiết kiệm ~2s** → Verify: log không có sync Gemini call for rewrite

## Estimated After Fix
| Bước | Before | After |
|------|--------|-------|
| Normalization | 2-3s | **0s** (disabled) |
| Memory context | 15-25s | **0-3s** (skip mới / lighter query) |
| Query rewrite | 5s | **3s** (async) |
| Reranking | 11-12s | **5-6s** (10 chunks thay vì 20) |
| Gemini response | 11-14s | 11-14s (inherent) |
| **TOTAL** | **40-58s** | **~15-23s** |

## Done When
- [x] Câu đầu tiên trả lời trong ~15s, follow-up ~20s
