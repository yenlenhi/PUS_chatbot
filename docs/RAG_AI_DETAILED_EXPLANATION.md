# GIẢI THÍCH KỸ THUẬT RAG VÀ AI CHO HỆ THỐNG CHATBOT

## 1. TỔNG QUAN VỀ RAG (RETRIEVAL-AUGMENTED GENERATION)

### 1.1. RAG là gì?

RAG là kỹ thuật kết hợp hai thành phần:
1. **Retrieval** (Truy xuất): Tìm kiếm thông tin liên quan từ knowledge base
2. **Generation** (Sinh văn bản): Sử dụng LLM để tạo câu trả lời dựa trên thông tin đã tìm được

### 1.2. Tại sao cần RAG?

**Vấn đề với LLM thuần túy:**
- ❌ Kiến thức bị giới hạn ở thời điểm training
- ❌ Không có kiến thức về tổ chức cụ thể
- ❌ Có thể "hallucinate" (đưa ra thông tin sai)
- ❌ Không trích dẫn được nguồn

**Giải pháp với RAG:**
- ✅ Truy cập real-time vào knowledge base
- ✅ Có thể cập nhật thông tin mà không cần retrain
- ✅ Grounded answers (dựa trên tài liệu thực tế)
- ✅ Trích dẫn nguồn rõ ràng
- ✅ Cost-effective (không cần fine-tuning)

### 1.3. So sánh các phương pháp

```
┌─────────────────────────────────────────────────────────────────┐
│                     LLM Thuần (GPT-4, etc.)                      │
├─────────────────────────────────────────────────────────────────┤
│ Ưu điểm:                                                         │
│ - Dễ implement                                                   │
│ - Tổng quát, hiểu nhiều domain                                  │
│                                                                  │
│ Nhược điểm:                                                      │
│ - Kiến thức cũ (cutoff date)                                    │
│ - Không biết về trường đại học cụ thể                           │
│ - Có thể hallucinate                                            │
│ - Không trích dẫn được                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       Fine-tuned LLM                             │
├─────────────────────────────────────────────────────────────────┤
│ Ưu điểm:                                                         │
│ - Kiến thức được "nằm trong" model                              │
│ - Response nhanh                                                │
│                                                                  │
│ Nhược điểm:                                                      │
│ - Rất tốn kém (cả tiền lẫn compute)                            │
│ - Cần retrain khi có thông tin mới                             │
│ - Vẫn có thể hallucinate                                        │
│ - Khó cập nhật                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    RAG (Hệ thống hiện tại)                       │
├─────────────────────────────────────────────────────────────────┤
│ Ưu điểm:                                                         │
│ - Grounded (dựa trên tài liệu thực)                            │
│ - Dễ cập nhật (chỉ cần add PDF mới)                           │
│ - Trích dẫn nguồn rõ ràng                                       │
│ - Cost-effective                                                │
│ - Transparent                                                   │
│                                                                  │
│ Nhược điểm:                                                      │
│ - Phụ thuộc vào chất lượng retrieval                           │
│ - Cần maintain vector database                                 │
│ - Response time cao hơn một chút                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. KIẾN TRÚC RAG PIPELINE CHI TIẾT

### 2.1. Phase 1: Indexing (Offline)

#### Bước 1: Document Loading
```python
# Load PDF file
pdf_file = "QUY_CHE_DAO_TAO.pdf"
pdf_reader = PyPDF2.PdfReader(pdf_file)

# Extract text from all pages
full_text = ""
for page in pdf_reader.pages:
    full_text += page.extract_text()
```

#### Bước 2: Text Chunking
```python
# Smart chunking với heading detection
chunks = []
current_chunk = ""
current_heading = None

for line in full_text.split('\n'):
    # Detect heading (ALL CAPS, hoặc format đặc biệt)
    if is_heading(line):
        # Save previous chunk
        if current_chunk:
            chunks.append({
                "heading": current_heading,
                "content": current_chunk,
                "size": len(current_chunk)
            })
        # Start new chunk
        current_heading = line
        current_chunk = line + "\n"
    else:
        current_chunk += line + "\n"
        
        # Split if too large (500 chars)
        if len(current_chunk) > 500:
            chunks.append({
                "heading": current_heading,
                "content": current_chunk,
                "size": len(current_chunk)
            })
            # Keep heading for next chunk (context)
            current_chunk = current_heading + "\n"
```

**Ví dụ chunking:**
```
Original PDF:
┌─────────────────────────────────────┐
│ CHƯƠNG 1: QUY ĐỊNH CHUNG            │
│                                     │
│ Điều 1. Phạm vi áp dụng            │
│ Quy chế này áp dụng cho...         │
│                                     │
│ Điều 2. Đối tượng áp dụng          │
│ Sinh viên đại học chính quy...     │
│                                     │
│ CHƯƠNG 2: QUY ĐỊNH VỀ NGHỈ HỌC    │
│                                     │
│ Điều 3. Nghỉ học có phép           │
│ Sinh viên nghỉ học có phép khi...  │
└─────────────────────────────────────┘

After Chunking:
┌─────────────────────────────────────┐
│ Chunk 1 (ID: 1)                     │
│ Heading: "CHƯƠNG 1: QUY ĐỊNH CHUNG" │
│ Content: "Điều 1. Phạm vi áp dụng  │
│          Quy chế này áp dụng cho..." │
├─────────────────────────────────────┤
│ Chunk 2 (ID: 2)                     │
│ Heading: "CHƯƠNG 1: QUY ĐỊNH CHUNG" │
│ Content: "Điều 2. Đối tượng áp dụng│
│          Sinh viên đại học..."      │
├─────────────────────────────────────┤
│ Chunk 3 (ID: 3)                     │
│ Heading: "CHƯƠNG 2: NGHỈ HỌC"      │
│ Content: "Điều 3. Nghỉ học có phép │
│          Sinh viên nghỉ học..."     │
└─────────────────────────────────────┘
```

#### Bước 3: Embedding Generation

**Sentence-BERT (Vietnamese):**
```python
from sentence_transformers import SentenceTransformer

