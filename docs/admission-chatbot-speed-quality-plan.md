# Plan: Admission Chatbot Speed and Quality Improvement

**Generated**: 2026-03-19
**Estimated Complexity**: High

## Overview
Mục tiêu là đưa chatbot về đúng vai trò "trợ lý tuyển sinh chính thức" của Trường Đại học An ninh Nhân dân, đồng thời giảm độ trễ và tăng độ tin cậy. Kế hoạch ưu tiên theo thứ tự: siết phạm vi nghiệp vụ, sửa các lệch contract/pipeline đang gây mất ngữ cảnh hoặc mất metadata, tối ưu latency trong retrieval/generation, rồi thiết lập bộ đo chất lượng và vận hành an toàn.

## Prerequisites
- Quyết định rõ scope nghiệp vụ: chatbot chỉ trả lời tuyển sinh hay vẫn hỗ trợ một số nội dung học vụ/quy chế.
- Có môi trường staging với PostgreSQL, Redis, Gemini key và bộ tài liệu tuyển sinh chuẩn.
- Có tập câu hỏi mẫu để benchmark: tối thiểu 100 câu tuyển sinh, 30 câu ngoài phạm vi, 20 câu follow-up đa lượt.
- Có quyền cập nhật cấu hình deploy backend/frontend.

## Sprint 1: Domain Guardrails and Product Policy
**Goal**: Chatbot chỉ trả lời đúng phạm vi tuyển sinh, từ chối rõ ràng với câu hỏi ngoài phạm vi.
**Demo/Validation**:
- Demo 20 câu hỏi tuyển sinh hợp lệ và 20 câu hỏi ngoài phạm vi.
- Xác nhận câu trả lời ngoài phạm vi luôn theo cùng một mẫu từ chối.

### Task 1.1: Define admission-only scope and refusal taxonomy
- **Location**: [docs\admission-chatbot-speed-quality-plan.md](c:\TruongVanKhai\Project\uni_bot\docs\admission-chatbot-speed-quality-plan.md), [docs\TECHNICAL_ARCHITECTURE.md](c:\TruongVanKhai\Project\uni_bot\docs\TECHNICAL_ARCHITECTURE.md)
- **Description**: Chốt danh sách intent được phép trả lời: điều kiện tuyển sinh, phương thức xét tuyển, chỉ tiêu, hồ sơ, mốc thời gian, đối tượng, vùng tuyển, học phí tuyển sinh nếu có trong tài liệu, FAQ tuyển sinh. Chốt intent bị từ chối: chính trị, thời sự, hỏi ngoài trường, hỏi kỹ thuật AI, hỏi học vụ nội bộ nếu không thuộc tuyển sinh.
- **Dependencies**: None
- **Acceptance Criteria**:
  - Có bảng scope in-scope/out-of-scope.
  - Có 1 mẫu từ chối chuẩn tiếng Việt và 1 mẫu tiếng Anh.
- **Validation**:
  - Review với stakeholder tuyển sinh.

### Task 1.2: Add intent gate before retrieval/LLM
- **Location**: [src\services\async_rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\async_rag_service.py), [src\services\rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\rag_service.py)
- **Description**: Thêm lớp phân loại intent đầu vào: `admission`, `non_admission`, `ambiguous`. Với `non_admission` trả lời từ chối ngay, không gọi retrieval/LLM chính. Với `ambiguous`, yêu cầu người dùng làm rõ.
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - Query ngoài phạm vi không đi qua pipeline retrieval đầy đủ.
  - Query mơ hồ trả về câu hỏi làm rõ ngắn gọn.
- **Validation**:
  - Unit tests cho classifier/rules.
  - Log xác nhận số request bị short-circuit.

### Task 1.3: Rewrite prompts to enforce policy and refusal style
- **Location**: [src\services\rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\rag_service.py)
- **Description**: Rút gọn `system_prompt`, bỏ phần scope quá rộng hiện tại, thêm nguyên tắc "nếu không thuộc tuyển sinh thì từ chối". Chuẩn hóa format trả lời: tóm tắt, chi tiết, nguồn.
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - Prompt chỉ còn domain tuyển sinh.
  - Không còn hướng dẫn khiến model trả lời quá rộng ngoài tuyển sinh.
- **Validation**:
  - So sánh prompt cũ/mới bằng review checklist.

