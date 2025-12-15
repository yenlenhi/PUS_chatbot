# QUY TRÌNH XỬ LÝ DOCUMENT TRONG HỆ THỐNG

## MỤC LỤC

1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc xử lý Document](#2-kiến-trúc-xử-lý-document)
3. [Phase 1: Document Ingestion](#3-phase-1-document-ingestion)
4. [Phase 2: Text Extraction](#4-phase-2-text-extraction)
5. [Phase 3: Chunking Strategy](#5-phase-3-chunking-strategy)
6. [Phase 4: Embedding Generation](#6-phase-4-embedding-generation)
7. [Phase 5: Storage & Indexing](#7-phase-5-storage--indexing)
8. [Auto-Ingestion Service](#8-auto-ingestion-service)
9. [Document Management](#9-document-management)
10. [Monitoring & Troubleshooting](#10-monitoring--troubleshooting)

---

## 1. TỔNG QUAN

### 1.1. Giới thiệu

Quy trình xử lý document là backbone của hệ thống RAG. Nó chịu trách nhiệm:
- Tiếp nhận và xử lý tài liệu PDF
- Trích xuất text với độ chính xác cao
- Chia nhỏ thành chunks hợp lý
- Tạo embeddings cho semantic search
- Lưu trữ và index trong database

### 1.2. Luồng xử lý tổng quan

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING FLOW                      │
└─────────────────────────────────────────────────────────────────┘

PDF Upload/Drop
    ↓
┌──────────────────────────────────────────┐
│  PHASE 1: INGESTION                      │
│  - Detect new PDF                        │
│  - Validate file                         │
│  - Calculate hash                        │
│  - Check duplicates                      │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  PHASE 2: TEXT EXTRACTION                │
│  - Try Gemini Vision API (OCR)          │
│  - Fallback to pdfplumber               │
│  - Fallback to PyPDF2                   │
│  - Page-by-page extraction              │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  PHASE 3: CHUNKING                       │
│  - Detect headings                       │
│  - Smart section splitting              │
│  - Context preservation                  │
│  - Metadata enrichment                   │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  PHASE 4: EMBEDDING GENERATION           │
│  - Batch processing                      │
│  - Vietnamese SBERT                      │
│  - 384-dimensional vectors              │
│  - Cache embeddings                      │
└──────────────────────────────────────────┘
    ↓
┌──────────────────────────────────────────┐
│  PHASE 5: STORAGE & INDEXING             │
│  - Insert into PostgreSQL                │
│  - Store embeddings (pgvector)          │
│  - Build BM25 index                      │
│  - Update analytics                      │
└──────────────────────────────────────────┘
    ↓
Ready for Retrieval!
```

### 1.3. Thống kê xử lý

**Average Processing Time:**
```
Small PDF (< 10 pages):     ~30 seconds
Medium PDF (10-50 pages):   ~2 minutes
Large PDF (50-100 pages):   ~5 minutes
Very Large (100+ pages):    ~10-15 minutes
```

**Breakdown:**
```
Text Extraction:        40% of time
Chunking:              10% of time
Embedding Generation:   45% of time
Storage & Indexing:     5% of time
```

---

## 2. KIẾN TRÚC XỬ LÝ DOCUMENT

### 2.1. Components Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DOCUMENT PROCESSING LAYER                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌─────────────────────┐              │
│  │ IngestionService │────▶│  PDFProcessor       │              │
│  │                  │     │  - Extract text     │              │
│  │ - File watching  │     │  - Gemini OCR       │              │
│  │ - Queue mgmt     │     │  - pdfplumber       │              │
│  │ - Orchestration  │     │  - PyPDF2           │              │
│  └──────────────────┘     └─────────────────────┘              │
│           │                         │                           │
│           │                         ↓                           │
│           │               ┌─────────────────────┐               │
│           │               │  HeadingChunker     │               │
│           │               │  - Pattern matching │               │
│           │               │  - Smart splitting  │               │
│           │               │  - Context preserve │               │
│           │               └─────────────────────┘               │
│           │                         │                           │
│           ↓                         ↓                           │
│  ┌──────────────────────────────────────────┐                  │
│  │         EmbeddingService                 │                  │
│  │  - Vietnamese SBERT                      │                  │
│  │  - Batch processing                      │                  │
│  │  - Redis caching                         │                  │
│  └──────────────────────────────────────────┘                  │
│           │                                                     │
│           ↓                                                     │
│  ┌──────────────────────────────────────────┐                  │
│  │    PostgresDatabaseService               │                  │
│  │  - Documents table                       │                  │
│  │  - Chunks table                          │                  │
│  │  - Embeddings table (pgvector)           │                  │
│  └──────────────────────────────────────────┘                  │
│           │                                                     │
│           ↓                                                     │
│  ┌──────────────────────────────────────────┐                  │
│  │   HybridRetrievalService                 │                  │
│  │  - Rebuild BM25 index                    │                  │
│  │  - Update statistics                     │                  │
│  └──────────────────────────────────────────┘                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2. Class Diagram

```python
┌─────────────────────────┐
│   IngestionService      │
├─────────────────────────┤
│ - db_service            │
│ - embedding_service     │
│ - pdf_processor         │
│ - observer (Watchdog)   │
├─────────────────────────┤
│ + start_watching()      │
│ + process_pdf()         │
│ + process_directory()   │
└─────────────────────────┘
            │
            │ uses
            ↓
┌─────────────────────────┐
│     PDFProcessor        │
├─────────────────────────┤
│ - gemini_service        │
│ - heading_chunker       │
├─────────────────────────┤
│ + extract_text()        │
│ + process_pdf()         │
└─────────────────────────┘
            │
            │ uses
            ↓
┌─────────────────────────┐
│    HeadingChunker       │
├─────────────────────────┤
│ - min_chunk_size        │
│ - max_chunk_size        │
│ - heading_patterns[]    │
├─────────────────────────┤
│ + extract_headings()    │
│ + chunk_by_headings()   │
│ + smart_split()         │
└─────────────────────────┘
```

---

## 3. PHASE 1: DOCUMENT INGESTION

### 3.1. Upload Methods

#### Method 1: Admin UI Upload

```
User Action:
1. Navigate to Admin Dashboard
2. Click "Upload Document"
3. Select PDF file
4. Click "Upload"

Backend Flow:
POST /api/v1/documents/upload
    ↓
1. Validate file (type, size)
2. Save to temporary location
3. Calculate file hash
4. Check for duplicates
5. Create document record
6. Queue for processing
7. Return document_id
```

**API Example:**
```python
@router.post("/documents/upload")
async def upload_document(
    file: UploadFile,
    background_tasks: BackgroundTasks
):
    # Validate
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files allowed")
    
    if file.size > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(400, "File too large")
    
    # Save file
    file_path = save_uploaded_file(file)
    
    # Create document record
    doc_id = db.create_document(
        filename=file.filename,
        file_path=str(file_path),
        file_size=file.size,
        status="pending"
    )
    
    # Process in background
    background_tasks.add_task(
        process_document_async,
        doc_id,
        file_path
    )
    
    return {"document_id": doc_id, "status": "processing"}
```

#### Method 2: Auto-Ingestion (File Drop)

```
User Action:
Copy PDF to data/new_pdf/

System Response:
1. Watchdog detects new file
2. Triggers on_created event
3. Auto-processes file
4. Moves to data/processed/
```

**Watchdog Implementation:**
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.src_path.endswith('.pdf'):
            log.info(f"New PDF detected: {event.src_path}")
            asyncio.create_task(
                ingestion_service.process_pdf(event.src_path)
            )

# Start watching
observer = Observer()
observer.schedule(handler, "data/new_pdf/", recursive=False)
observer.start()
```

#### Method 3: Bulk Upload via Script

```bash
# Process all PDFs in directory
python scripts/process_pdfs.py

# With Gemini OCR
python scripts/process_pdfs.py --use-gemini

# Without Gemini (faster, lower quality for scanned docs)
python scripts/process_pdfs.py --no-gemini
```

### 3.2. Validation & Preprocessing

**File Validation:**
```python
def validate_pdf(file_path: Path) -> dict:
    """
    Validate PDF file before processing
    
    Returns:
        dict with validation results
    """
    results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }
    
    # Check file exists
    if not file_path.exists():
        results["valid"] = False
        results["errors"].append("File not found")
        return results
    
    # Check file size
    size = file_path.stat().st_size
    if size > 50 * 1024 * 1024:  # 50MB
        results["warnings"].append("Large file, processing may be slow")
    
    if size == 0:
        results["valid"] = False
        results["errors"].append("File is empty")
        return results
    
    # Check if valid PDF
    try:
        with open(file_path, 'rb') as f:
            header = f.read(4)
            if header != b'%PDF':
                results["valid"] = False
                results["errors"].append("Not a valid PDF file")
    except Exception as e:
        results["valid"] = False
        results["errors"].append(f"Cannot read file: {e}")
    
    # Check if password protected
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            if reader.is_encrypted:
                results["valid"] = False
                results["errors"].append("PDF is password protected")
    except Exception as e:
        results["warnings"].append(f"Could not check encryption: {e}")
    
    return results
```

**Duplicate Detection:**
```python
def check_duplicate(file_path: Path, db_service) -> Optional[int]:
    """
    Check if document already exists using file hash
    
    Returns:
        document_id if duplicate found, None otherwise
    """
    # Calculate SHA-256 hash
    import hashlib
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    
    file_hash = sha256.hexdigest()
    
    # Check in database
    existing_doc = db_service.get_document_by_hash(file_hash)
    
    if existing_doc:
        log.warning(f"Duplicate detected: {file_path.name}")
        log.warning(f"Matches existing document ID: {existing_doc['id']}")
        return existing_doc['id']
    
    return None
```

### 3.3. Document Status Tracking

**Status Flow:**
```
pending → processing → completed
              ↓
            failed
```

**Database Schema:**
```sql
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_hash VARCHAR(64),
    total_chunks INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    processing_started_at TIMESTAMP,
    processing_completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);
```

**Status Updates:**
```python
# Start processing
db.update_document_status(
    doc_id,
    status="processing",
    processing_started_at=datetime.now()
)

# Success
db.update_document_status(
    doc_id,
    status="completed",
    total_chunks=len(chunks),
    processing_completed_at=datetime.now()
)

# Failure
db.update_document_status(
    doc_id,
    status="failed",
    error_message=str(error),
    processing_completed_at=datetime.now()
)
```

---

## 4. PHASE 2: TEXT EXTRACTION

### 4.1. Multi-Layer Extraction Strategy

**Strategy Overview:**
```
Layer 1: Gemini Vision API (Best quality, slower, costs tokens)
    ↓ (if fails or unavailable)
Layer 2: pdfplumber (Good for formatted PDFs)
    ↓ (if fails)
Layer 3: PyPDF2 (Basic, fast, works for most PDFs)
```

### 4.2. Gemini Vision API (OCR)

**Why Gemini?**
- ✅ Best OCR quality, especially for scanned documents
- ✅ Handles complex layouts (tables, multi-column)
- ✅ Preserves formatting and structure
- ✅ Works with images embedded in PDFs
- ❌ Slower (API call per page)
- ❌ Costs tokens

**Implementation:**
```python
class GeminiPDFService:
    def extract_text_from_pdf(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extract text from PDF using Gemini Vision API
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of (page_number, text) tuples
        """
        try:
            # Convert PDF pages to images
            images = self.pdf_to_images(pdf_path)
            
            pages_text = []
            
            for page_num, image in enumerate(images, 1):
                log.info(f"Processing page {page_num} with Gemini...")
                
                # Encode image to base64
                image_data = self.encode_image(image)
                
                # Call Gemini Vision API
                prompt = """
                Extract all text from this document page.
                Preserve formatting, headings, and structure.
                Output plain text with line breaks preserved.
                """
                
                response = self.call_gemini_vision(
                    prompt=prompt,
                    image_data=image_data
                )
                
                if response and response.text:
                    pages_text.append((page_num, response.text))
                else:
                    log.warning(f"No text extracted from page {page_num}")
            
            log.info(f"Gemini extracted text from {len(pages_text)} pages")
            return pages_text
            
        except Exception as e:
            log.error(f"Gemini extraction failed: {e}")
            return []
    
    def pdf_to_images(self, pdf_path: Path) -> List[Image]:
        """Convert PDF pages to images using pdf2image"""
        from pdf2image import convert_from_path
        
        images = convert_from_path(
            pdf_path,
            dpi=200,  # Good balance of quality and size
            fmt='PNG'
        )
        return images
```

**Gemini API Call:**
```python
def call_gemini_vision(self, prompt: str, image_data: str) -> str:
    """
    Call Gemini Vision API
    """
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": "image/png",
                        "data": image_data
                    }
                }
            ]
        }],
        "generationConfig": {
            "temperature": 0.1,  # Low for accuracy
            "maxOutputTokens": 8192
        }
    }
    
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()
    
    return result['candidates'][0]['content']['parts'][0]['text']
```

### 4.3. pdfplumber (Formatted PDFs)

**Best for:**
- ✅ PDFs with tables
- ✅ Multi-column layouts
- ✅ Preserves spacing
- ❌ Poor for scanned documents

**Implementation:**
```python
def extract_with_pdfplumber(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text using pdfplumber
    """
    import pdfplumber
    
    pages_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            # Extract text with custom settings
            text = page.extract_text(
                x_tolerance=3,  # Character spacing tolerance
                y_tolerance=3   # Line spacing tolerance
            )
            
            if text:
                pages_text.append((i, text))
    
    return pages_text
```

### 4.4. PyPDF2 (Fallback)

**Best for:**
- ✅ Simple text PDFs
- ✅ Fast extraction
- ❌ Poor for complex layouts
- ❌ Very poor for scanned documents

**Implementation:**
```python
def extract_with_pypdf2(pdf_path: Path) -> List[Tuple[int, str]]:
    """
    Extract text using PyPDF2 (fallback)
    """
    import PyPDF2
    
    pages_text = []
    
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        
        for i, page in enumerate(reader.pages, 1):
            text = page.extract_text()
            
            if text:
                pages_text.append((i, text))
    
    return pages_text
```

### 4.5. Complete Extraction Flow

```python
def extract_text_from_pdf(
    pdf_path: Path,
    use_gemini: bool = True
) -> List[Tuple[int, str]]:
    """
    Complete extraction flow with fallback strategy
    """
    pages_text = []
    
    # Layer 1: Try Gemini (if enabled)
    if use_gemini:
        try:
            log.info("Attempting Gemini Vision API extraction...")
            pages_text = gemini_service.extract_text_from_pdf(pdf_path)
            
            if pages_text:
                log.info(f"✅ Gemini extracted {len(pages_text)} pages")
                return pages_text
            else:
                log.warning("⚠️ Gemini returned no results")
        except Exception as e:
            log.warning(f"⚠️ Gemini failed: {e}")
    
    # Layer 2: Try pdfplumber
    try:
        log.info("Attempting pdfplumber extraction...")
        pages_text = extract_with_pdfplumber(pdf_path)
        
        if pages_text:
            log.info(f"✅ pdfplumber extracted {len(pages_text)} pages")
            return pages_text
        else:
            log.warning("⚠️ pdfplumber returned no results")
    except Exception as e:
        log.warning(f"⚠️ pdfplumber failed: {e}")
    
    # Layer 3: Fallback to PyPDF2
    try:
        log.info("Attempting PyPDF2 extraction...")
        pages_text = extract_with_pypdf2(pdf_path)
        
        if pages_text:
            log.info(f"✅ PyPDF2 extracted {len(pages_text)} pages")
            return pages_text
        else:
            log.error("❌ All extraction methods failed!")
    except Exception as e:
        log.error(f"❌ PyPDF2 failed: {e}")
    
    return []
```

### 4.6. Text Quality Assessment

```python
def assess_text_quality(text: str) -> dict:
    """
    Assess quality of extracted text
    """
    quality = {
        "has_text": bool(text.strip()),
        "length": len(text),
        "word_count": len(text.split()),
        "line_count": len(text.split('\n')),
        "has_gibberish": False,
        "confidence": 0.0
    }
    
    # Check for gibberish (common in poor OCR)
    gibberish_patterns = [
        r'[^\w\s]{5,}',  # Long sequences of special chars
        r'\w{30,}',      # Very long words (likely OCR error)
    ]
    
    for pattern in gibberish_patterns:
        if re.search(pattern, text):
            quality["has_gibberish"] = True
            break
    
    # Calculate confidence score
    if quality["word_count"] > 50 and not quality["has_gibberish"]:
        quality["confidence"] = 0.9
    elif quality["word_count"] > 20:
        quality["confidence"] = 0.6
    else:
        quality["confidence"] = 0.3
    
    return quality
```

---

## 5. PHASE 3: CHUNKING STRATEGY

### 5.1. Why Smart Chunking Matters

**Bad Chunking:**
```
Chunk 1: "...sinh viên cần nộp đơn xin nghỉ học."
Chunk 2: "Điều 5. Quy định về học bổng Sinh viên đạt..."
                    ↑ Missing context!
```

**Good Chunking:**
```
Chunk 1: 
"Điều 4. Quy định về nghỉ học
Sinh viên cần nộp đơn xin nghỉ học kèm giấy tờ..."

Chunk 2:
"Điều 5. Quy định về học bổng
Sinh viên đạt điểm trung bình 3.5 trở lên..."
```

### 5.2. Heading Detection

**Supported Heading Patterns:**

1. **Numbered Headings**
```
1. Khu vực tuyển sinh
7.1. Đối tượng dự tuyển
7.3.1. Thí sinh dự tuyển theo Phương thức 1
```

2. **Roman Numerals**
```
I. Giới thiệu
II. Quy định chung
III. Điều khoản thi hành
```

3. **Letter Headings**
```
A. Phần thứ nhất
B. Phần thứ hai
```

4. **All Caps Headings**
```
CHƯƠNG 1: QUY ĐỊNH CHUNG
ĐIỀU 5: QUY ĐỊNH VỀ NGHỈ HỌC
```

**Regex Patterns:**
```python
heading_patterns = [
    # Level 1: 1. Heading
    r'^\s*(\d+)\.\s+(.+)$',
    
    # Level 2: 7.1. Heading
    r'^\s*(\d+\.\d+)\.\s+(.+)$',
    
    # Level 3: 7.3.1. Heading
    r'^\s*(\d+\.\d+\.\d+)\.\s+(.+)$',
    
    # Level 4: 7.3.1.1. Heading
    r'^\s*(\d+\.\d+\.\d+\.\d+)\.\s+(.+)$',
    
    # Roman: I. Heading
    r'^\s*([IVX]+)\.\s+(.+)$',
    
    # Letter: A. Heading
    r'^\s*([A-Z])\.\s+(.+)$',
    
    # All caps
    r'^([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+)$'
]
```

### 5.3. HeadingChunker Implementation

**Extract Headings:**
```python
def extract_headings(self, text: str) -> List[Dict]:
    """
    Extract all headings from text
    """
    lines = text.split('\n')
    headings = []
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Try each pattern
        for level, pattern in enumerate(self.heading_patterns, 1):
            match = re.match(pattern, line_stripped)
            if match:
                heading_num = match.group(1)
                heading_text = match.group(2)
                
                headings.append({
                    "level": level,
                    "number": heading_num,
                    "text": heading_text,
                    "full_text": line_stripped,
                    "line_index": i,
                    "heading_type": "numbered"
                })
                break
    
    return headings
```

**Create Chunks by Headings:**
```python
def chunk_by_headings(
    self,
    text: str,
    source_file: str,
    page_number: int
) -> List[DocumentChunk]:
    """
    Create chunks based on heading structure
    """
    # Extract headings
    headings = self.extract_headings(text)
    
    if not headings:
        # No headings found, use fixed-size chunking
        return self.fallback_chunking(text, source_file, page_number)
    
    chunks = []
    lines = text.split('\n')
    
    for i, heading in enumerate(headings):
        # Determine content boundaries
        start_line = heading["line_index"]
        
        if i + 1 < len(headings):
            end_line = headings[i + 1]["line_index"]
        else:
            end_line = len(lines)
        
        # Extract content
        content_lines = lines[start_line:end_line]
        content = '\n'.join(content_lines).strip()
        
        # Check size
        if len(content) > self.max_chunk_size:
            # Split large sections
            sub_chunks = self.smart_split(
                content,
                heading["full_text"]
            )
            chunks.extend(sub_chunks)
        else:
            # Create single chunk
            chunk = DocumentChunk(
                source_file=source_file,
                page_number=page_number,
                heading_text=heading["full_text"],
                content=content,
                word_count=len(content.split()),
                char_count=len(content)
            )
            chunks.append(chunk)
    
    return chunks
```

**Smart Splitting for Large Sections:**
```python
def smart_split(
    self,
    content: str,
    heading: str
) -> List[DocumentChunk]:
    """
    Split large section intelligently
    """
    chunks = []
    
    # Try to split by paragraphs
    paragraphs = content.split('\n\n')
    
    current_chunk = heading + '\n\n'
    
    for para in paragraphs:
        # Check if adding paragraph exceeds max size
        if len(current_chunk) + len(para) > self.max_chunk_size:
            # Save current chunk
            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                heading_text=heading,
                # ... other fields
            ))
            
            # Start new chunk with heading (context preservation)
            current_chunk = heading + '\n\n' + para + '\n\n'
        else:
            current_chunk += para + '\n\n'
    
    # Add final chunk
    if current_chunk.strip():
        chunks.append(DocumentChunk(
            content=current_chunk.strip(),
            heading_text=heading,
            # ... other fields
        ))
    
    return chunks
```

### 5.4. Context Preservation

**Overlap Strategy:**
```python
def create_overlapping_chunks(
    chunks: List[DocumentChunk],
    overlap_size: int = 50
) -> List[DocumentChunk]:
    """
    Add overlap between consecutive chunks
    """
    overlapped = []
    
    for i, chunk in enumerate(chunks):
        if i > 0:
            # Add tail of previous chunk
            prev_tail = chunks[i-1].content[-overlap_size:]
            chunk.content = prev_tail + '\n...\n' + chunk.content
        
        if i < len(chunks) - 1:
            # Add head of next chunk
            next_head = chunks[i+1].content[:overlap_size]
            chunk.content = chunk.content + '\n...\n' + next_head
        
        overlapped.append(chunk)
    
    return overlapped
```

**Example with Overlap:**
```
Chunk 1:
"...nghỉ học có phép quá 5 ngày cần xin phép Hiệu trưởng."

Chunk 2 (with overlap):
"...quá 5 ngày cần xin phép Hiệu trưởng.
...
Điều 5. Quy định về học bổng
Sinh viên đạt..."
```

### 5.5. Metadata Enrichment

```python
class DocumentChunk:
    """Enhanced chunk with rich metadata"""
    
    source_file: str          # "QUY_CHE_DAO_TAO.pdf"
    page_number: int          # 5
    heading_text: str         # "Điều 4. Quy định về nghỉ học"
    heading_level: int        # 2 (for 7.1 style)
    content: str              # Actual text content
    word_count: int           # 234
    char_count: int           # 1456
    has_table: bool          # True if contains table
    has_list: bool           # True if contains bullet points
    language: str            # "vi" (Vietnamese)
    keywords: List[str]      # ["nghỉ học", "xin phép", "giấy tờ"]
    section_path: str        # "Chương 2 > Điều 4"
```

### 5.6. Chunking Quality Metrics

```python
def evaluate_chunking_quality(chunks: List[DocumentChunk]) -> dict:
    """
    Evaluate quality of chunking
    """
    metrics = {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(c.char_count for c in chunks) / len(chunks),
        "min_chunk_size": min(c.char_count for c in chunks),
        "max_chunk_size": max(c.char_count for c in chunks),
        "chunks_with_headings": sum(1 for c in chunks if c.heading_text),
        "too_small_chunks": sum(1 for c in chunks if c.char_count < 200),
        "too_large_chunks": sum(1 for c in chunks if c.char_count > 2500),
    }
    
    # Quality score (0-100)
    score = 100
    
    if metrics["too_small_chunks"] > len(chunks) * 0.2:
        score -= 20
    
    if metrics["too_large_chunks"] > len(chunks) * 0.1:
        score -= 15
    
    if metrics["chunks_with_headings"] < len(chunks) * 0.5:
        score -= 10
    
    metrics["quality_score"] = score
    
    return metrics
```

---

## 6. PHASE 4: EMBEDDING GENERATION

### 6.1. Batch Processing

**Why Batch?**
- ✅ 10-100x faster than processing one by one
- ✅ Better GPU utilization
- ✅ Reduced overhead

**Implementation:**
```python
def generate_embeddings_batch(
    chunks: List[DocumentChunk],
    batch_size: int = 32
) -> List[np.ndarray]:
    """
    Generate embeddings in batches
    """
    all_embeddings = []
    
    # Process in batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        texts = [chunk.content for chunk in batch]
        
        log.info(f"Processing batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        # Generate embeddings for batch
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            device='cuda' if torch.cuda.is_available() else 'cpu'
        )
        
        all_embeddings.extend(embeddings)
    
    return all_embeddings
```

### 6.2. Caching Strategy

```python
def generate_embedding_with_cache(text: str) -> np.ndarray:
    """
    Generate embedding with Redis caching
    """
    # Create cache key (hash of text)
    import hashlib
    text_hash = hashlib.md5(text.encode()).hexdigest()
    cache_key = f"embedding:{text_hash}"
    
    # Try to get from cache
    cached = redis_client.get(cache_key)
    if cached:
        log.debug("Cache hit")
        return pickle.loads(cached)
    
    # Generate embedding
    log.debug("Cache miss, generating embedding")
    embedding = model.encode(text)
    
    # Save to cache (7 days TTL)
    redis_client.setex(
        cache_key,
        7 * 24 * 3600,
        pickle.dumps(embedding)
    )
    
    return embedding
```

### 6.3. Progress Tracking

```python
from tqdm import tqdm

def generate_embeddings_with_progress(chunks: List[DocumentChunk]):
    """
    Generate embeddings with progress bar
    """
    embeddings = []
    
    with tqdm(total=len(chunks), desc="Generating embeddings") as pbar:
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_embeddings = model.encode([c.content for c in batch])
            embeddings.extend(batch_embeddings)
            pbar.update(len(batch))
    
    return embeddings
```

---

## 7. PHASE 5: STORAGE & INDEXING

### 7.1. Database Insertion

**Insert Documents:**
```python
def insert_document(
    filename: str,
    file_path: str,
    file_size: int,
    file_hash: str
) -> int:
    """
    Insert document record
    """
    query = """
    INSERT INTO documents (filename, file_path, file_size, file_hash, status)
    VALUES (%s, %s, %s, %s, 'processing')
    RETURNING id
    """
    
    result = session.execute(query, (filename, file_path, file_size, file_hash))
    doc_id = result.fetchone()[0]
    session.commit()
    
    return doc_id
```

**Insert Chunks:**
```python
def insert_chunks(
    document_id: int,
    chunks: List[DocumentChunk]
) -> List[int]:
    """
    Batch insert chunks
    """
    chunk_ids = []
    
    for i, chunk in enumerate(chunks):
        query = """
        INSERT INTO chunks (
            document_id, content, chunk_index,
            heading, metadata, page_number
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        metadata = {
            "word_count": chunk.word_count,
            "char_count": chunk.char_count,
            "source_file": chunk.source_file
        }
        
        result = session.execute(
            query,
            (document_id, chunk.content, i, chunk.heading_text, 
             json.dumps(metadata), chunk.page_number)
        )
        
        chunk_ids.append(result.fetchone()[0])
    
    session.commit()
    return chunk_ids
```

**Insert Embeddings:**
```python
def insert_embeddings(
    chunk_ids: List[int],
    embeddings: List[np.ndarray]
):
    """
    Batch insert embeddings into pgvector
    """
    for chunk_id, embedding in zip(chunk_ids, embeddings):
        # Convert numpy array to list
        embedding_list = embedding.tolist()
        
        # pgvector format
        embedding_str = '[' + ','.join(map(str, embedding_list)) + ']'
        
        query = """
        INSERT INTO embeddings (chunk_id, embedding)
        VALUES (%s, %s::vector)
        ON CONFLICT (chunk_id) DO UPDATE
        SET embedding = EXCLUDED.embedding
        """
        
        session.execute(query, (chunk_id, embedding_str))
    
    session.commit()
```

### 7.2. Index Creation

**Vector Index (IVFFlat):**
```sql
-- Create vector index for fast similarity search
CREATE INDEX IF NOT EXISTS embeddings_embedding_idx 
ON embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- For 10K documents: lists = 100
-- For 100K documents: lists = 1000
-- Rule of thumb: lists = sqrt(num_rows)
```

**BM25 Index Rebuild:**
```python
def rebuild_bm25_index(self):
    """
    Rebuild BM25 index after adding new documents
    """
    log.info("Rebuilding BM25 index...")
    
    # Get all active chunks
    chunks = self.db_service.get_all_chunks(active_only=True)
    
    # Tokenize
    corpus = []
    self.chunk_ids_list = []
    self.chunks_dict = {}
    
    for chunk in chunks:
        tokens = chunk['content'].lower().split()
        corpus.append(tokens)
        
        self.chunk_ids_list.append(chunk['id'])
        self.chunks_dict[chunk['id']] = chunk
    
    # Build BM25
    self.bm25_index = BM25Okapi(corpus)
    
    log.info(f"BM25 index built with {len(corpus)} documents")
```

### 7.3. Transaction Management

```python
def process_document_transactional(pdf_path: Path):
    """
    Process document with transaction rollback on failure
    """
    try:
        # Start transaction
        session.begin()
        
        # Insert document
        doc_id = insert_document(...)
        
        # Process PDF
        chunks = extract_and_chunk(pdf_path)
        
        # Insert chunks
        chunk_ids = insert_chunks(doc_id, chunks)
        
        # Generate embeddings
        embeddings = generate_embeddings(chunks)
        
        # Insert embeddings
        insert_embeddings(chunk_ids, embeddings)
        
        # Update document status
        update_document_status(doc_id, "completed", len(chunks))
        
        # Commit transaction
        session.commit()
        
        log.info(f"✅ Document {doc_id} processed successfully")
        
    except Exception as e:
        # Rollback on error
        session.rollback()
        
        # Mark as failed
        update_document_status(doc_id, "failed", error_message=str(e))
        
        log.error(f"❌ Failed to process document: {e}")
        raise
```

---

## 8. AUTO-INGESTION SERVICE

### 8.1. Watchdog Implementation

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class PDFFileHandler(FileSystemEventHandler):
    """Handle PDF file system events"""
    
    def __init__(self, ingestion_service):
        self.ingestion_service = ingestion_service
    
    def on_created(self, event):
        """Handle new PDF file"""
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith('.pdf'):
            log.info(f"📄 New PDF detected: {event.src_path}")
            
            # Add small delay to ensure file is fully written
            time.sleep(2)
            
            # Process asynchronously
            asyncio.create_task(
                self.ingestion_service.process_pdf(event.src_path)
            )
    
    def on_modified(self, event):
        """Handle PDF modification"""
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith('.pdf'):
            log.info(f"📝 PDF modified: {event.src_path}")
            
            # Reprocess
            asyncio.create_task(
                self.ingestion_service.process_pdf(
                    event.src_path,
                    is_update=True
                )
            )
    
    def on_deleted(self, event):
        """Handle PDF deletion"""
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith('.pdf'):
            filename = Path(event.src_path).name
            log.info(f"🗑️ PDF deleted: {filename}")
            
            # Mark as inactive in database
            self.ingestion_service.mark_document_inactive(filename)
```

### 8.2. Starting the Watcher

```python
class IngestionService:
    def start_watching(self):
        """
        Start watching directory for new PDFs
        """
        # Create observer
        self.observer = Observer()
        
        # Create event handler
        handler = PDFFileHandler(self)
        
        # Schedule watching
        self.observer.schedule(
            handler,
            str(self.watch_dir),
            recursive=False
        )
        
        # Start observer
        self.observer.start()
        
        log.info(f"📡 Watchdog started monitoring: {self.watch_dir}")
    
    def stop_watching(self):
        """Stop watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            log.info("📡 Watchdog stopped")
```

### 8.3. Startup Ingestion

```python
async def ingest_on_startup(self):
    """
    Process existing PDFs on startup
    """
    if not AUTO_INGEST_ON_STARTUP:
        log.info("Auto-ingestion on startup disabled")
        return
    
    log.info("🚀 Running startup ingestion...")
    
    # Find unprocessed PDFs
    existing_pdfs = list(self.watch_dir.glob("*.pdf"))
    
    log.info(f"Found {len(existing_pdfs)} PDFs in watch directory")
    
    # Process each
    for pdf_path in existing_pdfs:
        if pdf_path.name not in self.processed_files:
            log.info(f"Processing: {pdf_path.name}")
            await self.process_pdf(str(pdf_path))
        else:
            log.info(f"Skipping (already processed): {pdf_path.name}")
    
    log.info("✅ Startup ingestion completed")
```

---

## 9. DOCUMENT MANAGEMENT

### 9.1. List Documents

```python
@router.get("/documents")
async def list_documents(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
):
    """
    List all documents with pagination
    """
    query = """
    SELECT id, filename, file_size, total_chunks, status,
           created_at, updated_at
    FROM documents
    WHERE is_active = true
    """
    
    if status:
        query += f" AND status = '{status}'"
    
    query += f" ORDER BY created_at DESC LIMIT {limit} OFFSET {skip}"
    
    documents = db.execute(query).fetchall()
    
    return {
        "documents": documents,
        "total": db.count_documents(),
        "skip": skip,
        "limit": limit
    }
```

### 9.2. Get Document Details

```python
@router.get("/documents/{document_id}")
async def get_document(document_id: int):
    """
    Get document details including chunks
    """
    # Get document
    doc = db.get_document(document_id)
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Get chunks
    chunks = db.get_chunks_by_document(document_id)
    
    # Get statistics
    stats = {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(c['char_count'] for c in chunks) / len(chunks),
        "total_characters": sum(c['char_count'] for c in chunks),
        "chunks_with_headings": sum(1 for c in chunks if c['heading'])
    }
    
    return {
        "document": doc,
        "chunks": chunks,
        "statistics": stats
    }
```

### 9.3. Delete Document

```python
@router.delete("/documents/{document_id}")
async def delete_document(document_id: int, hard_delete: bool = False):
    """
    Delete document (soft or hard)
    """
    if hard_delete:
        # Hard delete: Remove from database
        db.hard_delete_document(document_id)
        message = "Document permanently deleted"
    else:
        # Soft delete: Mark as inactive
        db.soft_delete_document(document_id)
        message = "Document marked as inactive"
    
    # Rebuild BM25 index
    hybrid_retrieval_service.rebuild_bm25_index()
    
    return {"success": True, "message": message}
```

### 9.4. Reprocess Document

```python
@router.post("/documents/{document_id}/reprocess")
async def reprocess_document(
    document_id: int,
    background_tasks: BackgroundTasks
):
    """
    Reprocess document with new chunking strategy
    """
    # Get document
    doc = db.get_document(document_id)
    
    if not doc:
        raise HTTPException(404, "Document not found")
    
    # Check file still exists
    file_path = Path(doc['file_path'])
    if not file_path.exists():
        raise HTTPException(400, "Source file not found")
    
    # Delete old chunks and embeddings
    db.delete_chunks_by_document(document_id)
    
    # Reprocess in background
    background_tasks.add_task(
        process_document_async,
        document_id,
        file_path
    )
    
    return {
        "success": True,
        "message": "Document reprocessing started"
    }
```

---

## 10. MONITORING & TROUBLESHOOTING

### 10.1. Processing Logs

```python
# Example log output during processing

📄 New PDF detected: QUY_CHE_DAO_TAO.pdf
🔄 Processing PDF: QUY_CHE_DAO_TAO.pdf
✅ Validation passed
📖 Extracting text from QUY_CHE_DAO_TAO.pdf...
🤖 Attempting Gemini Vision API extraction...
   ├─ Converting PDF to images...
   ├─ Processing page 1/25 with Gemini...
   ├─ Processing page 2/25 with Gemini...
   └─ ...
✅ Gemini extracted text from 25 pages
✂️ Created 45 chunks from QUY_CHE_DAO_TAO.pdf
   ├─ Chunks with headings: 42
   ├─ Average chunk size: 892 chars
   └─ Quality score: 95/100
🧠 Generating embeddings for 45 chunks...
   ├─ Processing batch 1/2 (32 chunks)
   ├─ Processing batch 2/2 (13 chunks)
   └─ ✅ 45 embeddings generated
💾 Inserting into database...
   ├─ Document ID: 123
   ├─ Chunks inserted: 45
   └─ Embeddings inserted: 45
🔨 Rebuilding BM25 index...
   └─ ✅ Index rebuilt with 1,245 documents
📊 Analytics updated
✅ Successfully processed QUY_CHE_DAO_TAO.pdf
   ├─ Total time: 3m 42s
   ├─ Chunks: 45
   ├─ Size: 2.3 MB
   └─ Moved to: data/processed/QUY_CHE_DAO_TAO.pdf
```

### 10.2. Error Handling

**Common Errors:**

**1. Extraction Failed**
```
❌ Error: All extraction methods failed
Cause: Corrupted PDF, password protected
Solution:
- Check PDF can be opened manually
- Remove password protection
- Try re-downloading PDF
```

**2. Out of Memory**
```
❌ Error: MemoryError during embedding generation
Cause: PDF too large, batch size too high
Solution:
- Reduce batch size: EMBEDDING_BATCH_SIZE=16
- Process in smaller chunks
- Add more RAM or use GPU
```

**3. Gemini API Error**
```
❌ Error: 429 Too Many Requests
Cause: Gemini API quota exceeded
Solution:
- Wait and retry
- Use --no-gemini flag
- Upgrade Gemini API quota
```

**4. Database Error**
```
❌ Error: could not connect to database
Cause: PostgreSQL not running
Solution:
- Check: docker-compose ps postgres
- Restart: docker-compose restart postgres
```

### 10.3. Health Checks

```python
@router.get("/documents/health")
async def documents_health_check():
    """
    Health check for document processing system
    """
    health = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check database
    try:
        db.execute("SELECT 1").fetchone()
        health["checks"]["database"] = "ok"
    except:
        health["checks"]["database"] = "error"
        health["status"] = "degraded"
    
    # Check watch directory
    if PDF_WATCH_DIR.exists():
        health["checks"]["watch_dir"] = "ok"
    else:
        health["checks"]["watch_dir"] = "error"
        health["status"] = "degraded"
    
    # Check Gemini service
    try:
        gemini_service.test_connection()
        health["checks"]["gemini"] = "ok"
    except:
        health["checks"]["gemini"] = "warning"
    
    # Check processing queue
    queue_size = len(ingestion_service.processing_queue)
    health["checks"]["queue_size"] = queue_size
    
    if queue_size > 10:
        health["status"] = "degraded"
    
    return health
```

### 10.4. Performance Metrics

```python
def get_processing_metrics():
    """
    Get document processing performance metrics
    """
    metrics = {
        "total_documents": db.count_documents(),
        "documents_by_status": {
            "completed": db.count_documents_by_status("completed"),
            "processing": db.count_documents_by_status("processing"),
            "failed": db.count_documents_by_status("failed"),
            "pending": db.count_documents_by_status("pending")
        },
        "average_processing_time": db.get_avg_processing_time(),
        "total_chunks": db.count_chunks(),
        "average_chunks_per_document": db.get_avg_chunks_per_document(),
        "storage_used": calculate_storage_used(),
        "cache_hit_rate": calculate_cache_hit_rate()
    }
    
    return metrics
```

---

## APPENDIX

### A. Configuration Parameters

```python
# config/settings.py

# Directories
PDF_DIR = BASE_DIR / "data" / "pdfs"
NEW_PDF_DIR = BASE_DIR / "data" / "new_pdf"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Chunking
CHUNK_SIZE = 1000            # Target chunk size in characters
MIN_CHUNK_SIZE = 250         # Minimum chunk size
MAX_CHUNK_SIZE = 2500        # Maximum chunk size
CHUNK_OVERLAP = 50           # Overlap between chunks

# Embedding
EMBEDDING_MODEL = "keepitreal/vietnamese-sbert"
EMBEDDING_DIMENSION = 384
EMBEDDING_BATCH_SIZE = 32

# Gemini
USE_GEMINI_OCR = True        # Enable Gemini Vision API
GEMINI_API_KEY = "your_key"
GEMINI_MAX_RETRIES = 3

# Processing
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = [".pdf"]
AUTO_INGEST_ON_STARTUP = True
INGESTION_CHECK_INTERVAL = 60  # seconds

# Database
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
POSTGRES_DB = "uni_bot_db"

# Cache
REDIS_HOST = "localhost"
REDIS_PORT = 6379
ENABLE_REDIS_CACHE = True
REDIS_CACHE_TTL = 604800  # 7 days
```

### B. Database Queries

```sql
-- Get processing statistics
SELECT 
    status,
    COUNT(*) as count,
    AVG(total_chunks) as avg_chunks,
    AVG(EXTRACT(EPOCH FROM (processing_completed_at - processing_started_at))) as avg_time_seconds
FROM documents
WHERE processing_started_at IS NOT NULL
GROUP BY status;

-- Find failed documents
SELECT filename, error_message, updated_at
FROM documents
WHERE status = 'failed'
ORDER BY updated_at DESC;

-- Get largest documents
SELECT filename, file_size, total_chunks
FROM documents
ORDER BY file_size DESC
LIMIT 10;

-- Find documents without embeddings
SELECT d.id, d.filename, COUNT(e.id) as embedding_count
FROM documents d
LEFT JOIN chunks c ON d.id = c.document_id
LEFT JOIN embeddings e ON c.id = e.chunk_id
GROUP BY d.id
HAVING COUNT(e.id) = 0;
```

### C. Troubleshooting Checklist

**Before Processing:**
- [ ] PostgreSQL running?
- [ ] Redis running? (optional but recommended)
- [ ] Gemini API key configured?
- [ ] Watch directory exists and writable?
- [ ] Enough disk space?

**During Processing:**
- [ ] Check logs for errors
- [ ] Monitor memory usage
- [ ] Check Gemini API quota
- [ ] Verify PDF can be opened

**After Processing:**
- [ ] Verify chunks created
- [ ] Check embeddings inserted
- [ ] Test retrieval
- [ ] Verify BM25 index rebuilt

---

**Document Version**: 1.0.0  
**Last Updated**: December 2025  
**Author**: University Chatbot Development Team