# Load model
model = SentenceTransformer('keepitreal/vietnamese-sbert')

# Generate embedding cho mỗi chunk
for chunk in chunks:
    embedding = model.encode(chunk['content'])
    # embedding shape: (384,) - vector 384 chiều
    
    # Save to database
    save_embedding(chunk_id, embedding)
```

**Cách hoạt động của SBERT:**
```
Input Text: "Quy định về nghỉ học có phép"
    ↓
Tokenization: ["quy", "định", "về", "nghỉ", "học", "có", "phép"]
    ↓
BERT Encoding: [[0.1, -0.3, ...], [0.5, 0.2, ...], ...]
    ↓
Mean Pooling: [0.23, -0.15, 0.44, ..., 0.67]
    ↓
Normalization: [0.18, -0.12, 0.35, ..., 0.53]
    ↓
Output: 384-dimensional vector
```

**Tại sao dùng embedding?**
```
Semantic similarity:
Vector("nghỉ học")     ≈ Vector("xin nghỉ")
Vector("học bổng")     ≈ Vector("trợ cấp")
Vector("đăng ký")      ≈ Vector("đăng kí")

Không giống nhau nhưng ý nghĩa tương tự!
```

#### Bước 4: Vector Storage (pgvector)

```sql
-- Create table with vector column
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    chunk_id INTEGER,
    embedding vector(384)  -- 384-dimensional vector
);

-- Create vector index for fast similarity search
CREATE INDEX embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

**IVFFlat Index:**
```
Clustering vectors into 100 lists (centroids)
    ↓
List 1: [vectors similar to centroid 1]
List 2: [vectors similar to centroid 2]
...
List 100: [vectors similar to centroid 100]

Query time:
1. Find nearest centroids (fast)
2. Search only in those lists (fast)
Instead of searching all vectors (slow)
```

### 2.2. Phase 2: Retrieval (Online)

#### Bước 1: Query Preprocessing

**Gemini Question Normalization:**
```python
# Original user query
user_query = "cho tôi xin cái form đơn xin nghỉ học đi ạ"

# Normalize với Gemini
prompt = f"""
Chuẩn hóa câu hỏi sau thành dạng ngắn gọn, giữ từ khóa chính:
"{user_query}"

Chỉ trả về câu đã chuẩn hóa, không giải thích.
"""

normalized = gemini.generate(prompt)
# Output: "form đơn xin nghỉ học"
```

**Lợi ích normalization:**
```
Original:     "cho tôi xin cái form đơn xin nghỉ học đi ạ"
Normalized:   "form đơn xin nghỉ học"
                ↓ Better retrieval
                
Original:     "mình muốn hỏi về quy định nghỉ phép như thế nào"
Normalized:   "quy định nghỉ phép"
                ↓ More focused
```

#### Bước 2: Dense Retrieval (Vector Search)

```python
# Create query embedding
query_embedding = embedding_service.create_embedding(normalized_query)
# query_embedding shape: (384,)

# Search trong pgvector với cosine similarity
sql = """
SELECT 
    chunk_id,
    1 - (embedding <=> %s) as similarity
FROM embeddings
WHERE 1 - (embedding <=> %s) > 0.7  -- threshold
ORDER BY embedding <=> %s
LIMIT 20
"""

results = execute(sql, [query_embedding, query_embedding, query_embedding])
```

**Cosine Similarity:**
```
similarity = 1 - cosine_distance(vec1, vec2)
           = (vec1 · vec2) / (||vec1|| * ||vec2||)

Ví dụ:
Query: "nghỉ học"      → [0.2, 0.5, 0.3, ...]
Chunk: "xin nghỉ học"  → [0.25, 0.48, 0.32, ...]
Similarity = 0.95 (very similar!)

Query: "nghỉ học"      → [0.2, 0.5, 0.3, ...]
Chunk: "học bổng"      → [-0.1, 0.3, -0.5, ...]
Similarity = 0.35 (not very similar)
```

#### Bước 3: Sparse Retrieval (BM25)

**BM25 Algorithm:**
```python
from rank_bm25 import BM25Okapi

# Build BM25 index
corpus = [chunk['content'].lower().split() for chunk in all_chunks]
bm25 = BM25Okapi(corpus)

# Search
query_tokens = normalized_query.lower().split()
scores = bm25.get_scores(query_tokens)

# Get top results
top_indices = np.argsort(scores)[-20:][::-1]
```

**BM25 Score Formula:**
```
score(D, Q) = Σ IDF(qi) * (f(qi,D) * (k1 + 1)) / (f(qi,D) + k1 * (1 - b + b * |D|/avgdl))

Where:
- D: document (chunk)
- Q: query
- qi: query term i
- f(qi,D): frequency of qi in D
- |D|: length of D
- avgdl: average document length
- k1, b: tuning parameters (k1=1.5, b=0.75)
- IDF(qi): inverse document frequency
```

**Ví dụ BM25:**
```
Query: "form đơn nghỉ học"

Chunk A: "Form xin nghỉ học có phép quá 5 ngày..."
- Contains: "form" (1x), "nghỉ" (1x), "học" (1x)
- BM25 Score: 8.5

Chunk B: "Quy định về nghỉ học không phép..."
- Contains: "nghỉ" (1x), "học" (1x)
- BM25 Score: 4.2

Chunk C: "Đăng ký học phần học kỳ 1..."
- Contains: "học" (3x)
- BM25 Score: 2.1

Ranking: A > B > C
```

#### Bước 4: Hybrid Fusion (RRF)