### Task 1.4: Add out-of-scope analytics
- **Location**: [src\services\analytics_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\analytics_service.py), [src\api\routes.py](c:\TruongVanKhai\Project\uni_bot\src\api\routes.py)
- **Description**: Ghi nhận số câu hỏi ngoài phạm vi, câu hỏi mơ hồ, top chủ đề bị từ chối để biết người dùng đang hỏi gì ngoài mong đợi.
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - Có metric riêng cho `out_of_scope_count` và `ambiguous_count`.
- **Validation**:
  - Test log analytics với 3 loại intent.

## Sprint 2: Contract and Pipeline Cleanup
**Goal**: Một pipeline chat thống nhất, không mất lịch sử hội thoại, không mất metadata attachments/chart/source.
**Demo/Validation**:
- Demo 1 cuộc hội thoại text nhiều lượt và 1 cuộc hội thoại ảnh nhiều lượt.
- So sánh response JSON/SSE đồng nhất giữa các nhánh.

### Task 2.1: Remove contract drift between `/api/chat`, `/api/chat-stream`, and `/api/v1/chat`
- **Location**: [frontend\src\app\api\chat\route.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\api\chat\route.ts), [frontend\src\app\api\chat-stream\route.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\api\chat-stream\route.ts), [frontend\src\app\chat-bot\page.tsx](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\chat-bot\page.tsx), [src\api\routes.py](c:\TruongVanKhai\Project\uni_bot\src\api\routes.py)
- **Description**: Chọn 1 đường đi chuẩn cho text chat và 1 đường đi chuẩn cho vision chat. Loại bỏ hoặc deprecate pipeline cũ không dùng. Đồng bộ field request/response.
- **Dependencies**: None
- **Acceptance Criteria**:
  - Chỉ còn 1 contract chính cho text chat.
  - Không còn mapping thủ công thiếu field giữa frontend proxy và backend.
- **Validation**:
  - Integration tests cho text chat và vision chat.

### Task 2.2: Forward and persist `conversation_history` consistently
- **Location**: [frontend\src\app\api\chat\route.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\api\chat\route.ts), [src\models\schemas.py](c:\TruongVanKhai\Project\uni_bot\src\models\schemas.py), [src\services\async_rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\async_rag_service.py)
- **Description**: Bảo đảm mọi nhánh đều forward `conversation_history` và xử lý như nhau, nhất là nhánh có ảnh.
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - Follow-up question sau ảnh vẫn giữ ngữ cảnh.
- **Validation**:
  - Test case multi-turn với ảnh.

### Task 2.3: Unify response schema for `attachments`, `chart_data`, `images`, `source_references`
- **Location**: [src\models\schemas.py](c:\TruongVanKhai\Project\uni_bot\src\models\schemas.py), [src\api\routes.py](c:\TruongVanKhai\Project\uni_bot\src\api\routes.py), [frontend\src\types\index.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\types\index.ts)
- **Description**: Nâng `ChatResponse` để chứa đầy đủ metadata đang được service sinh ra. Không để API trả thiếu so với frontend cần hiển thị.
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - `attachments`, `source_references`, `chart_data`, `images` được trả nhất quán.
- **Validation**:
  - API contract tests.
  - Frontend smoke test render source/attachment.

### Task 2.4: Remove fake frontend fallback answers
- **Location**: [frontend\src\app\api\chat\route.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\api\chat\route.ts)
- **Description**: Bỏ fallback trả lời giả với confidence cao. Thay bằng lỗi chuẩn, có mã lỗi và thông điệp thân thiện.
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - Khi backend lỗi, frontend không tự bịa câu trả lời.
- **Validation**:
  - Simulate backend 500.

## Sprint 3: Latency Optimization
**Goal**: Cải thiện time-to-first-token và total response time rõ rệt cho câu hỏi text chuẩn tuyển sinh.
**Demo/Validation**:
- Benchmark trước/sau trên cùng 50 câu hỏi.
- Báo cáo P50/P95 cho `first_token_ms` và `total_response_ms`.

### Task 3.1: Baseline performance instrumentation
- **Location**: [src\api\routes.py](c:\TruongVanKhai\Project\uni_bot\src\api\routes.py), [src\services\analytics_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\analytics_service.py), [frontend\src\app\chat-bot\page.tsx](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\chat-bot\page.tsx)
- **Description**: Đo riêng các pha: normalize, rewrite, retrieval, rerank, prompt build, first token, full answer.
- **Dependencies**: None
- **Acceptance Criteria**:
  - Có log/tables đo latency theo từng stage.
- **Validation**:
  - Benchmark script chạy ra báo cáo CSV.

