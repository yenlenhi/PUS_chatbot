# CHƯƠNG 3: CƠ SỞ LÝ THUYẾT

## MỤC LỤC

1. [RAG - Retrieval-Augmented Generation](#31-rag---retrieval-augmented-generation)
2. [Vector Embeddings và Semantic Search](#32-vector-embeddings-và-semantic-search)
3. [BM25 và Sparse Retrieval](#33-bm25-và-sparse-retrieval)
4. [Hybrid Search](#34-hybrid-search)
5. [Cross-Encoder Reranking](#35-cross-encoder-reranking)
6. [Large Language Models](#36-large-language-models)
7. [Công nghệ Backend](#37-công-nghệ-backend)
8. [Công nghệ Frontend](#38-công-nghệ-frontend)
9. [Cơ sở dữ liệu](#39-cơ-sở-dữ-liệu)
10. [Containerization và Deployment](#310-containerization-và-deployment)

---

## 3.1. RAG - Retrieval-Augmented Generation

### 3.1.1. Khái niệm

**RAG (Retrieval-Augmented Generation)** là một kiến trúc AI tiên tiến kết hợp hai thành phần chính:

1. **Retrieval (Truy xuất)**: Tìm kiếm thông tin liên quan từ knowledge base
2. **Generation (Sinh văn bản)**: Sử dụng LLM để tạo câu trả lời dựa trên thông tin đã truy xuất

### 3.1.2. Tại sao cần RAG?

**Vấn đề của LLM thuần túy:**

```
❌ LLM standalone:
   - Kiến thức giới hạn (cutoff date)
   - Không biết thông tin cụ thể của tổ chức
   - Có thể "hallucinate" (bịa đặt thông tin)
   - Không cập nhật real-time
   
✅ RAG Solution:
   - Truy cập knowledge base cập nhật
   - Dữ liệu domain-specific
   - Giảm hallucination
   - Có nguồn trích dẫn rõ ràng
```

### 3.1.3. Kiến trúc RAG

```
┌─────────────────────────────────────────────────────────────┐
│                         RAG PIPELINE                         │
└─────────────────────────────────────────────────────────────┘

User Query: "Điều kiện xét học bổng là gì?"
    ↓
┌──────────────────────────────────┐
│  STEP 1: QUERY PROCESSING        │
│  - Normalize text                │
│  - Generate query embedding      │
│  - Expand query (optional)       │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  STEP 2: RETRIEVAL               │
│  - Vector search (semantic)      │
│  - BM25 search (keyword)         │
│  - Hybrid fusion                 │
│  → Top-K documents (e.g., K=20)  │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  STEP 3: RERANKING               │
│  - Cross-encoder scoring         │
│  - Re-sort by relevance          │
│  → Top-N documents (e.g., N=5)   │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  STEP 4: CONTEXT GENERATION      │
│  - Format retrieved docs         │
│  - Add metadata (source, page)   │
│  - Build prompt                  │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  STEP 5: GENERATION              │
│  - Send to LLM (Gemini)          │
│  - Generate answer               │
│  - Include citations             │
└──────────────────────────────────┘
    ↓
Response: "Theo quy chế đào tạo, sinh viên cần đạt 
điểm trung bình từ 3.5 trở lên... [Nguồn: QUY_CHE_DAO_TAO.pdf, trang 12]"
```

### 3.1.4. Lợi ích của RAG

| Tiêu chí | LLM thuần | RAG |
|----------|-----------|-----|
| **Độ chính xác** | Trung bình | Cao |
| **Tính cập nhật** | Cố định | Real-time |
| **Trích dẫn nguồn** | Không có | Có |
| **Hallucination** | Cao | Thấp |
| **Domain knowledge** | Chung chung | Chuyên biệt |
| **Chi phí** | Thấp | Trung bình |

### 3.1.5. Ứng dụng RAG trong hệ thống

Hệ thống chatbot áp dụng RAG để:

- ✅ Trả lời câu hỏi về quy chế, quy định của trường
- ✅ Cung cấp thông tin tuyển sinh, học bổng
- ✅ Hướng dẫn thủ tục hành chính
- ✅ Trích dẫn chính xác từ tài liệu gốc
- ✅ Cập nhật thông tin khi có tài liệu mới

### 3.1.6. Công thức đánh giá RAG

**Precision (Độ chính xác):**
```
Precision = (Số documents liên quan được truy xuất) / (Tổng số documents được truy xuất)
```

**Recall (Độ phủ):**
```
Recall = (Số documents liên quan được truy xuất) / (Tổng số documents liên quan)
```

**F1-Score:**
```
F1 = 2 × (Precision × Recall) / (Precision + Recall)
```

**Mean Reciprocal Rank (MRR):**
```
MRR = (1/n) × Σ(1/rank_i)
```
Trong đó `rank_i` là vị trí của document liên quan đầu tiên trong kết quả truy xuất.

---

## 3.2. Vector Embeddings và Semantic Search

### 3.2.1. Khái niệm Vector Embeddings

**Embedding** là quá trình chuyển đổi text thành vector số trong không gian nhiều chiều, nơi:
- Văn bản có nghĩa tương tự → Vectors gần nhau
- Văn bản khác nghĩa → Vectors xa nhau

**Ví dụ:**
```python
Text: "sinh viên xin nghỉ học"
↓ Embedding Model
Vector: [0.23, -0.45, 0.67, ..., 0.12]  # 384 dimensions

Text: "học sinh xin phép vắng mặt"
↓ Embedding Model  
Vector: [0.25, -0.43, 0.65, ..., 0.15]  # Gần với vector trên!

Text: "thời tiết hôm nay"
↓ Embedding Model
Vector: [-0.78, 0.32, -0.12, ..., 0.89]  # Xa với 2 vectors trên
```

### 3.2.2. Mô hình Embedding: Vietnamese SBERT

Hệ thống sử dụng **keepitreal/vietnamese-sbert**:

```python
Model: keepitreal/vietnamese-sbert
Base: sentence-transformers
Dimension: 384
Language: Vietnamese
Training: Contrastive learning on Vietnamese corpus
```

**Ưu điểm:**
- ✅ Được huấn luyện trên corpus tiếng Việt
- ✅ Hiểu ngữ nghĩa tiếng Việt tốt
- ✅ Kích thước vector nhỏ (384 dim) → nhanh
- ✅ Chất lượng tốt cho semantic search

**Kiến trúc SBERT:**
```
Input Text
    ↓
┌──────────────────┐
│  Tokenization    │
│  (WordPiece)     │
└──────────────────┘
    ↓
┌──────────────────┐
│  BERT Encoder    │
│  (12 layers)     │
└──────────────────┘
    ↓
┌──────────────────┐
│  Pooling Layer   │
│  (Mean pooling)  │
└──────────────────┘
    ↓
┌──────────────────┐
│  Dense Layer     │
│  (384 units)     │
└──────────────────┘
    ↓
384-dimensional Vector
```

### 3.2.3. Semantic Search

**Quy trình:**

```
1. Indexing Phase (Offline):
   Documents → Embeddings → Store in pgvector

2. Query Phase (Online):
   Query → Embedding → Vector Search → Top-K Results
```

**Cosine Similarity:**

Độ tương đồng giữa 2 vectors được tính bằng cosine của góc giữa chúng:

```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)

Trong đó:
- A · B: Tích vô hướng (dot product)
- ||A||: Độ dài (norm) của vector A
- ||B||: Độ dài (norm) của vector B

Giá trị: [-1, 1]
- 1: Hoàn toàn giống nhau
- 0: Trực giao (không liên quan)
- -1: Hoàn toàn ngược nhau
```

**Ví dụ tính toán:**
```python
import numpy as np

# Vector A: "sinh viên xin nghỉ"
A = np.array([0.5, 0.8, 0.2])

# Vector B: "học sinh xin phép"
B = np.array([0.6, 0.7, 0.3])

# Tích vô hướng
dot_product = np.dot(A, B)  # 0.5×0.6 + 0.8×0.7 + 0.2×0.3 = 0.92

# Norm
norm_A = np.linalg.norm(A)  # sqrt(0.5² + 0.8² + 0.2²) = 0.97
norm_B = np.linalg.norm(B)  # sqrt(0.6² + 0.7² + 0.3²) = 0.97

# Cosine similarity
similarity = dot_product / (norm_A * norm_B)  # 0.92 / 0.94 = 0.98
# → Rất giống nhau!
```

### 3.2.4. Vector Search với pgvector

**pgvector** là PostgreSQL extension cho vector similarity search:

```sql
-- Create vector column
ALTER TABLE embeddings 
ADD COLUMN embedding vector(384);

-- Create IVFFlat index for fast search
CREATE INDEX embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Search query
SELECT chunk_id, content, 
       1 - (embedding <=> query_embedding) AS similarity
FROM embeddings
ORDER BY embedding <=> query_embedding
LIMIT 20;
```

**IVFFlat Index:**

```
IVFFlat = Inverted File with Flat compression

Principle:
1. Cluster vectors into N lists (e.g., 100 lists)
2. Each vector belongs to nearest centroid
3. At search time:
   - Find nearest centroids to query
   - Only search vectors in those lists
   - Much faster than brute force

Trade-off:
- Speed: 10-100x faster
- Accuracy: ~95% recall (might miss some results)
```

### 3.2.5. Advantages & Limitations

**Ưu điểm Semantic Search:**
- ✅ Hiểu ngữ nghĩa, không chỉ từ khóa
- ✅ Tìm được văn bản tương tự ngữ nghĩa
- ✅ Robust với typos, synonyms
- ✅ Hoạt động tốt với queries dài

**Hạn chế:**
- ❌ Yếu với exact keyword matches
- ❌ Kém với tên riêng, mã số
- ❌ Có thể bỏ sót kết quả quan trọng

→ **Giải pháp: Hybrid Search (kết hợp với BM25)**

---

## 3.3. BM25 và Sparse Retrieval

### 3.3.1. Khái niệm BM25

**BM25 (Best Matching 25)** là thuật toán ranking dựa trên keyword matching, được cải tiến từ TF-IDF.

**TF-IDF Problems:**
```
TF-IDF có vấn đề:
1. Term frequency không được normalize tốt
2. Không xử lý document length
3. Saturation: Từ xuất hiện nhiều lần bị đánh giá quá cao
```

**BM25 Improvements:**
```
BM25 cải thiện:
1. Term frequency saturation
2. Document length normalization
3. Tunable parameters (k1, b)
```

### 3.3.2. Công thức BM25

**BM25 Score:**

```
score(D, Q) = Σ IDF(qi) × [f(qi, D) × (k1 + 1)] / [f(qi, D) + k1 × (1 - b + b × |D| / avgdl)]

Trong đó:
- D: Document
- Q: Query = {q1, q2, ..., qn}
- f(qi, D): Tần số từ qi trong document D
- |D|: Độ dài document D (số từ)
- avgdl: Độ dài trung bình của documents
- k1: Parameter điều chỉnh term frequency saturation (default: 1.5)
- b: Parameter điều chỉnh document length normalization (default: 0.75)

IDF(qi) = log[(N - n(qi) + 0.5) / (n(qi) + 0.5) + 1]

Trong đó:
- N: Tổng số documents
- n(qi): Số documents chứa từ qi
```

**Ý nghĩa các parameters:**

- **k1**: Kiểm soát saturation của term frequency
  - k1 = 0: Binary (chỉ quan tâm có/không)
  - k1 càng lớn: Term frequency càng quan trọng
  - Thường dùng: 1.2 - 2.0

- **b**: Kiểm soát ảnh hưởng của document length
  - b = 0: Không normalize length
  - b = 1: Full normalization
  - Thường dùng: 0.75

### 3.3.3. Ví dụ tính BM25

**Corpus:**
```
D1: "sinh viên cần nộp đơn xin nghỉ học"
D2: "sinh viên đạt điểm cao được học bổng"
D3: "quy định về học bổng cho sinh viên"
```

**Query:** "học bổng sinh viên"

**Bước 1: Tính IDF**
```
N = 3 (tổng số documents)

"học": xuất hiện trong D2, D3 → n = 2
IDF("học") = log[(3 - 2 + 0.5) / (2 + 0.5) + 1] = log[1.6] = 0.47

"bổng": xuất hiện trong D2, D3 → n = 2
IDF("bổng") = log[1.6] = 0.47

"sinh": xuất hiện trong D1, D2, D3 → n = 3
IDF("sinh") = log[(3 - 3 + 0.5) / (3 + 0.5) + 1] = log[1.14] = 0.13

"viên": xuất hiện trong D1, D2, D3 → n = 3
IDF("viên") = log[1.14] = 0.13
```

**Bước 2: Tính score cho D2**
```
D2: "sinh viên đạt điểm cao được học bổng"
|D2| = 8 từ
avgdl = (8 + 8 + 7) / 3 = 7.67
k1 = 1.5, b = 0.75

Term "học":
- f("học", D2) = 1
- Numerator = 1 × (1.5 + 1) = 2.5
- Denominator = 1 + 1.5 × (1 - 0.75 + 0.75 × 8/7.67) = 2.48
- Score = 0.47 × (2.5 / 2.48) = 0.474

Term "bổng":
- f("bổng", D2) = 1
- Score = 0.47 × (2.5 / 2.48) = 0.474

Term "sinh":
- f("sinh", D2) = 1
- Score = 0.13 × (2.5 / 2.48) = 0.131

Term "viên":
- f("viên", D2) = 1
- Score = 0.13 × (2.5 / 2.48) = 0.131

Total score(D2) = 0.474 + 0.474 + 0.131 + 0.131 = 1.21
```

**Kết quả:**
```
D3: score = 1.30 (cao nhất - chứa cả "học bổng sinh viên")
D2: score = 1.21 (trung bình - chứa "học bổng sinh viên")
D1: score = 0.26 (thấp - chỉ chứa "sinh viên")
```

### 3.3.4. Implementation với rank-bm25

```python
from rank_bm25 import BM25Okapi

# Corpus
documents = [
    "sinh viên cần nộp đơn xin nghỉ học",
    "sinh viên đạt điểm cao được học bổng",
    "quy định về học bổng cho sinh viên"
]

# Tokenize
tokenized_corpus = [doc.split() for doc in documents]

# Build BM25 index
bm25 = BM25Okapi(tokenized_corpus)

# Query
query = "học bổng sinh viên"
tokenized_query = query.split()

# Get scores
scores = bm25.get_scores(tokenized_query)
# [0.26, 1.21, 1.30]

# Get top-k
top_docs = bm25.get_top_n(tokenized_query, documents, n=2)
# ["quy định về học bổng cho sinh viên", 
#  "sinh viên đạt điểm cao được học bổng"]
```

### 3.3.5. Ưu điểm và Hạn chế

**Ưu điểm BM25:**
- ✅ Rất tốt với exact keyword matches
- ✅ Nhanh, không cần GPU
- ✅ Hoạt động tốt với tên riêng, mã số
- ✅ Không cần training
- ✅ Explainable (có thể giải thích kết quả)

**Hạn chế BM25:**
- ❌ Không hiểu ngữ nghĩa
- ❌ Không xử lý synonyms
- ❌ Yếu với typos
- ❌ Yêu cầu exact word match

---

## 3.4. Hybrid Search

### 3.4.1. Tại sao cần Hybrid Search?

**Vấn đề:**
```
Vector Search tốt:        "điều kiện nhận học bổng"
                      vs  "yêu cầu để được cấp học bổng"
                      → Semantic match ✅

BM25 tốt:                 "mã sinh viên SV2024001"
                      vs  "SV2024001"
                      → Exact match ✅
```

**Kết hợp cả hai → Hybrid Search tối ưu!**

### 3.4.2. Reciprocal Rank Fusion (RRF)

**Công thức RRF:**

```
RRF_score(d) = Σ [1 / (k + rank_i(d))]

Trong đó:
- d: Document
- rank_i(d): Vị trí của document d trong ranked list i
- k: Constant (thường = 60)
- Σ: Sum qua tất cả ranked lists (vector + BM25)
```

**Ví dụ:**

```
Query: "học bổng sinh viên giỏi"

Vector Search Results:
1. Doc A (score: 0.95)
2. Doc B (score: 0.88)
3. Doc C (score: 0.82)
4. Doc D (score: 0.75)

BM25 Results:
1. Doc B (score: 8.5)
2. Doc A (score: 7.2)
3. Doc E (score: 6.8)
4. Doc C (score: 5.9)

RRF Calculation (k=60):

Doc A:
- Vector rank: 1 → 1/(60+1) = 0.0164
- BM25 rank: 2 → 1/(60+2) = 0.0161
- RRF = 0.0164 + 0.0161 = 0.0325

Doc B:
- Vector rank: 2 → 1/(60+2) = 0.0161
- BM25 rank: 1 → 1/(60+1) = 0.0164
- RRF = 0.0161 + 0.0164 = 0.0325

Doc C:
- Vector rank: 3 → 1/(60+3) = 0.0159
- BM25 rank: 4 → 1/(60+4) = 0.0156
- RRF = 0.0159 + 0.0156 = 0.0315

Doc D:
- Vector rank: 4 → 1/(60+4) = 0.0156
- BM25 rank: ∞ (not in BM25 results) → 0
- RRF = 0.0156

Doc E:
- Vector rank: ∞ (not in vector results) → 0
- BM25 rank: 3 → 1/(60+3) = 0.0159
- RRF = 0.0159

Final Ranking:
1. Doc A (RRF: 0.0325)
2. Doc B (RRF: 0.0325)
3. Doc C (RRF: 0.0315)
4. Doc E (RRF: 0.0159)
5. Doc D (RRF: 0.0156)
```

### 3.4.3. Implementation

```python
def hybrid_search(query: str, top_k: int = 20):
    """
    Hybrid search combining vector and BM25
    """
    # 1. Vector search
    query_embedding = embedding_service.get_embedding(query)
    vector_results = vector_search(query_embedding, k=top_k)
    
    # 2. BM25 search
    bm25_results = bm25_search(query, k=top_k)
    
    # 3. RRF fusion
    rrf_scores = {}
    k = 60
    
    # Add vector results
    for rank, (chunk_id, score) in enumerate(vector_results, 1):
        rrf_scores[chunk_id] = 1 / (k + rank)
    
    # Add BM25 results
    for rank, (chunk_id, score) in enumerate(bm25_results, 1):
        if chunk_id in rrf_scores:
            rrf_scores[chunk_id] += 1 / (k + rank)
        else:
            rrf_scores[chunk_id] = 1 / (k + rank)
    
    # 4. Sort by RRF score
    sorted_results = sorted(
        rrf_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_results[:top_k]
```

### 3.4.4. Ưu điểm Hybrid Search

| Aspect | Vector Only | BM25 Only | Hybrid |
|--------|------------|-----------|--------|
| Semantic | ✅ | ❌ | ✅ |
| Exact match | ❌ | ✅ | ✅ |
| Synonyms | ✅ | ❌ | ✅ |
| Typos | ✅ | ❌ | ✅ |
| Names/Codes | ❌ | ✅ | ✅ |
| **Overall** | **Good** | **Good** | **Best** |

---

## 3.5. Cross-Encoder Reranking

### 3.5.1. Bi-Encoder vs Cross-Encoder

**Bi-Encoder (SBERT - dùng cho retrieval):**
```
Query → Encoder A → Vector A
                              ↓
                         Cosine Similarity
                              ↑
Document → Encoder B → Vector B

Pros:
✅ Fast: Encode once, search many times
✅ Scalable: Can index millions of docs

Cons:
❌ Less accurate: No interaction between query & doc
```

**Cross-Encoder (dùng cho reranking):**
```
[Query + Document] → Encoder → Relevance Score

Pros:
✅ More accurate: Full attention between query & doc
✅ Better for final ranking

Cons:
❌ Slow: Must encode each pair
❌ Not scalable for large corpus
```

### 3.5.2. Pipeline với Cross-Encoder

```
Query
  ↓
Retrieval (Bi-Encoder + BM25)
  ↓ Top-K=100
[Doc1, Doc2, ..., Doc100]
  ↓
Reranking (Cross-Encoder)
  ↓ Top-N=5
[Doc7, Doc23, Doc5, Doc89, Doc34]
  ↓
Send to LLM
```

### 3.5.3. Model: MS-MARCO Cross-Encoder

```python
Model: cross-encoder/ms-marco-MiniLM-L-6-v2
Base: MiniLM
Parameters: 22M
Input: Query + Document (max 512 tokens)
Output: Relevance score [0, 1]
```

**Usage:**
```python
from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Score query-document pairs
pairs = [
    ['học bổng sinh viên', 'Quy định về học bổng...'],
    ['học bổng sinh viên', 'Lịch thi học kỳ...'],
]

scores = model.predict(pairs)
# [0.87, 0.23]
```

### 3.5.4. Ví dụ Reranking

**Initial Retrieval (Top-5):**
```
1. Doc A: "Quy định về học bổng khuyến khích học tập" (score: 0.82)
2. Doc B: "Danh sách sinh viên đạt học bổng" (score: 0.79)
3. Doc C: "Điều kiện xét học bổng: GPA ≥ 3.5" (score: 0.77)
4. Doc D: "Học phí và các khoản thu" (score: 0.75)
5. Doc E: "Thủ tục xin học bổng" (score: 0.73)
```

**Query:** "Điều kiện để được nhận học bổng là gì?"

**After Cross-Encoder Reranking:**
```
1. Doc C: "Điều kiện xét học bổng: GPA ≥ 3.5" (score: 0.95) ⬆️
2. Doc E: "Thủ tục xin học bổng" (score: 0.88) ⬆️
3. Doc A: "Quy định về học bổng khuyến khích học tập" (score: 0.81) ⬇️
4. Doc B: "Danh sách sinh viên đạt học bổng" (score: 0.45) ⬇️
5. Doc D: "Học phí và các khoản thu" (score: 0.21) ⬇️
```

→ Doc C được đẩy lên top vì chính xác trả lời "điều kiện"!

### 3.5.5. Lợi ích Reranking

**Cải thiện Precision:**
```
Without Reranking:
Top-5 relevant: 3/5 = 60% precision

With Reranking:
Top-5 relevant: 5/5 = 100% precision
```

**Giảm chi phí LLM:**
```
Gửi 5 docs relevant → LLM generate tốt
Gửi 5 docs irrelevant → LLM confused, waste tokens
```

---

## 3.6. Large Language Models

### 3.6.1. Khái niệm LLM

**Large Language Model (LLM)** là mô hình ngôn ngữ được huấn luyện trên lượng dữ liệu khổng lồ, có khả năng:
- Hiểu và sinh văn bản tự nhiên
- Trả lời câu hỏi
- Tóm tắt, dịch thuật
- Reasoning và problem solving

### 3.6.2. Google Gemini 2.0 Flash

Hệ thống sử dụng **Gemini 2.0 Flash Experimental**:

```
Model: gemini-2.0-flash-exp
Release: December 2024
Context Window: 1,048,576 tokens (~1M tokens!)
Output: 8,192 tokens max
Modality: Text + Image (multimodal)
Speed: Fast (optimized for low latency)
Cost: Free tier available
```

**Ưu điểm:**
- ✅ Context window cực lớn (1M tokens)
- ✅ Tốc độ nhanh
- ✅ Hỗ trợ tiếng Việt tốt
- ✅ Multimodal (text + image) → OCR PDFs
- ✅ Free tier hào phóng

### 3.6.3. Prompt Engineering

**System Prompt:**
```python
SYSTEM_PROMPT = """
Bạn là trợ lý AI của Trường Đại học, chuyên trả lời câu hỏi về:
- Quy chế đào tạo
- Tuyển sinh
- Học bổng
- Thủ tục hành chính

HƯỚNG DẪN:
1. Trả lời dựa trên CONTEXT được cung cấp
2. Nếu không tìm thấy thông tin trong CONTEXT, hãy nói rõ
3. Trích dẫn nguồn (tên file, trang số)
4. Trả lời bằng tiếng Việt, rõ ràng, lịch sự
5. Format markdown khi cần (danh sách, bảng...)

CONTEXT:
{retrieved_documents}

QUESTION:
{user_question}

ANSWER:
"""
```

**Few-shot Examples:**
```python
FEW_SHOT_EXAMPLES = """
Example 1:
Q: Điều kiện xét học bổng là gì?
A: Theo quy chế đào tạo, sinh viên được xét học bổng khi đáp ứng:
1. Điểm trung bình học tập ≥ 3.5/4.0
2. Điểm rèn luyện ≥ 80/100
3. Không có học phần nào dưới điểm C

[Nguồn: QUY_CHE_DAO_TAO.pdf, trang 15]

Example 2:
Q: Thời tiết hôm nay thế nào?
A: Xin lỗi, tôi không có thông tin về thời tiết. Tôi chỉ có thể trả lời các câu hỏi liên quan đến quy định, tuyển sinh, học bổng của trường.
"""
```

### 3.6.4. Response Generation Flow

```python
def generate_response(query: str, context: List[Document]) -> str:
    """
    Generate response using Gemini
    """
    # 1. Format context
    context_text = "\n\n".join([
        f"[Document {i+1}]\n"
        f"Source: {doc.source_file}, Page: {doc.page_number}\n"
        f"Content: {doc.content}\n"
        for i, doc in enumerate(context)
    ])
    
    # 2. Build prompt
    prompt = SYSTEM_PROMPT.format(
        retrieved_documents=context_text,
        user_question=query
    )
    
    # 3. Call Gemini API
    response = genai.GenerativeModel('gemini-2.0-flash-exp').generate_content(
        prompt,
        generation_config={
            'temperature': 0.2,      # Low for factual answers
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2048,
        }
    )
    
    return response.text
```

### 3.6.5. Parameters Tuning

**Temperature:**
```
temperature = 0.0   → Deterministic, factual
temperature = 0.5   → Balanced
temperature = 1.0   → Creative, diverse

Hệ thống dùng: 0.2 (ưu tiên độ chính xác)
```

**Top-p (Nucleus Sampling):**
```
top_p = 0.1   → Very focused
top_p = 0.9   → More diverse
top_p = 1.0   → All tokens considered

Hệ thống dùng: 0.8
```

**Top-k:**
```
top_k = 1     → Always pick most likely token
top_k = 40    → Consider top 40 tokens
top_k = ∞     → Consider all tokens

Hệ thống dùng: 40
```

### 3.6.6. Gemini Vision API (OCR)

**Sử dụng cho PDF OCR:**
```python
def extract_text_with_gemini(pdf_page_image):
    """
    Extract text from PDF page using Gemini Vision
    """
    prompt = """
    Extract all text from this document page.
    Preserve formatting, headings, and structure.
    Output plain text with line breaks preserved.
    """
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    response = model.generate_content([prompt, pdf_page_image])
    
    return response.text
```

**Ưu điểm:**
- ✅ OCR quality cao nhất
- ✅ Hiểu layout phức tạp
- ✅ Xử lý được bảng, multi-column
- ✅ Hỗ trợ tiếng Việt tốt

---

## 3.7. Công nghệ Backend

### 3.7.1. FastAPI

**FastAPI** là modern web framework cho Python:

```python
from fastapi import FastAPI

app = FastAPI(
    title="University Chatbot API",
    version="1.0.0",
    docs_url="/api/docs"
)

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """Chat endpoint"""
    response = await chat_service.process_query(request.query)
    return ChatResponse(
        answer=response.answer,
        sources=response.sources,
        confidence=response.confidence
    )
```

**Ưu điểm:**
- ✅ Rất nhanh (dựa trên Starlette + Pydantic)
- ✅ Auto-generated OpenAPI docs
- ✅ Type hints và validation
- ✅ Async support
- ✅ Easy to test

### 3.7.2. SQLAlchemy + psycopg2

**SQLAlchemy**: ORM (Object-Relational Mapping)

```python
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(500))
    content = Column(Text)
    status = Column(String(50))
```

**psycopg2**: PostgreSQL adapter

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="uni_bot_db",
    user="postgres",
    password="password"
)
```

### 3.7.3. Pydantic

**Data validation và serialization:**

```python
from pydantic import BaseModel, Field, validator

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    conversation_id: Optional[str] = None
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class ChatResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    confidence: float
    processing_time: float
```

### 3.7.4. Redis (Caching)

**Caching layer:**

```python
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

# Cache embedding
def get_embedding_cached(text: str):
    cache_key = f"emb:{hash(text)}"
    
    # Try cache
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Generate
    embedding = model.encode(text)
    
    # Save to cache (7 days TTL)
    redis_client.setex(
        cache_key,
        7 * 24 * 3600,
        json.dumps(embedding.tolist())
    )
    
    return embedding
```

---

## 3.8. Công nghệ Frontend

### 3.8.1. Next.js 15

**Next.js** là React framework với:

```typescript
// App Router (Next.js 15)
// app/chat/page.tsx
export default function ChatPage() {
  return (
    <div>
      <ChatInterface />
    </div>
  )
}

// Server Components by default
// Client Components với 'use client'
'use client'
export function ChatInterface() {
  const [messages, setMessages] = useState([])
  // ... client logic
}
```

**Features:**
- ✅ App Router (new architecture)
- ✅ Server Components
- ✅ API Routes
- ✅ Image Optimization
- ✅ Built-in CSS support

### 3.8.2. React 19

**Latest React with:**
- ✅ Concurrent rendering
- ✅ Suspense for data fetching
- ✅ Server Components
- ✅ Actions

```tsx
'use client'
import { useState } from 'react'

export function ChatBox() {
  const [query, setQuery] = useState('')
  const [messages, setMessages] = useState([])
  
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    const response = await fetch('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify({ query })
    })
    
    const data = await response.json()
    setMessages([...messages, { role: 'assistant', content: data.answer }])
  }
  
  return (
    <form onSubmit={handleSubmit}>
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button type="submit">Send</button>
    </form>
  )
}
```

### 3.8.3. TypeScript

**Type safety:**

```typescript
// types/chat.ts
export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  sources?: Source[]
}

export interface Source {
  filename: string
  pageNumber: number
  content: string
}

export interface ChatResponse {
  answer: string
  sources: Source[]
  confidence: number
}
```

### 3.8.4. Tailwind CSS

**Utility-first CSS:**

```tsx
<div className="flex flex-col h-screen bg-gray-50">
  <div className="flex-1 overflow-y-auto p-4 space-y-4">
    {messages.map(msg => (
      <div 
        key={msg.id}
        className={`
          max-w-2xl rounded-lg p-4
          ${msg.role === 'user' 
            ? 'bg-blue-500 text-white ml-auto' 
            : 'bg-white text-gray-800 shadow-md'}
        `}
      >
        {msg.content}
      </div>
    ))}
  </div>
</div>
```

### 3.8.5. shadcn/ui

**Beautiful components:**

```tsx
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

<Card className="p-6">
  <Input 
    placeholder="Nhập câu hỏi..." 
    value={query}
    onChange={(e) => setQuery(e.target.value)}
  />
  <Button onClick={handleSubmit}>
    Gửi câu hỏi
  </Button>
</Card>
```

---

## 3.9. Cơ sở dữ liệu

### 3.9.1. PostgreSQL 16

**Features:**
- ✅ ACID compliance
- ✅ JSONB support
- ✅ Full-text search
- ✅ Extensions (pgvector)
- ✅ Replication

**Schema Example:**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_hash VARCHAR(64) UNIQUE,
    total_chunks INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_hash ON documents(file_hash);
```

### 3.9.2. pgvector Extension

**Vector similarity search:**

```sql
-- Install extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create table with vector column
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER REFERENCES chunks(id),
    embedding vector(384),  -- 384 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for fast search
CREATE INDEX embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Search query
SELECT chunk_id, 
       1 - (embedding <=> '[0.1,0.2,...]'::vector) AS similarity
FROM embeddings
ORDER BY embedding <=> '[0.1,0.2,...]'::vector
LIMIT 20;
```

**Operators:**
```sql
<=>   -- Cosine distance (1 - cosine similarity)
<->   -- L2 distance (Euclidean)
<#>   -- Inner product
```

### 3.9.3. Indexes

**B-tree Index:**
```sql
CREATE INDEX idx_chunks_doc_id ON chunks(document_id);
```

**GIN Index (Full-text search):**
```sql
CREATE INDEX idx_chunks_content_gin 
ON chunks 
USING gin(to_tsvector('english', content));
```

**IVFFlat Index (Vector):**
```sql
CREATE INDEX embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

---

## 3.10. Containerization và Deployment

### 3.10.1. Docker

**Containerization benefits:**
- ✅ Consistent environment
- ✅ Easy deployment
- ✅ Isolation
- ✅ Scalability

**Dockerfile Example:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3.10.2. Docker Compose

**Multi-container orchestration:**

```yaml
version: '3.8'

services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: uni_bot_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  backend:
    build: .
    depends_on:
      - postgres
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:password@postgres:5432/uni_bot_db
      REDIS_URL: redis://redis:6379
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    depends_on:
      - backend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

**Commands:**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down

# Rebuild
docker-compose up --build
```

### 3.10.3. Environment Variables

**.env file:**
```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/uni_bot_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=uni_bot_db

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Application
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://your-domain.com
```

---

## KẾT LUẬN CHƯƠNG 3

Chương này đã trình bày đầy đủ các cơ sở lý thuyết và công nghệ được sử dụng trong hệ thống:

### 🎯 Các kỹ thuật AI/ML:
- **RAG**: Kết hợp retrieval và generation cho câu trả lời chính xác
- **Vector Embeddings**: Semantic search với Vietnamese SBERT
- **BM25**: Sparse retrieval cho keyword matching
- **Hybrid Search**: Kết hợp vector + BM25 với RRF
- **Cross-Encoder**: Reranking để cải thiện precision
- **LLM**: Gemini 2.0 Flash cho generation và OCR

### 💻 Stack công nghệ:
- **Backend**: FastAPI, SQLAlchemy, Redis
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL 16 với pgvector
- **Deployment**: Docker, Docker Compose

### 📊 So sánh các phương pháp:

| Method | Accuracy | Speed | Use Case |
|--------|----------|-------|----------|
| Vector Search | High (semantic) | Fast | General queries |
| BM25 | High (exact) | Very Fast | Keyword queries |
| Hybrid | Very High | Fast | Best overall |
| + Reranking | Excellent | Medium | Final top-N |

Các lý thuyết này tạo nền tảng vững chắc cho việc hiểu và phát triển hệ thống chatbot trong các chương tiếp theo.

---

**Chương tiếp theo**: [Chương 4 - Kiến trúc Hệ thống](./TECHNICAL_ARCHITECTURE.md)

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team