**Reciprocal Rank Fusion:**
```python
def hybrid_score(dense_score, sparse_score, alpha=0.7):
    return alpha * dense_score + (1 - alpha) * sparse_score

# Dense results (từ vector search)
dense_results = [
    {"chunk_id": 5, "score": 0.92},
    {"chunk_id": 12, "score": 0.88},
    {"chunk_id": 3, "score": 0.85},
]

# Sparse results (từ BM25)
sparse_results = [
    {"chunk_id": 5, "score": 8.5},   # Normalize to 0-1
    {"chunk_id": 7, "score": 7.2},
    {"chunk_id": 12, "score": 6.8},
]

# Normalize sparse scores
max_sparse = max([r['score'] for r in sparse_results])
for r in sparse_results:
    r['score'] = r['score'] / max_sparse

# Combine
hybrid_results = {}
for r in dense_results:
    cid = r['chunk_id']
    hybrid_results[cid] = alpha * r['score']

for r in sparse_results:
    cid = r['chunk_id']
    if cid in hybrid_results:
        hybrid_results[cid] += (1 - alpha) * r['score']
    else:
        hybrid_results[cid] = (1 - alpha) * r['score']

# Sort by hybrid score
final_results = sorted(hybrid_results.items(), key=lambda x: x[1], reverse=True)
```

**Ví dụ kết quả:**
```
Chunk ID | Dense Score | Sparse Score | Hybrid Score (α=0.7)
─────────|─────────────|──────────────|────────────────────
   5     |    0.92     |     1.00     |   0.92*0.7 + 1.00*0.3 = 0.944
  12     |    0.88     |     0.80     |   0.88*0.7 + 0.80*0.3 = 0.856
   3     |    0.85     |     0.00     |   0.85*0.7 + 0.00*0.3 = 0.595
   7     |    0.00     |     0.85     |   0.00*0.7 + 0.85*0.3 = 0.255

Final Ranking: 5 > 12 > 3 > 7
```

**Tại sao hybrid tốt hơn?**
```
Example Query: "FORM nghỉ học"

Dense (Semantic):
✓ Tìm được "đơn xin nghỉ"
✓ Tìm được "xin phép vắng mặt"
✗ Bỏ sót "FORM" (keyword exact match)

Sparse (BM25):
✓ Tìm chính xác "FORM"
✓ Tìm chính xác "nghỉ học"
✗ Bỏ sót "đơn xin" (synonym)

Hybrid:
✓ Kết hợp cả hai
✓ Tốt nhất!
```

#### Bước 5: Reranking với Cross-Encoder

**Why Reranking?**
```
Bi-Encoder (SBERT):
- Encode query và documents separately
- Fast (can precompute document embeddings)
- Lower accuracy

Cross-Encoder:
- Process [query, document] as pair
- Slow (must compute for each pair)
- Higher accuracy

Solution:
1st stage: Bi-Encoder retrieves 100 candidates (fast)
2nd stage: Cross-Encoder reranks top 20 (accurate)
```

**Cross-Encoder Process:**
```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# Create [query, doc] pairs
pairs = [[query, chunk['content']] for chunk in top_chunks]

# Get relevance scores
scores = reranker.predict(pairs)

# Rerank
for chunk, score in zip(top_chunks, scores):
    chunk['rerank_score'] = score

top_chunks.sort(key=lambda x: x['rerank_score'], reverse=True)
final_chunks = top_chunks[:5]  # Top 5 after reranking
```

**Ví dụ reranking:**
```
Before Reranking (Hybrid Score):
1. Chunk 5  (score: 0.944)  "Form xin nghỉ học có phép quá 5 ngày..."
2. Chunk 12 (score: 0.856)  "Quy định về nghỉ học không phép..."
3. Chunk 3  (score: 0.595)  "Đơn xin nghỉ học có phép dưới 3 ngày..."
4. Chunk 18 (score: 0.544)  "Form đăng ký học phần..."

After Cross-Encoder Reranking:
1. Chunk 5  (rerank: 0.98)  "Form xin nghỉ học có phép quá 5 ngày..."
2. Chunk 3  (rerank: 0.92)  "Đơn xin nghỉ học có phép dưới 3 ngày..."
3. Chunk 12 (rerank: 0.75)  "Quy định về nghỉ học không phép..."
4. Chunk 18 (rerank: 0.23)  "Form đăng ký học phần..."

Note: Chunk 3 promoted because more relevant to query!
```

### 2.3. Phase 3: Generation

#### Bước 1: Context Assembly

```python
# Assemble context from top chunks
context = ""
sources = []

for i, chunk in enumerate(top_chunks[:5], 1):
    context += f"\n[Document {i}]\n"
    context += f"Heading: {chunk['heading']}\n"
    context += f"Content: {chunk['content']}\n"
    context += "-" * 50 + "\n"
    
    sources.append({
        "document": chunk['document_name'],
        "heading": chunk['heading'],
        "page": chunk['page_number']
    })
```

**Example context:**
```
[Document 1]
Heading: CHƯƠNG 2: QUY ĐỊNH VỀ NGHỈ HỌC
Content: Điều 3. Nghỉ học có phép
Sinh viên nghỉ học có phép từ 3 ngày trở xuống cần có giấy xin phép
của giảng viên. Nghỉ học có phép quá 5 ngày cần có xác nhận của
Hiệu trưởng và nộp form đơn xin nghỉ học.
--------------------------------------------------
[Document 2]
Heading: PHỤ LỤC: CÁC MẪU ĐƠN
Content: Form đơn xin nghỉ học (FORM_NGHI_HOC.doc)
Dùng cho trường hợp nghỉ học có phép quá 5 ngày...
--------------------------------------------------
```

#### Bước 2: Prompt Engineering