### Task 3.2: Reduce unnecessary preprocessing on clear admission queries
- **Location**: [src\services\async_rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\async_rag_service.py)
- **Description**: Giữ router thông minh hiện có nhưng siết rule hơn nữa: chỉ normalize khi cần, chỉ rewrite với follow-up thật, chỉ load memory khi có back-reference thật.
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - Query đơn giản 1 lượt không gọi 3 bước phụ không cần thiết.
- **Validation**:
  - Profiling log trước/sau.

### Task 3.3: Tune retrieval candidate sizes and reranking thresholds
- **Location**: [config\settings.py](c:\TruongVanKhai\Project\uni_bot\config\settings.py), [src\services\rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\rag_service.py), [src\services\hybrid_retrieval_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\hybrid_retrieval_service.py)
- **Description**: Benchmark các cấu hình `TOP_K_RESULTS`, `DENSE_WEIGHT`, dense/sparse thresholds, số candidates rerank, và chiến lược skip rerank.
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - Giảm P95 response time mà không giảm accuracy target.
- **Validation**:
  - Offline evaluation trên bộ câu hỏi chuẩn.

### Task 3.4: Rework model/process footprint for deployment
- **Location**: [main.py](c:\TruongVanKhai\Project\uni_bot\main.py), [Dockerfile](c:\TruongVanKhai\Project\uni_bot\Dockerfile), deploy config tương ứng
- **Description**: Đánh giá lại `workers=24`, số process load model, và thread pools. Chuyển sang worker count dựa trên CPU/RAM thực tế và concurrency profile của app.
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - Ổn định RAM/CPU khi tải cao.
  - Không swap hoặc OOM do nhân bản model.
- **Validation**:
  - Load test staging.

### Task 3.5: Optimize frontend streaming UX without extra buffering
- **Location**: [frontend\src\app\chat-bot\page.tsx](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\chat-bot\page.tsx), [frontend\src\app\api\chat-stream\route.ts](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\api\chat-stream\route.ts), [frontend\next.config.ts](c:\TruongVanKhai\Project\uni_bot\frontend\next.config.ts)
- **Description**: Giảm layer proxy không cần thiết, giữ `X-Accel-Buffering: no`, tránh parse/buffer dư thừa ở frontend.
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - Time-to-first-token frontend không bị chậm do proxy thừa.
- **Validation**:
  - Browser timing traces.

## Sprint 4: Quality, Grounding, and Safety
**Goal**: Tăng độ chính xác thực tế, giảm hallucination, tăng chất lượng nguồn dẫn.
**Demo/Validation**:
- Chạy bộ eval tuyển sinh chuẩn và so sánh score trước/sau.
- Kiểm tra 30 câu hỏi không có trong tài liệu và 30 câu hỏi ngoài phạm vi.

### Task 4.1: Build admission QA evaluation set and score rubric
- **Location**: [tests](c:\TruongVanKhai\Project\uni_bot\tests), [docs](c:\TruongVanKhai\Project\uni_bot\docs)
- **Description**: Tạo bộ dữ liệu đánh giá gồm gold answer, allowed sources, expected refusal, expected clarify.
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - Có bộ eval tối thiểu 150 case.
- **Validation**:
  - Review với đội tuyển sinh.

### Task 4.2: Enforce evidence-based answer policy
- **Location**: [src\services\rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\rag_service.py), [config\settings.py](c:\TruongVanKhai\Project\uni_bot\config\settings.py)
- **Description**: Dùng `STRICT_MODE`, `CONFIDENCE_THRESHOLD`, và luật "không có nguồn đủ mạnh thì không trả lời chi tiết". Nếu tài liệu không đủ, bot phải nói rõ là chưa có căn cứ.
- **Dependencies**: Task 4.1
- **Acceptance Criteria**:
  - Low-confidence query không trả lời tự tin.
- **Validation**:
  - Eval tập no-answer/out-of-doc.

### Task 4.3: Improve source presentation and citation usefulness
- **Location**: [frontend\src\app\chat-bot\page.tsx](c:\TruongVanKhai\Project\uni_bot\frontend\src\app\chat-bot\page.tsx), [src\services\async_rag_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\async_rag_service.py)
- **Description**: Hiển thị nhiều mức relevance hơn thay vì hard-cut quá sớm ở `>= 0.8`; ưu tiên filename + page + heading + snippet hữu ích.
- **Dependencies**: Task 2.3
- **Acceptance Criteria**:
  - Người dùng thấy rõ vì sao câu trả lời được đưa ra.
- **Validation**:
  - UX review với 20 câu mẫu.

