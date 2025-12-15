# 📊 BIỂU ĐỒ HỆ THỐNG CHATBOT HỖ TRỢ TƯ VẤN TUYỂN SINH

> Tài liệu này chứa tất cả các biểu đồ minh họa cho bài NCKH

---

## 📑 MỤC LỤC BIỂU ĐỒ

1. [Kiến trúc RAG Overview](#1-kiến-trúc-rag-overview)
2. [Kiến trúc 3 tầng (3-Tier Architecture)](#2-kiến-trúc-3-tầng-3-tier-architecture)
3. [Component Diagram](#3-component-diagram)
4. [Luồng truy vấn người dùng (User Query Sequence)](#4-luồng-truy-vấn-người-dùng)
5. [Luồng Ingest tài liệu (Document Ingestion)](#5-luồng-ingest-tài-liệu)
6. [Quy trình xử lý tài liệu (Document Processing Pipeline)](#6-quy-trình-xử-lý-tài-liệu)
7. [RAG Retrieval Pipeline](#7-rag-retrieval-pipeline)
8. [Hybrid Search Fusion](#8-hybrid-search-fusion)
9. [Bi-Encoder vs Cross-Encoder](#9-bi-encoder-vs-cross-encoder)
10. [JWT Authentication Flow](#10-jwt-authentication-flow)
11. [Security Middleware Flow](#11-security-middleware-flow)
12. [Use Case Diagram](#12-use-case-diagram)
13. [User Journey - Chatbot](#13-user-journey---chatbot)
14. [Admin Workflow](#14-admin-workflow)

---

## 1. Kiến trúc RAG Overview

```mermaid
flowchart LR
    subgraph Input
        Q[🔍 User Query]
    end
    
    subgraph Retrieval["📚 Retrieval Phase"]
        E[Embedding Model]
        VS[(Vector Store)]
        BM[BM25 Index]
    end
    
    subgraph Augmentation["🔧 Augmentation Phase"]
        R[Reranker]
        C[Context Builder]
    end
    
    subgraph Generation["🤖 Generation Phase"]
        LLM[Large Language Model]
        A[📝 Answer]
    end
    
    Q --> E
    E --> VS
    E --> BM
    VS --> R
    BM --> R
    R --> C
    C --> LLM
    LLM --> A
    
    style Q fill:#e1f5fe
    style A fill:#c8e6c9
    style LLM fill:#fff3e0
    style VS fill:#f3e5f5
```

---

## 2. Kiến trúc 3 tầng (3-Tier Architecture)

```mermaid
flowchart TB
    subgraph Frontend["🖥️ TẦNG FRONTEND (Next.js 14)"]
        direction LR
        UI[Chat Interface]
        Admin[Admin Dashboard]
        Docs[Document Viewer]
    end
    
    subgraph Backend["⚙️ TẦNG BACKEND (FastAPI)"]
        direction LR
        API[REST API]
        Auth[Auth Service]
        Chat[Chat Service]
        RAG[RAG Service]
    end
    
    subgraph Database["🗄️ TẦNG DATABASE"]
        direction LR
        PG[(PostgreSQL)]
        PGV[(pgvector)]
        Redis[(Redis Cache)]
    end
    
    subgraph AI["🤖 TẦNG AI/ML"]
        direction LR
        EMB[Embedding Model<br/>intfloat/multilingual-e5-large]
        RR[Cross-Encoder<br/>Reranker]
        LLM[Gemini 2.0 Flash]
    end
    
    Frontend <--> Backend
    Backend <--> Database
    Backend <--> AI
    
    style Frontend fill:#e3f2fd
    style Backend fill:#fff8e1
    style Database fill:#f3e5f5
    style AI fill:#e8f5e9
```

---

## 3. Component Diagram

```mermaid
flowchart TB
    subgraph FE["Frontend Components"]
        ChatUI[ChatInterface.tsx]
        AdminUI[AdminDashboard.tsx]
        DocUI[DocumentViewer.tsx]
        FeedUI[FeedbackButtons.tsx]
    end
    
    subgraph BE["Backend Services"]
        direction TB
        subgraph API["API Layer"]
            Routes[routes.py]
            AuthRoutes[auth_routes.py]
        end
        
        subgraph Services["Service Layer"]
            RAGSvc[rag_service.py]
            DocSvc[document_service.py]
            ChatSvc[chat_service.py]
            FeedSvc[feedback_service.py]
        end
        
        subgraph Core["Core Components"]
            Embed[embedding_service.py]
            Chunk[chunking_service.py]
            Rerank[reranking_service.py]
        end
    end
    
    subgraph DB["Database Layer"]
        PG[(PostgreSQL)]
        Cache[(Redis)]
    end
    
    ChatUI --> Routes
    AdminUI --> Routes
    Routes --> Services
    Services --> Core
    Services --> DB
    Core --> DB
    
    style FE fill:#bbdefb
    style BE fill:#fff9c4
    style DB fill:#e1bee7
```

---

## 4. Luồng truy vấn người dùng

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚙️ FastAPI
    participant RAG as 🔍 RAGService
    participant VS as 📊 VectorStore
    participant BM as 📚 BM25
    participant RR as 🎯 Reranker
    participant LLM as 🤖 Gemini

    U->>FE: Nhập câu hỏi
    FE->>API: POST /api/chat
    API->>RAG: process_query()
    
    par Dense Retrieval
        RAG->>VS: vector_search(query)
        VS-->>RAG: top_k candidates
    and Sparse Retrieval
        RAG->>BM: bm25_search(query)
        BM-->>RAG: top_k candidates
    end
    
    RAG->>RAG: hybrid_fusion()
    RAG->>RR: rerank(candidates)
    RR-->>RAG: ranked_results
    
    RAG->>LLM: generate(query + context)
    LLM-->>RAG: response
    
    RAG-->>API: ChatResponse
    API-->>FE: JSON Response
    FE-->>U: Hiển thị câu trả lời
```

---

## 5. Luồng Ingest tài liệu

```mermaid
sequenceDiagram
    autonumber
    participant A as 👨‍💼 Admin
    participant FE as 🖥️ Dashboard
    participant API as ⚙️ FastAPI
    participant IS as 📥 IngestionService
    participant EX as 📄 Extractor
    participant CH as ✂️ Chunker
    participant EM as 🔢 Embedder
    participant DB as 🗄️ Database

    A->>FE: Upload PDF
    FE->>API: POST /api/documents/upload
    API->>IS: ingest_document()
    
    IS->>IS: validate_file()
    IS->>EX: extract_text(pdf)
    EX-->>IS: raw_text + metadata
    
    IS->>CH: chunk_document()
    CH-->>IS: chunks[]
    
    loop For each chunk
        IS->>EM: generate_embedding()
        EM-->>IS: vector[768]
    end
    
    IS->>DB: store_document()
    IS->>DB: store_chunks()
    IS->>DB: store_embeddings()
    
    DB-->>IS: success
    IS-->>API: IngestionResult
    API-->>FE: Upload Complete
    FE-->>A: ✅ Thông báo thành công
```

---

## 6. Quy trình xử lý tài liệu

```mermaid
flowchart TB
    subgraph Stage1["📥 Giai đoạn 1: Tiếp nhận"]
        A1[Upload PDF/DOCX]
        A2{Kiểm tra<br/>định dạng}
        A3[Lưu file tạm]
        A1 --> A2
        A2 -->|Valid| A3
        A2 -->|Invalid| A4[❌ Reject]
    end
    
    subgraph Stage2["📄 Giai đoạn 2: Trích xuất"]
        B1[PDF Parser<br/>pdfplumber]
        B2[Text Cleaning]
        B3[Metadata Extraction]
        A3 --> B1
        B1 --> B2
        B2 --> B3
    end
    
    subgraph Stage3["✂️ Giai đoạn 3: Chunking"]
        C1[Heading Detection]
        C2[Semantic Chunking]
        C3[Overlap Handling]
        B3 --> C1
        C1 --> C2
        C2 --> C3
    end
    
    subgraph Stage4["🔢 Giai đoạn 4: Embedding"]
        D1[Load E5 Model]
        D2[Generate Vectors]
        D3[Normalize Vectors]
        C3 --> D1
        D1 --> D2
        D2 --> D3
    end
    
    subgraph Stage5["💾 Giai đoạn 5: Lưu trữ"]
        E1[(PostgreSQL)]
        E2[(pgvector Index)]
        E3[BM25 Index Update]
        D3 --> E1
        D3 --> E2
        D3 --> E3
    end
    
    style Stage1 fill:#ffebee
    style Stage2 fill:#e3f2fd
    style Stage3 fill:#f3e5f5
    style Stage4 fill:#e8f5e9
    style Stage5 fill:#fff3e0
```

---

## 7. RAG Retrieval Pipeline

```mermaid
flowchart TB
    subgraph Input["🔍 Input"]
        Q[User Query]
    end
    
    subgraph Step1["Bước 1: Query Normalization"]
        N1[Lowercase]
        N2[Remove Accents]
        N3[Tokenization]
        Q --> N1 --> N2 --> N3
    end
    
    subgraph Step2["Bước 2: Dense Retrieval"]
        E[E5 Embedding]
        VS[(pgvector)]
        N3 --> E
        E -->|Cosine Similarity| VS
        VS --> DR[Dense Results<br/>top_k=50]
    end
    
    subgraph Step3["Bước 3: Sparse Retrieval"]
        BM[BM25 Algorithm]
        N3 --> BM
        BM --> SR[Sparse Results<br/>top_k=50]
    end
    
    subgraph Step4["Bước 4: Hybrid Fusion"]
        RRF[Reciprocal Rank Fusion]
        DR --> RRF
        SR --> RRF
        RRF --> HR[Hybrid Results<br/>top_k=30]
    end
    
    subgraph Step5["Bước 5: Reranking"]
        CE[Cross-Encoder<br/>ms-marco-MiniLM]
        HR --> CE
        CE --> RR[Reranked Results<br/>top_k=10]
    end
    
    subgraph Step6["Bước 6: Context Selection"]
        CS[Context Builder]
        RR --> CS
        CS --> CTX[Final Context<br/>≤4000 tokens]
    end
    
    subgraph Output["📤 Output"]
        CTX --> LLM[Send to LLM]
    end
    
    style Input fill:#e1f5fe
    style Step1 fill:#fff8e1
    style Step2 fill:#e8f5e9
    style Step3 fill:#fce4ec
    style Step4 fill:#f3e5f5
    style Step5 fill:#e0f2f1
    style Step6 fill:#fff3e0
    style Output fill:#c8e6c9
```

---

## 8. Hybrid Search Fusion

```mermaid
flowchart LR
    subgraph Dense["🔵 Dense Search (Semantic)"]
        direction TB
        D1[Query Embedding]
        D2[Vector Similarity]
        D3[Results: A, B, C, D, E]
        D1 --> D2 --> D3
    end
    
    subgraph Sparse["🟢 Sparse Search (BM25)"]
        direction TB
        S1[Term Matching]
        S2[TF-IDF Scoring]
        S3[Results: B, D, F, G, H]
        S1 --> S2 --> S3
    end
    
    subgraph Fusion["🟣 Reciprocal Rank Fusion"]
        direction TB
        F1["RRF Score = Σ 1/(k + rank)"]
        F2[Merge & Sort]
        F3[Final: B, D, A, C, F, E, G, H]
    end
    
    D3 --> F1
    S3 --> F1
    F1 --> F2 --> F3
    
    style Dense fill:#bbdefb
    style Sparse fill:#c8e6c9
    style Fusion fill:#e1bee7
```

### Công thức RRF:

$$RRF(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$

Trong đó:
- $d$ = document
- $R$ = tập các ranking lists
- $r(d)$ = rank của document d trong list r
- $k$ = constant (thường = 60)

---

## 9. Bi-Encoder vs Cross-Encoder

```mermaid
flowchart TB
    subgraph BiEncoder["🔵 Bi-Encoder (Fast)"]
        direction TB
        BE_Q[Query] --> BE_EQ[Encoder]
        BE_D[Document] --> BE_ED[Encoder]
        BE_EQ --> BE_VQ[Vector Q]
        BE_ED --> BE_VD[Vector D]
        BE_VQ --> BE_SIM[Cosine Similarity]
        BE_VD --> BE_SIM
        BE_SIM --> BE_S[Score: 0.85]
    end
    
    subgraph CrossEncoder["🟠 Cross-Encoder (Accurate)"]
        direction TB
        CE_Q[Query]
        CE_D[Document]
        CE_Q --> CE_CONCAT["[CLS] Query [SEP] Doc [SEP]"]
        CE_D --> CE_CONCAT
        CE_CONCAT --> CE_ENC[BERT Encoder]
        CE_ENC --> CE_CLS[CLS Token]
        CE_CLS --> CE_FF[Feed Forward]
        CE_FF --> CE_S[Score: 0.92]
    end
    
    style BiEncoder fill:#e3f2fd
    style CrossEncoder fill:#fff3e0
```

### So sánh:

| Tiêu chí | Bi-Encoder | Cross-Encoder |
|----------|------------|---------------|
| **Tốc độ** | ⚡ Rất nhanh | 🐢 Chậm |
| **Độ chính xác** | Tốt | Xuất sắc |
| **Use case** | Initial retrieval | Reranking |
| **Candidates** | 1000+ docs | 10-50 docs |

---

## 10. JWT Authentication Flow

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 User
    participant FE as 🖥️ Frontend
    participant API as ⚙️ FastAPI
    participant Auth as 🔐 AuthService
    participant DB as 🗄️ Database
    participant JWT as 🎫 JWT Handler

    rect rgb(255, 245, 238)
        Note over U,JWT: 🔑 LOGIN FLOW
        U->>FE: Nhập username/password
        FE->>API: POST /api/auth/login
        API->>Auth: authenticate()
        Auth->>DB: verify_credentials()
        DB-->>Auth: user_data
        Auth->>JWT: create_token(user_id, role)
        JWT-->>Auth: access_token + refresh_token
        Auth-->>API: AuthResponse
        API-->>FE: Set cookies
        FE-->>U: ✅ Đăng nhập thành công
    end

    rect rgb(232, 245, 233)
        Note over U,JWT: 🔒 PROTECTED REQUEST
        U->>FE: Truy cập Admin page
        FE->>API: GET /api/admin/stats<br/>Authorization: Bearer token
        API->>JWT: verify_token()
        JWT-->>API: decoded_payload
        API->>Auth: check_permission(role)
        Auth-->>API: ✅ Authorized
        API->>DB: get_stats()
        DB-->>API: stats_data
        API-->>FE: JSON Response
        FE-->>U: Hiển thị dashboard
    end

    rect rgb(255, 243, 224)
        Note over U,JWT: 🔄 TOKEN REFRESH
        FE->>API: POST /api/auth/refresh<br/>refresh_token
        API->>JWT: verify_refresh_token()
        JWT->>JWT: create_new_access_token()
        JWT-->>API: new_access_token
        API-->>FE: Updated token
    end
```

---

## 11. Security Middleware Flow

```mermaid
flowchart TB
    subgraph Request["📨 Incoming Request"]
        REQ[HTTP Request]
    end
    
    subgraph Middleware["🛡️ Security Middleware Stack"]
        M1[CORS Middleware]
        M2[Rate Limiter]
        M3[JWT Validator]
        M4[Role Checker]
        M5[Input Sanitizer]
        M6[Request Logger]
    end
    
    subgraph Checks["✅ Security Checks"]
        C1{Origin<br/>Allowed?}
        C2{Rate<br/>OK?}
        C3{Token<br/>Valid?}
        C4{Role<br/>Permitted?}
        C5{Input<br/>Safe?}
    end
    
    subgraph Response["📤 Response"]
        PASS[✅ Process Request]
        FAIL[❌ 401/403 Error]
    end
    
    REQ --> M1
    M1 --> C1
    C1 -->|Yes| M2
    C1 -->|No| FAIL
    
    M2 --> C2
    C2 -->|Yes| M3
    C2 -->|No| FAIL
    
    M3 --> C3
    C3 -->|Yes| M4
    C3 -->|No| FAIL
    
    M4 --> C4
    C4 -->|Yes| M5
    C4 -->|No| FAIL
    
    M5 --> C5
    C5 -->|Yes| M6
    C5 -->|No| FAIL
    
    M6 --> PASS
    
    style Request fill:#e3f2fd
    style Middleware fill:#fff8e1
    style Checks fill:#f3e5f5
    style PASS fill:#c8e6c9
    style FAIL fill:#ffcdd2
```

---

## 12. Use Case Diagram

```mermaid
flowchart TB
    subgraph Actors["👥 Actors"]
        User["👤 Thí sinh/<br/>Sinh viên/<br/>Phụ huynh"]
        Admin["👨‍💼 Admin"]
        System["🤖 System"]
    end
    
    subgraph UserCases["📱 User Use Cases"]
        UC1[Đặt câu hỏi<br/>tư vấn tuyển sinh]
        UC2[Xem lịch sử<br/>trò chuyện]
        UC3[Gửi phản hồi<br/>đánh giá]
        UC4[Tải tài liệu<br/>đính kèm]
        UC5[Tra cứu<br/>thông tin]
    end
    
    subgraph AdminCases["🔧 Admin Use Cases"]
        AC1[Đăng nhập<br/>hệ thống]
        AC2[Xem thống kê<br/>dashboard]
        AC3[Quản lý<br/>tài liệu]
        AC4[Upload<br/>PDF mới]
        AC5[Xem lịch sử<br/>chat users]
        AC6[Xem & phân tích<br/>feedback]
    end
    
    subgraph SystemCases["⚙️ System Use Cases"]
        SC1[Auto-ingest<br/>tài liệu]
        SC2[Generate<br/>embeddings]
        SC3[Backup<br/>database]
        SC4[Log &<br/>monitoring]
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    
    Admin --> AC1
    Admin --> AC2
    Admin --> AC3
    Admin --> AC4
    Admin --> AC5
    Admin --> AC6
    
    System --> SC1
    System --> SC2
    System --> SC3
    System --> SC4
    
    AC3 -.->|includes| AC4
    UC1 -.->|includes| UC4
    
    style User fill:#bbdefb
    style Admin fill:#c8e6c9
    style System fill:#fff9c4
```

---

## 13. User Journey - Chatbot

```mermaid
flowchart LR
    subgraph Entry["🚪 Entry"]
        E1[Truy cập website]
        E2[Click Chatbot]
    end
    
    subgraph Interact["💬 Interaction"]
        I1[Nhập câu hỏi]
        I2[Nhận câu trả lời]
        I3[Xem nguồn tham khảo]
        I4[Click xem tài liệu]
    end
    
    subgraph Feedback["📝 Feedback"]
        F1[👍 Like]
        F2[👎 Dislike]
        F3[Viết nhận xét]
    end
    
    subgraph Exit["🚶 Exit"]
        X1[Tiếp tục hỏi]
        X2[Đóng chatbot]
    end
    
    E1 --> E2
    E2 --> I1
    I1 --> I2
    I2 --> I3
    I3 --> I4
    I2 --> F1
    I2 --> F2
    F2 --> F3
    F1 --> X1
    F3 --> X1
    X1 --> I1
    I2 --> X2
    
    style Entry fill:#e1f5fe
    style Interact fill:#e8f5e9
    style Feedback fill:#fff3e0
    style Exit fill:#f3e5f5
```

---

## 14. Admin Workflow

```mermaid
flowchart TB
    subgraph Login["🔐 Authentication"]
        L1[Truy cập /admin]
        L2[Nhập credentials]
        L3{Xác thực?}
        L1 --> L2 --> L3
    end
    
    subgraph Dashboard["📊 Dashboard"]
        D1[Xem Overview]
        D2[Thống kê chat]
        D3[Thống kê feedback]
        D4[Charts & Graphs]
    end
    
    subgraph DocMgmt["📁 Document Management"]
        M1[Xem danh sách docs]
        M2[Upload PDF mới]
        M3[Xóa document]
        M4[Xem processing status]
    end
    
    subgraph ChatHistory["💬 Chat History"]
        C1[Xem conversations]
        C2[Filter by date]
        C3[Search messages]
        C4[Export data]
    end
    
    subgraph FeedbackMgmt["📝 Feedback Analysis"]
        F1[Xem all feedback]
        F2[Filter positive/negative]
        F3[Analyze patterns]
        F4[Export reports]
    end
    
    L3 -->|Yes| D1
    L3 -->|No| L1
    
    D1 --> D2
    D1 --> D3
    D1 --> D4
    
    D1 --> M1
    M1 --> M2
    M1 --> M3
    M1 --> M4
    
    D1 --> C1
    C1 --> C2
    C1 --> C3
    C1 --> C4
    
    D1 --> F1
    F1 --> F2
    F1 --> F3
    F1 --> F4
    
    style Login fill:#ffebee
    style Dashboard fill:#e3f2fd
    style DocMgmt fill:#e8f5e9
    style ChatHistory fill:#fff3e0
    style FeedbackMgmt fill:#f3e5f5
```

---

## 📌 Hướng dẫn sử dụng

### Xem biểu đồ Mermaid:

1. **VS Code**: Cài extension "Markdown Preview Mermaid Support"
2. **GitHub**: Tự động render khi push lên repo
3. **Online**: Copy code vào [Mermaid Live Editor](https://mermaid.live/)

### Export sang hình ảnh:

1. Truy cập https://mermaid.live/
2. Paste code Mermaid
3. Click "Export" → PNG/SVG

---

## 📚 Tài liệu tham khảo

- [Mermaid Documentation](https://mermaid.js.org/intro/)
- [PlantUML](https://plantuml.com/)
- [Draw.io](https://app.diagrams.net/)

---

*Tài liệu được tạo tự động - Cập nhật: December 2024*