```python
prompt = f"""
Bạn là trợ lý AI của trường đại học, chuyên trả lời các câu hỏi về quy định, thủ tục.

CONTEXT (từ tài liệu chính thức của trường):
{context}

QUESTION:
{user_query}

INSTRUCTIONS:
1. Trả lời bằng tiếng Việt, rõ ràng và chính xác
2. Chỉ sử dụng thông tin từ CONTEXT, không tự sáng tác
3. Nếu CONTEXT không đủ thông tin, hãy nói rõ
4. Trích dẫn nguồn bằng cách đề cập đến [Document X]
5. Nếu có form/mẫu đơn liên quan, hãy đề cập
6. Sử dụng bullet points cho câu trả lời nhiều bước

ANSWER:
"""
```

**Prompt Engineering Best Practices:**
```
✅ DO:
- Clear role definition ("Bạn là trợ lý...")
- Explicit context provision
- Specific instructions
- Format requirements
- Constraint definitions ("Chỉ sử dụng...")

❌ DON'T:
- Vague prompts
- No constraints → hallucination risk
- No format guidance → inconsistent output
```

#### Bước 3: LLM Generation (Gemini)

```python
import requests

def generate_with_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.7,       # Balance creativity & accuracy
            "maxOutputTokens": 8192,  # Max response length
            "topP": 0.95,             # Nucleus sampling
            "topK": 40                # Top-K sampling
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    answer = result['candidates'][0]['content']['parts'][0]['text']
    return answer
```

**Gemini Parameters:**
```
temperature (0.0 - 1.0):
- 0.0: Deterministic, always same answer
- 0.7: Balanced (recommended)
- 1.0: Very creative, may deviate

topP (0.0 - 1.0):
- Nucleus sampling
- Consider tokens with cumulative probability topP
- 0.95 recommended

topK (integer):
- Consider only top K probable tokens
- 40 recommended for good diversity
```

#### Bước 4: Response Formatting

```python
# Format final response
response = {
    "answer": answer,
    "sources": [
        {
            "document": "QUY_CHE_DAO_TAO.pdf",
            "heading": "CHƯƠNG 2: QUY ĐỊNH VỀ NGHỈ HỌC",
            "page": 5,
            "relevance": 0.95
        },
        # ...
    ],
    "attachments": [
        {
            "file_name": "FORM_NGHI_HOC.doc",
            "download_url": "/api/v1/attachments/download/1",
            "description": "Form xin nghỉ học có phép"
        }
    ],
    "confidence": 0.92,
    "session_id": "abc123"
}
```

---

## 3. EMBEDDING & VECTOR SEARCH CHI TIẾT

### 3.1. Word Embeddings vs Sentence Embeddings

**Word Embeddings (Word2Vec, GloVe):**
```
"học"     → [0.2, -0.5, 0.3, ...]  (50-300 dim)
"sinh"    → [0.4, -0.2, 0.1, ...]
"viên"    → [-0.1, 0.3, -0.4, ...]

Problem: How to get sentence embedding?
"sinh viên" = average([0.2,-0.5,0.3], [0.4,-0.2,0.1], [-0.1,0.3,-0.4])
            = [0.17, -0.13, 0.0, ...]

Issues:
- Loses word order
- Loses context
- Poor for long sentences
```

**Sentence Embeddings (SBERT):**
```
"sinh viên học giỏi" → [0.45, -0.23, 0.67, ..., 0.12]  (384 dim)

Advantages:
- Captures full meaning
- Preserves context
- Better for similarity
```

### 3.2. Sentence-BERT Architecture

```
Input: "Quy định về nghỉ học có phép"
    ↓
Tokenization: [CLS] quy định về nghỉ học có phép [SEP]
    ↓
Token Embeddings (BERT Base):
    [CLS]   → [-0.2, 0.5, ...]
    "quy"   → [0.3, -0.1, ...]
    "định"  → [0.1, 0.4, ...]
    ...
    [SEP]   → [0.0, -0.3, ...]
    ↓
BERT Layers (12 transformer layers):
    Layer 1  → contextual representations
    Layer 2  → more contextual
    ...
    Layer 12 → final representations
    ↓
Mean Pooling:
    Average all token embeddings
    ↓
Normalization:
    ||embedding|| = 1
    ↓
Output: [0.45, -0.23, 0.67, ..., 0.12]  (384-dim)
```

### 3.3. Vietnamese SBERT Training

**Training Data:**
```
Parallel sentences (Vietnamese):
- Original: "Sinh viên cần nộp đơn"
- Paraphrase: "Học sinh phải nộp đơn xin"
→ Should have high similarity

Negative samples:
- "Sinh viên cần nộp đơn"
- "Thời tiết hôm nay đẹp"
→ Should have low similarity
```

**Training Objective (Contrastive Learning):**
```
minimize: distance(anchor, positive)
maximize: distance(anchor, negative)

Loss = max(0, distance(anchor, positive) - distance(anchor, negative) + margin)
```

### 3.4. Vector Similarity Metrics

**Cosine Similarity:**
```python
def cosine_similarity(vec1, vec2):
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    return dot_product / (norm1 * norm2)

# Range: [-1, 1]
# -1: opposite direction
#  0: orthogonal
#  1: same direction
```

**Euclidean Distance:**
```python
def euclidean_distance(vec1, vec2):
    return np.sqrt(np.sum((vec1 - vec2)**2))

# Range: [0, ∞)
# 0: identical
# Large: very different
```

**Dot Product:**
```python
def dot_product(vec1, vec2):
    return np.dot(vec1, vec2)

# For normalized vectors, equivalent to cosine similarity
```

**pgvector operators:**
```sql
-- Cosine distance (0 = identical, 2 = opposite)
embedding <=> query_embedding

-- Euclidean distance (L2)
embedding <-> query_embedding

-- Dot product (inner product)
embedding <#> query_embedding

-- Cosine similarity (most common for SBERT)
1 - (embedding <=> query_embedding)
```

### 3.5. Approximate Nearest Neighbor (ANN)

**Problem:**
```
Exact search (brute force):
- Compare query with ALL vectors
- Time: O(N * D) where N = number of vectors, D = dimension
- For 10,000 chunks, 384 dim: ~3.84M operations
- Too slow!
```