### Task 4.4: Rationalize Google Search grounding usage
- **Location**: [src\services\gemini_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\gemini_service.py), [src\services\async_gemini_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\async_gemini_service.py)
- **Description**: Chỉ bật grounding cho nhóm query thời sự thực sự cần thiết. Với chatbot tuyển sinh chính thức, ưu tiên tài liệu nhà trường; không để grounding kéo bot ra ngoài scope.
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - Query tuyển sinh chuẩn không phụ thuộc web search trừ khi là thông tin thời điểm cần xác minh.
- **Validation**:
  - Compare latency và answer drift với grounding on/off theo loại query.

## Sprint 5: Data and Knowledge Base Hygiene
**Goal**: Nguồn dữ liệu sạch, chunking tốt, retrieval ổn định.
**Demo/Validation**:
- Re-index một bộ tài liệu tuyển sinh chuẩn.
- So sánh retrieval top-k trước/sau trên tập eval.

### Task 5.1: Separate admission documents from broader university corpus
- **Location**: [data](c:\TruongVanKhai\Project\uni_bot\data), ingestion scripts và schema liên quan
- **Description**: Gắn category rõ cho tài liệu tuyển sinh; cho phép retrieval chỉ search trong corpus tuyển sinh khi chatbot ở chế độ admission-only.
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - Query tuyển sinh không bị lẫn các tài liệu học vụ/bảo đảm chất lượng không liên quan.
- **Validation**:
  - Retrieval precision@k trên bộ eval.

### Task 5.2: Audit chunking and heading extraction on core admission PDFs
- **Location**: [src\services\pdf_processor.py](c:\TruongVanKhai\Project\uni_bot\src\services\pdf_processor.py), [src\utils\heading_chunker.py](c:\TruongVanKhai\Project\uni_bot\src\utils\heading_chunker.py)
- **Description**: Kiểm tra thủ công 10 PDF quan trọng, sửa pattern heading và chunk size nếu retrieval đang cắt sai mục/lệch tiêu đề.
- **Dependencies**: None
- **Acceptance Criteria**:
  - Các mục như điều kiện, hồ sơ, mốc thời gian, chỉ tiêu nằm trọn trong chunk hợp lý.
- **Validation**:
  - Manual QA với chunk viewer hoặc export chunk samples.

### Task 5.3: Fix ingestion API drift and add ingestion regression tests
- **Location**: [src\services\ingestion_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\ingestion_service.py), [src\services\pdf_processor.py](c:\TruongVanKhai\Project\uni_bot\src\services\pdf_processor.py), [src\services\embedding_service.py](c:\TruongVanKhai\Project\uni_bot\src\services\embedding_service.py), [tests](c:\TruongVanKhai\Project\uni_bot\tests)
- **Description**: Đồng bộ lại API ingest để dùng đúng method hiện có hoặc thêm method thiếu, sau đó thêm regression tests cho xử lý tài liệu.
- **Dependencies**: None
- **Acceptance Criteria**:
  - Ingestion chạy được end-to-end trên ít nhất 1 PDF mẫu.
- **Validation**:
  - Automated test + manual ingest.

## Testing Strategy
- Unit tests cho intent gating, refusal policy, source schema, attachment matching.
- Integration tests cho text chat, streaming chat, image chat, multi-turn history.
- Offline evaluation với bộ 150+ câu hỏi tuyển sinh chuẩn.
- Load test đo P50/P95 latency và memory footprint.
- Staging smoke test trước khi rollout production.

## Potential Risks & Gotchas
- Nếu siết scope quá mạnh, chatbot sẽ từ chối cả các câu hỏi học vụ mà nhà trường vẫn muốn hỗ trợ.
- Nếu bỏ fallback frontend nhưng không chuẩn hóa error UX, người dùng sẽ thấy chatbot “hay lỗi”.
- Nếu giảm grounding quá tay, một số câu hỏi thời sự có thể trả lời cũ.
- Nếu vẫn giữ nhiều pipeline song song, bug contract sẽ tái diễn.
- Nếu worker/process không tối ưu theo RAM thực, tối ưu code vẫn không cứu được latency khi production tải cao.

## Rollback Plan
- Giữ feature flags cho `ADMISSION_ONLY_MODE`, `STRICT_MODE`, `ENABLE_GOOGLE_SEARCH_GROUNDING`.
- Rollback prompt/policy theo config trước khi rollback code retrieval.
- Với schema response, rollout theo kiểu backward-compatible trước, chỉ xóa contract cũ sau khi frontend đã cut over.
- Với tuning retrieval, lưu benchmark trước/sau để có thể quay lại thông số cũ ngay.