**Solution: IVFFlat Index:**
```
1. Training Phase:
   - Cluster vectors into K clusters (e.g., K=100)
   - Find K centroids using k-means

2. Indexing Phase:
   - Assign each vector to nearest centroid
   - Store in inverted lists

3. Query Phase:
   - Find nearest centroids (nprobe=10)
   - Search only in those 10 lists
   - Much faster!

Time: O(K + nprobe * (N/K) * D)
For K=100, nprobe=10: ~40K operations (100x faster!)
```

**Trade-off:**
```
Exact Search:
- Accuracy: 100%
- Speed: Slow

IVFFlat (nprobe=10):
- Accuracy: ~95-98%
- Speed: 10-100x faster

HNSW (Hierarchical Navigable Small World):
- Accuracy: ~98-99%
- Speed: 5-50x faster
- Memory: Higher
```

---

## 4. HYBRID SEARCH CHI TIẾT

### 4.1. Tại sao cần Hybrid?

**Scenario 1: Semantic query**
```
Query: "làm sao để được miễn học phí?"

Dense (Vector):
✓ "điều kiện được miễn giảm học phí"     (similarity: 0.92)
✓ "các trường hợp được xét miễn học phí" (similarity: 0.88)
✓ "quy trình xin miễn học phí"           (similarity: 0.85)

Sparse (BM25):
✗ Poor results (no exact keyword match)
```

**Scenario 2: Keyword query**
```
Query: "FORM đăng ký chuyển ngành"

Sparse (BM25):
✓ "Tải FORM đăng ký chuyển ngành tại..."  (score: 8.5)
✓ "Hướng dẫn điền FORM chuyển ngành"      (score: 7.2)

Dense (Vector):
✗ May miss due to different phrasing
```

**Scenario 3: Mixed query**
```
Query: "FORM xin nghỉ học có phép"

Hybrid:
✓ Finds "FORM" exactly (BM25)
✓ Finds "xin nghỉ" semantically (Dense)
✓ Best of both worlds!
```

### 4.2. BM25 Algorithm Deep Dive

**Intuition:**
```
TF (Term Frequency):
- More occurrences → higher score
- But diminishing returns (log scale)

IDF (Inverse Document Frequency):
- Rare terms → higher score
- Common terms (e.g., "là", "của") → lower score

Document Length Normalization:
- Longer documents penalized
- Prevents bias towards long documents
```

**Formula Breakdown:**
```
BM25(D,Q) = Σ IDF(qi) * (f(qi,D) * (k1 + 1)) / (f(qi,D) + k1 * (1 - b + b * |D|/avgdl))
            for each query term qi

IDF(qi) = log((N - n(qi) + 0.5) / (n(qi) + 0.5))
where:
- N = total number of documents
- n(qi) = number of documents containing qi

Parameters:
- k1 = 1.5 (term saturation, higher = more importance to TF)
- b = 0.75 (length normalization, 0 = no norm, 1 = full norm)
```

**Example Calculation:**
```
Corpus:
Doc1: "học sinh nghỉ học"
Doc2: "sinh viên nghỉ phép"
Doc3: "quy định về học phí"

Query: "nghỉ học"

Step 1: Calculate IDF
- IDF("nghỉ") = log((3 - 2 + 0.5) / (2 + 0.5)) = log(1.5/2.5) = -0.51
- IDF("học") = log((3 - 2 + 0.5) / (2 + 0.5)) = log(1.5/2.5) = -0.51

Wait, negative IDF? Let's use proper formula:
IDF("nghỉ") = log(3/2) = 0.405
IDF("học") = log(3/2) = 0.405

Step 2: Calculate TF component for Doc1
- f("nghỉ", Doc1) = 1
- f("học", Doc1) = 2
- |Doc1| = 4, avgdl = 3.67

TF_component("nghỉ") = (1 * (1.5 + 1)) / (1 + 1.5 * (1 - 0.75 + 0.75 * 4/3.67))
                     = 2.5 / (1 + 1.5 * 0.997)
                     = 2.5 / 2.496 = 1.002

TF_component("học") = (2 * 2.5) / (2 + 1.5 * 0.997)
                    = 5.0 / 3.496 = 1.430

Step 3: Final BM25 score
BM25(Doc1, "nghỉ học") = IDF("nghỉ") * 1.002 + IDF("học") * 1.430
                       = 0.405 * 1.002 + 0.405 * 1.430
                       = 0.406 + 0.579
                       = 0.985
```

### 4.3. Fusion Strategies

**Reciprocal Rank Fusion (RRF):**
```python
def reciprocal_rank_fusion(rankings, k=60):
    scores = {}
    for ranking in rankings:
        for rank, doc_id in enumerate(ranking, 1):
            if doc_id not in scores:
                scores[doc_id] = 0
            scores[doc_id] += 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

# Example:
dense_ranking = [5, 12, 3, 18, 7]    # chunk IDs
sparse_ranking = [5, 7, 12, 20, 3]

# RRF scores:
# Chunk 5:  1/(60+1) + 1/(60+1) = 0.0328
# Chunk 12: 1/(60+2) + 1/(60+3) = 0.0317
# Chunk 3:  1/(60+3) + 1/(60+5) = 0.0293
```

**Weighted Linear Combination:**
```python
def weighted_fusion(dense_scores, sparse_scores, alpha=0.7):
    # Normalize scores to [0, 1]
    dense_scores = normalize(dense_scores)
    sparse_scores = normalize(sparse_scores)
    
    # Combine
    combined = {}
    for doc_id in set(dense_scores.keys()) | set(sparse_scores.keys()):
        d_score = dense_scores.get(doc_id, 0)
        s_score = sparse_scores.get(doc_id, 0)
        combined[doc_id] = alpha * d_score + (1 - alpha) * s_score
    
    return sorted(combined.items(), key=lambda x: x[1], reverse=True)
```

**Adaptive Weighting:**
```python
def adaptive_fusion(query, dense_scores, sparse_scores):
    # Nếu query có nhiều keywords cụ thể → tăng weight cho sparse
    if has_many_specific_keywords(query):
        alpha = 0.5  # Equal weight
    # Nếu query semantic → tăng weight cho dense
    elif is_semantic_query(query):
        alpha = 0.8  # Favor dense
    else:
        alpha = 0.7  # Default
    
    return weighted_fusion(dense_scores, sparse_scores, alpha)
```

---

## 5. CROSS-ENCODER RERANKING

### 5.1. Bi-Encoder vs Cross-Encoder

**Bi-Encoder (SBERT):**
```
Query:    "nghỉ học"  →  Encoder  →  [0.2, 0.5, ...]
Document: "xin nghỉ"  →  Encoder  →  [0.25, 0.48, ...]
                                         ↓
                                  Similarity (cosine)
                                         ↓
                                      Score: 0.95

Pros:
- Fast (can precompute document embeddings)
- Scalable
Cons:
- Lower accuracy (no interaction between query and doc)
```

**Cross-Encoder:**
```
[CLS] nghỉ học [SEP] xin nghỉ [SEP]
            ↓
    Full BERT Model (12 layers)
            ↓
      [CLS] representation
            ↓
    Classification layer
            ↓
    Relevance score: 0.98

Pros:
- Higher accuracy (full attention between query and doc)
Cons:
- Slow (must compute for each pair)
- Not scalable for first-stage retrieval
```

### 5.2. Two-Stage Retrieval Pipeline

```
Stage 1: Bi-Encoder (Fast, broad)
- Retrieve 100 candidates from 10,000 documents
- Time: ~50ms

Stage 2: Cross-Encoder (Slow, accurate)
- Rerank top 20 candidates
- Time: ~200ms

Total: ~250ms (much faster than cross-encoder on all 10,000!)
```

### 5.3. Cross-Encoder Training

**Training Data:**
```
[query, relevant_doc, score=1.0]
[query, irrelevant_doc, score=0.0]

Example:
["nghỉ học", "quy định về nghỉ học có phép...", 1.0]
["nghỉ học", "thời khóa biểu học kỳ 1...", 0.0]
```

**Training Objective:**
```
Binary Cross-Entropy Loss:
loss = -[y * log(p) + (1-y) * log(1-p)]

where:
- y = true label (0 or 1)
- p = predicted probability
```

---

## 6. LLM INTEGRATION & PROMPT ENGINEERING

### 6.1. Prompt Components

**System Prompt:**
```
Defines:
- Role/persona
- Capabilities
- Constraints
- Tone/style

Example:
"Bạn là trợ lý AI của trường đại học.
Nhiệm vụ: Trả lời câu hỏi về quy định, thủ tục.
Yêu cầu: Chính xác, rõ ràng, dựa trên tài liệu.
Giọng điệu: Thân thiện, chuyên nghiệp."
```

**Context:**
```
Retrieved information từ RAG
- Relevant chunks
- Source citations
- Metadata
```

**User Query:**
```
Câu hỏi gốc của user
```

**Instructions:**
```
Specific guidelines cho response:
- Format (bullet points, numbered list)
- Length constraints
- Citation requirements
- Language
```

### 6.2. Advanced Prompt Techniques

**Few-Shot Learning:**
```
prompt = """
Examples:
Q: "Quy định về nghỉ học như thế nào?"
A: "Theo quy chế đào tạo:
   - Nghỉ ≤ 3 ngày: xin phép giảng viên
   - Nghỉ > 5 ngày: xin phép hiệu trưởng, nộp form
   [Nguồn: QUY_CHE_DAO_TAO.pdf, Chương 2]"

Now answer:
Q: {user_query}
"""
```

**Chain-of-Thought:**
```
prompt = """
Hãy suy nghĩ từng bước:
1. Phân tích câu hỏi: user muốn biết gì?
2. Tìm thông tin liên quan trong CONTEXT
3. Tổng hợp và trả lời
4. Trích dẫn nguồn

CONTEXT: {...}
QUESTION: {query}
"""
```

**Self-Consistency:**
```
# Generate multiple answers
answers = []
for i in range(3):
    answer = llm.generate(prompt, temperature=0.8)
    answers.append(answer)

# Vote or merge
final_answer = majority_vote(answers)
```

### 6.3. Gemini API Parameters

**temperature:**
```
0.0: Deterministic
- Pro: Consistent, predictable
- Con: May be repetitive
- Use: Factual queries

0.7: Balanced (recommended)
- Pro: Good balance
- Con: Slight variation
- Use: Most cases

1.0: Creative
- Pro: Diverse responses
- Con: May hallucinate
- Use: Creative writing (NOT for our chatbot)
```

**topP (Nucleus Sampling):**
```
Algorithm:
1. Sort tokens by probability
2. Select top tokens with cumulative probability ≤ topP
3. Sample from selected tokens

Example (topP=0.9):
Token probabilities: {A: 0.5, B: 0.3, C: 0.15, D: 0.05}
Cumulative: {A: 0.5, B: 0.8, C: 0.95, D: 1.0}
Selected: {A, B, C} (cumulative ≤ 0.95)
Sample from {A, B, C}
```

**topK:**
```
Select top K most probable tokens

Example (topK=3):
All tokens: {A: 0.5, B: 0.3, C: 0.15, D: 0.04, E: 0.01}
Top 3: {A, B, C}
Sample from {A, B, C}
```

**maxOutputTokens:**
```
8192 tokens ≈ 6000 words ≈ 12 pages

Calculation:
1 token ≈ 0.75 words (English)
1 token ≈ 0.5-1 character (Vietnamese)

Our setting: 8192 (generous for detailed answers)
```

---

## 7. CONVERSATION MEMORY

### 7.1. Memory Types

**Short-term (In-Memory):**
```python
conversations = {
    "session_abc123": {
        "messages": [
            {"role": "user", "content": "Quy định nghỉ học?"},
            {"role": "assistant", "content": "Nghỉ ≤ 3 ngày..."},
        ],
        "timestamp": "2024-12-09T10:30:00"
    }
}
```

**Long-term (Database):**
```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100),
    messages JSONB,
    created_at TIMESTAMP
);
```

### 7.2. Context Window Management

**Problem:**
```
LLM has limited context window (e.g., 1M tokens for Gemini)
Long conversation → too many tokens → expensive/slow
```

**Solution: Sliding Window**
```python
MAX_HISTORY = 5  # Last 5 exchanges

def get_conversation_context(session_id):
    messages = get_messages(session_id)
    recent_messages = messages[-MAX_HISTORY:]
    
    context = ""
    for msg in recent_messages:
        context += f"{msg['role']}: {msg['content']}\n"
    
    return context
```

**Solution: Summarization**
```python
def summarize_old_messages(messages):
    old_messages = messages[:-5]  # All except recent 5
    
    prompt = f"""
    Summarize this conversation:
    {old_messages}
    
    Focus on key information and context.
    """
    
    summary = llm.generate(prompt)
    return summary
```

### 7.3. Contextual Follow-up

**Example:**
```
User: "Quy định về nghỉ học?"
Bot: "Nghỉ ≤ 3 ngày: xin phép GV. Nghỉ > 5 ngày: xin phép HT."

User: "Cần form gì không?" (follow-up)
Bot needs to understand "form gì" refers to "nghỉ học"

Solution: Include previous exchange in prompt
```

**Implementation:**
```python
def query_with_context(query, session_id):
    # Get recent messages
    history = get_conversation_context(session_id)
    
    # Append to prompt
    prompt = f"""
    CONVERSATION HISTORY:
    {history}
    
    CURRENT QUESTION:
    {query}
    
    CONTEXT:
    {retrieved_chunks}
    
    Answer the CURRENT QUESTION, considering CONVERSATION HISTORY.
    """
    
    answer = llm.generate(prompt)
    return answer
```

---

## 8. PERFORMANCE OPTIMIZATION

### 8.1. Caching Strategy

**Multi-Level Cache:**
```
L1: Model Cache (GPU/CPU Memory)
- Embedding model
- Reranker model
- BM25 index

L2: Redis Cache (7 days)
- Embeddings
- Frequent queries
- Session data

L3: Database (Permanent)
- All data
```

**Cache Key Design:**
```python
# Embedding cache
key = f"embedding:{hash(text)}"
value = embedding_vector (pickled)

# Query cache
key = f"query:{hash(normalized_query)}:{top_k}:{alpha}"
value = json({answer, sources, attachments})

# Session cache
key = f"session:{session_id}"
value = json({messages, metadata})
```

### 8.2. Database Optimization

**Connection Pooling:**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Maintain 10 connections
    max_overflow=20,     # Allow 20 additional temp connections
    pool_pre_ping=True,  # Verify connection before use
    pool_recycle=3600    # Recycle connections after 1 hour
)
```

**Query Optimization:**
```sql
-- Bad: Full table scan
SELECT * FROM chunks WHERE content LIKE '%nghỉ học%';

-- Good: Use index
SELECT * FROM chunks 
WHERE is_active = true
AND id IN (
    SELECT chunk_id FROM embeddings
    WHERE 1 - (embedding <=> query_vec) > 0.7
    ORDER BY embedding <=> query_vec
    LIMIT 20
);

-- Check query plan
EXPLAIN ANALYZE SELECT ...;
```

### 8.3. Async Processing

**Background Tasks:**
```python
@app.post("/documents/upload")
async def upload_document(file, background_tasks: BackgroundTasks):
    # Save file immediately
    file_path = save_file(file)
    
    # Process in background
    background_tasks.add_task(process_pdf, file_path)
    
    return {"status": "processing", "file_path": file_path}

# User gets immediate response
# Processing happens asynchronously
```

**Batch Processing:**
```python
# Bad: Process one by one
for chunk in chunks:
    embedding = model.encode(chunk)
    save_embedding(embedding)

# Good: Batch process
embeddings = model.encode(chunks, batch_size=32)
save_embeddings_batch(embeddings)

# 10-100x faster!
```

---

## 9. EVALUATION & METRICS

### 9.1. Retrieval Metrics

**Precision @ K:**
```
Precision@5 = (Number of relevant documents in top 5) / 5

Example:
Retrieved: [relevant, relevant, irrelevant, relevant, irrelevant]
Precision@5 = 3/5 = 0.6
```

**Recall @ K:**
```
Recall@5 = (Number of relevant documents in top 5) / (Total relevant documents)

Example:
Total relevant: 10
Retrieved relevant: 3
Recall@5 = 3/10 = 0.3
```

**Mean Reciprocal Rank (MRR):**
```
MRR = Average(1 / rank of first relevant document)

Example:
Query 1: First relevant at rank 1 → 1/1 = 1.0
Query 2: First relevant at rank 3 → 1/3 = 0.33
Query 3: First relevant at rank 2 → 1/2 = 0.5
MRR = (1.0 + 0.33 + 0.5) / 3 = 0.61
```

### 9.2. Generation Metrics

**BLEU Score:**
```
Measures overlap between generated and reference answer
Range: [0, 1]
Higher = better

Not ideal for RAG (multiple valid answers)
```

**ROUGE Score:**
```
Measures recall of n-grams
ROUGE-1: unigrams
ROUGE-2: bigrams
ROUGE-L: longest common subsequence

Better for summarization than RAG
```

**Semantic Similarity:**
```python
# Compare embeddings
generated_emb = model.encode(generated_answer)
reference_emb = model.encode(reference_answer)
similarity = cosine_similarity(generated_emb, reference_emb)
```

### 9.3. End-to-End Metrics

**Answer Relevance:**
```
Human evaluation:
- Is the answer relevant to the question?
- Scale: 1-5
```

**Faithfulness:**
```
- Does the answer stay faithful to the retrieved context?
- No hallucination?
- Scale: 1-5
```

**Completeness:**
```
- Does the answer fully address the question?
- Missing information?
- Scale: 1-5
```

**User Feedback:**
```
- Thumbs up/down
- Follow-up questions (indicates satisfaction/confusion)
```

---

## 10. COMMON CHALLENGES & SOLUTIONS

### 10.1. Challenge: Low Retrieval Quality

**Symptoms:**
- Irrelevant chunks retrieved
- Low confidence scores
- User complaints

**Diagnosis:**
```python
# Check retrieval results
results = retrieval_service.search(query)
for r in results:
    print(f"Score: {r['score']}, Content: {r['content'][:100]}")
```

**Solutions:**
1. **Improve chunking**
   - Reduce chunk size
   - Add more overlap
   - Better heading detection

2. **Adjust thresholds**
   ```python
   DENSE_SIMILARITY_THRESHOLD = 0.7  # Increase to 0.75
   SPARSE_SIMILARITY_THRESHOLD = 0.5  # Increase to 0.6
   ```

3. **Tune fusion weights**
   ```python
   DENSE_WEIGHT = 0.7  # Try 0.6 or 0.8
   ```

4. **Add more training data**
   - Upload more PDFs
   - Diversify content

### 10.2. Challenge: Slow Response Time

**Symptoms:**
- Response time > 3 seconds
- Timeout errors

**Diagnosis:**
```python
import time

start = time.time()
# ... step 1 ...
print(f"Step 1: {time.time() - start:.2f}s")
# ... step 2 ...
print(f"Step 2: {time.time() - start:.2f}s")
```

**Solutions:**
1. **Enable caching**
   ```python
   ENABLE_REDIS_CACHE = True
   ```

2. **Reduce TOP_K**
   ```python
   TOP_K_RESULTS = 3  # Instead of 5
   ```

3. **Optimize database**
   ```sql
   VACUUM ANALYZE embeddings;
   REINDEX TABLE embeddings;
   ```

4. **Use GPU**
   ```python
   # For embedding generation
   device = "cuda" if torch.cuda.is_available() else "cpu"
   ```

### 10.3. Challenge: LLM Hallucination

**Symptoms:**
- Answer contains information not in context
- Fabricated sources

**Diagnosis:**
```python
# Check if answer content is in retrieved chunks
def check_hallucination(answer, chunks):
    for sentence in answer.split('.'):
        found = any(sentence.lower() in chunk.lower() for chunk in chunks)
        if not found:
            print(f"Potential hallucination: {sentence}")
```

**Solutions:**
1. **Strengthen prompt**
   ```python
   prompt = """
   CRITICAL: Only use information from CONTEXT.
   If CONTEXT doesn't contain answer, say "Tôi không tìm thấy..."
   DO NOT make up information.
   """
   ```

2. **Lower temperature**
   ```python
   temperature = 0.3  # More deterministic
   ```

3. **Add verification step**
   ```python
   # Generate answer
   answer = llm.generate(prompt)
   
   # Verify against context
   if not verify_answer(answer, context):
       answer = "Tôi không chắc chắn về thông tin này..."
   ```

### 10.4. Challenge: Memory Issues

**Symptoms:**
- Out of memory errors
- System crashes
- Slow performance

**Solutions:**
1. **Reduce batch size**
   ```python
   EMBEDDING_BATCH_SIZE = 16  # Default: 32
   ```

2. **Use smaller model**
   ```python
   EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dim instead of 768
   ```

3. **Clear cache periodically**
   ```python
   # Every hour
   cache_service.clear_old_entries(max_age=3600)
   ```

4. **Limit Docker memory**
   ```yaml
   services:
     backend:
       mem_limit: 4g
   ```

---

## 11. FUTURE IMPROVEMENTS

### 11.1. Advanced RAG Techniques

**Query Decomposition:**
```
Complex query: "So sánh quy định nghỉ học và bảo lưu"
    ↓
Decompose:
  1. "Quy định về nghỉ học"
  2. "Quy định về bảo lưu"
    ↓
Retrieve for each sub-query
    ↓
Synthesize final answer
```

**Multi-hop Reasoning:**
```
Query: "Nếu bảo lưu xong muốn quay lại học thì cần làm gì?"
    ↓
Hop 1: Find "quy định bảo lưu"
Hop 2: Find "quy trình quay lại sau bảo lưu"
    ↓
Combine information
```

**Self-RAG (Self-Reflective RAG):**
```
1. Generate initial answer
2. Check: "Is this answer good?"
3. If not: Retrieve more context
4. Generate improved answer
5. Repeat until satisfied
```

### 11.2. Multimodal RAG

**Process Images/Charts:**
```
PDF contains:
- Text → Extract with PyPDF2
- Tables → Extract with pdfplumber
- Charts → OCR + Image understanding (GPT-4V)
- Diagrams → Convert to text description
```

**Visual Question Answering:**
```
User: "Cho tôi xem sơ đồ quy trình đăng ký học phần"
    ↓
Retrieve relevant page image
    ↓
Display image + text explanation
```

### 11.3. Advanced Evaluation

**Automatic Evaluation:**
```python
def evaluate_rag_system(test_queries):
    results = []
    for query, ground_truth in test_queries:
        answer = rag_system.query(query)
        
        # Metrics
        relevance = semantic_similarity(answer, ground_truth)
        faithfulness = check_faithfulness(answer, retrieved_chunks)
        
        results.append({
            "query": query,
            "relevance": relevance,
            "faithfulness": faithfulness
        })
    
    return aggregate_results(results)
```

**A/B Testing:**
```
Version A: Current system
Version B: New chunking strategy

Route 50% of traffic to each
Compare metrics:
- Response time
- User satisfaction
- Accuracy
```

---

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot AI Team
