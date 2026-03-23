"""
Service for processing PDF files
"""

import json
import os
import re
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import Dict, List, Optional
from src.models.schemas import DocumentChunk
from src.utils.logger import log
from src.utils.heading_chunker import HeadingChunker
from src.services.gemini_pdf_service import GeminiPDFService
from config.settings import (
    PDF_DIR,
    NEW_PDF_DIR,
    PROCESSED_DIR,
    HEADING_CHUNK_MAX_SIZE,
    HEADING_CHUNK_MIN_SIZE,
    HEADING_CHUNK_TARGET_SIZE,
    PDF_OCR_DPI,
    PDF_OCR_LANGUAGES,
    PDF_OCR_MIN_TEXT_CHARS,
)

try:
    import fitz  # PyMuPDF
except Exception:  # pragma: no cover - optional import safety
    fitz = None


class PDFProcessor:
    """Service for processing PDF files"""

    def __init__(self, use_gemini: bool = True):
        """Initialize PDF processor"""
        self.pdf_dir = PDF_DIR
        self.new_pdf_dir = NEW_PDF_DIR
        self.processed_dir = PROCESSED_DIR
        self.heading_chunker = HeadingChunker(
            min_chunk_size=HEADING_CHUNK_MIN_SIZE,
            max_chunk_size=HEADING_CHUNK_MAX_SIZE,
            target_chunk_size=HEADING_CHUNK_TARGET_SIZE,
        )
        self.use_gemini = use_gemini

        # Initialize Gemini service if enabled
        if self.use_gemini:
            try:
                self.gemini_service = GeminiPDFService()
                log.info("Gemini PDF service initialized successfully")
            except Exception as e:
                log.warning(f"Failed to initialize Gemini service: {e}")
                self.gemini_service = None
                self.use_gemini = False
        else:
            self.gemini_service = None

    def process_pdf_with_headings(self, pdf_path: Path) -> List[DocumentChunk]:
        """
        Process a PDF file using heading-based chunking, page by page.

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of document chunks from the entire PDF.
        """
        try:
            log.info(f"Processing PDF with headings: {pdf_path.name}")
            all_chunks = []
            next_chunk_index = 0

            # Extract text page by page
            pages_text = self.extract_text_from_pdf(pdf_path)

            if not pages_text:
                log.warning(f"No text extracted from {pdf_path.name}")
                return []

            # Process each page's text
            for page_number, page_text in pages_text:
                if page_text.strip():
                    # Use heading chunker to create chunks for the current page
                    chunks = self.heading_chunker.chunk_by_headings(
                        page_text, pdf_path.name, page_number
                    )
                    for chunk in chunks:
                        chunk.chunk_index = next_chunk_index
                        next_chunk_index += 1
                    all_chunks.extend(chunks)

            log.info(
                f"Created {len(all_chunks)} heading-based chunks from {pdf_path.name}"
            )
            return all_chunks

        except Exception as e:
            log.error(f"Error processing PDF with headings: {e}")
            return []

    def _normalize_page_text(self, text: Optional[str]) -> str:
        if not text:
            return ""

        raw_lines = [line.rstrip() for line in str(text).splitlines()]
        collapsed_lines = [re.sub(r"\s+", " ", line).strip() for line in raw_lines]

        paragraphs: List[str] = []
        current_paragraph = ""

        for line in collapsed_lines:
            if not line:
                if current_paragraph:
                    paragraphs.append(current_paragraph.strip())
                    current_paragraph = ""
                continue

            if not current_paragraph:
                current_paragraph = line
                continue

            if self._should_merge_lines(current_paragraph, line):
                if current_paragraph.endswith("-"):
                    current_paragraph = f"{current_paragraph[:-1].rstrip()}{line}"
                else:
                    current_paragraph = f"{current_paragraph} {line}"
            else:
                paragraphs.append(current_paragraph.strip())
                current_paragraph = line

        if current_paragraph:
            paragraphs.append(current_paragraph.strip())

        return "\n\n".join(paragraphs).strip()

    def _looks_like_structural_line(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False

        return bool(
            re.match(r"^(\d+(?:\.\d+)*\.?|[a-zA-Z]\)|[-*•])\s+", stripped)
            or stripped.endswith(":")
        )

    def _should_merge_lines(self, current_line: str, next_line: str) -> bool:
        current = current_line.strip()
        upcoming = next_line.strip()
        if not current or not upcoming:
            return False

        if self._looks_like_structural_line(current) or self._looks_like_structural_line(
            upcoming
        ):
            return False

        if current.endswith((".", ";", "?", "!", ":")):
            return False

        return True

    def _text_quality_score(self, text: Optional[str]) -> int:
        normalized = self._normalize_page_text(text)
        if not normalized:
            return 0

        alnum_count = sum(1 for char in normalized if char.isalnum())
        word_count = len(re.findall(r"\w+", normalized, flags=re.UNICODE))
        score = alnum_count + (word_count * 5)
        if self._looks_like_extraction_garbage(normalized):
            return max(1, score // 10)
        return score

    def _looks_like_extraction_garbage(self, text: Optional[str]) -> bool:
        normalized = self._normalize_page_text(text)
        if not normalized:
            return True

        lowered = normalized.lower()
        if "\ufffd" in normalized or "cid:" in lowered or "(cid:" in lowered:
            return True

        words = re.findall(r"\w+", normalized, flags=re.UNICODE)
        if not words:
            return True

        if len(words) >= 6:
            single_char_ratio = sum(1 for word in words if len(word) == 1) / len(words)
            if single_char_ratio >= 0.65:
                return True

        if len(words) >= 4:
            long_token_ratio = sum(1 for word in words if len(word) >= 25) / len(words)
            if long_token_ratio >= 0.5:
                return True

        return False

    def _has_meaningful_text(self, text: Optional[str]) -> bool:
        normalized = self._normalize_page_text(text)
        if not normalized:
            return False

        if self._looks_like_extraction_garbage(normalized):
            return False

        return (
            self._text_quality_score(normalized) >= PDF_OCR_MIN_TEXT_CHARS
            and len(re.findall(r"\w+", normalized, flags=re.UNICODE)) >= 3
        )

    def _merge_page_results(
        self, base_pages: Dict[int, str], candidate_pages: Dict[int, str]
    ) -> Dict[int, str]:
        merged_pages = dict(base_pages)

        for page_number, candidate_text in candidate_pages.items():
            if self._text_quality_score(candidate_text) > self._text_quality_score(
                merged_pages.get(page_number, "")
            ):
                merged_pages[page_number] = self._normalize_page_text(candidate_text)

        return merged_pages

    def _get_page_count(self, pdf_path: Path) -> int:
        if fitz is not None:
            try:
                with fitz.open(str(pdf_path)) as document:
                    return document.page_count
            except Exception as exc:
                log.debug(f"PyMuPDF could not determine page count: {exc}")

        try:
            with open(pdf_path, "rb") as file:
                return len(PyPDF2.PdfReader(file).pages)
        except Exception as exc:
            log.debug(f"PyPDF2 could not determine page count: {exc}")
            return 0

    def _extract_with_pdfplumber(self, pdf_path: Path) -> Dict[int, str]:
        extracted_pages: Dict[int, str] = {}
        with pdfplumber.open(pdf_path) as pdf:
            for page_number, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text(x_tolerance=2, y_tolerance=2)
                if page_text:
                    extracted_pages[page_number] = self._normalize_page_text(page_text)
        return extracted_pages

    def _extract_with_pymupdf_native(
        self, pdf_path: Path, page_numbers: Optional[List[int]] = None
    ) -> Dict[int, str]:
        if fitz is None:
            return {}

        extracted_pages: Dict[int, str] = {}
        selected_pages = set(page_numbers or [])

        with fitz.open(str(pdf_path)) as document:
            for page_index in range(document.page_count):
                page_number = page_index + 1
                if selected_pages and page_number not in selected_pages:
                    continue

                page_text = document.load_page(page_index).get_text("text", sort=True)
                if page_text:
                    extracted_pages[page_number] = self._normalize_page_text(page_text)

        return extracted_pages

    def _extract_with_pypdf2(
        self, pdf_path: Path, page_numbers: Optional[List[int]] = None
    ) -> Dict[int, str]:
        extracted_pages: Dict[int, str] = {}
        selected_pages = set(page_numbers or [])

        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page_index, page in enumerate(reader.pages):
                page_number = page_index + 1
                if selected_pages and page_number not in selected_pages:
                    continue

                page_text = page.extract_text()
                if page_text:
                    extracted_pages[page_number] = self._normalize_page_text(page_text)

        return extracted_pages

    def _resolve_tessdata_path(self) -> Optional[str]:
        configured_path = os.getenv("TESSDATA_PREFIX")
        if configured_path and Path(configured_path).exists():
            return configured_path

        common_paths = (
            "/usr/share/tesseract-ocr/5/tessdata",
            "/usr/share/tesseract-ocr/4.00/tessdata",
            "/usr/share/tessdata",
        )
        for tessdata_path in common_paths:
            if Path(tessdata_path).exists():
                return tessdata_path

        return None

    def _extract_with_pymupdf_ocr(
        self, pdf_path: Path, page_numbers: List[int]
    ) -> Dict[int, str]:
        if fitz is None or not page_numbers:
            return {}

        extracted_pages: Dict[int, str] = {}
        tessdata_path = self._resolve_tessdata_path()

        try:
            with fitz.open(str(pdf_path)) as document:
                for page_number in page_numbers:
                    page = document.load_page(page_number - 1)
                    ocr_kwargs = {
                        "language": PDF_OCR_LANGUAGES,
                        "dpi": PDF_OCR_DPI,
                        "full": True,
                    }
                    if tessdata_path:
                        ocr_kwargs["tessdata"] = tessdata_path

                    textpage = page.get_textpage_ocr(**ocr_kwargs)
                    page_text = page.get_text("text", textpage=textpage)
                    if page_text:
                        extracted_pages[page_number] = self._normalize_page_text(
                            page_text
                        )
        except Exception as exc:
            log.warning(f"PyMuPDF OCR unavailable for {pdf_path.name}: {exc}")
            return {}

        return extracted_pages

    def _pages_needing_ocr(
        self, page_texts: Dict[int, str], total_pages: int
    ) -> List[int]:
        if total_pages > 0:
            candidate_pages = range(1, total_pages + 1)
        else:
            candidate_pages = sorted(page_texts.keys())

        return [
            page_number
            for page_number in candidate_pages
            if not self._has_meaningful_text(page_texts.get(page_number, ""))
        ]

    def extract_text_from_pdf(
        self, pdf_path: Path, use_gemini: bool = None
    ) -> List[tuple[int, str]]:
        """
        Extract text from each page of a PDF file.
        Uses a hybrid strategy: native extraction first, OCR only for low-text pages.

        Args:
            pdf_path: Path to PDF file
            use_gemini: Override to force Gemini usage (None uses instance setting)

        Returns:
            A list of tuples, where each tuple contains (page_number, page_text).
        """
        try:
            should_use_gemini = (
                use_gemini if use_gemini is not None else self.use_gemini
            )
            total_pages = self._get_page_count(pdf_path)
            extracted_pages: Dict[int, str] = {}

            try:
                extracted_pages = self._merge_page_results(
                    extracted_pages, self._extract_with_pdfplumber(pdf_path)
                )
            except Exception as exc:
                log.warning(
                    f"Error extracting text with pdfplumber: {exc}, falling back to other extractors"
                )

            weak_pages = self._pages_needing_ocr(extracted_pages, total_pages)
            if weak_pages:
                try:
                    extracted_pages = self._merge_page_results(
                        extracted_pages,
                        self._extract_with_pymupdf_native(pdf_path, weak_pages),
                    )
                except Exception as exc:
                    log.warning(f"PyMuPDF native extraction failed: {exc}")

            weak_pages = self._pages_needing_ocr(extracted_pages, total_pages)
            if weak_pages:
                try:
                    extracted_pages = self._merge_page_results(
                        extracted_pages, self._extract_with_pypdf2(pdf_path, weak_pages)
                    )
                except Exception as exc:
                    log.warning(f"PyPDF2 extraction failed: {exc}")

            weak_pages = self._pages_needing_ocr(extracted_pages, total_pages)
            if weak_pages:
                log.info(
                    f"Attempting OCR for {len(weak_pages)} low-text page(s) via PyMuPDF: {pdf_path.name}"
                )
                extracted_pages = self._merge_page_results(
                    extracted_pages, self._extract_with_pymupdf_ocr(pdf_path, weak_pages)
                )

            weak_pages = self._pages_needing_ocr(extracted_pages, total_pages)
            if weak_pages and should_use_gemini and self.gemini_service:
                try:
                    log.info(
                        f"Attempting Gemini OCR for {len(weak_pages)} remaining low-text page(s): {pdf_path.name}"
                    )
                    extracted_pages = self._merge_page_results(
                        extracted_pages,
                        dict(
                            self.gemini_service.extract_text_from_pdf(
                                pdf_path, page_numbers=weak_pages
                            )
                        ),
                    )
                except Exception as exc:
                    log.warning(f"Gemini OCR fallback failed: {exc}")

            pages = [
                (page_number, page_text)
                for page_number, page_text in sorted(extracted_pages.items())
                if self._normalize_page_text(page_text)
            ]
            return pages

        except Exception as e:
            log.error(f"Error extracting text from PDF {pdf_path.name}: {e}")
            return []

    def load_heading_chunks_from_file(self) -> List[DocumentChunk]:
        """
        Load heading-based chunks from file

        Returns:
            List of document chunks
        """
        try:
            chunks_file = self.processed_dir / "heading_chunks.json"

            if not chunks_file.exists():
                log.warning(f"Chunks file not found: {chunks_file}")
                return []

            with open(chunks_file, "r", encoding="utf-8") as f:
                chunks_data = json.load(f)

            chunks = [DocumentChunk(**chunk_data) for chunk_data in chunks_data]
            log.info(f"Loaded {len(chunks)} heading-based chunks from {chunks_file}")

            return chunks

        except Exception as e:
            log.error(f"Error loading heading chunks: {e}")
            return []

    def process_all_pdfs(self) -> List[DocumentChunk]:
        """Process all PDFs from both regular and scan directories"""
        all_chunks = []

        # Process regular PDFs (can be copied)
        regular_pdf_files = list(self.pdf_dir.glob("*.pdf"))
        log.info(f"Found {len(regular_pdf_files)} regular PDF files in {self.pdf_dir}")

        for pdf_path in regular_pdf_files:
            log.info(f"Processing regular PDF: {pdf_path.name}")
            chunks = self.process_pdf_with_headings(pdf_path)
            all_chunks.extend(chunks)

        # Process scanned PDFs (use Gemini for better OCR)
        scan_pdf_files = list(self.new_pdf_dir.glob("*.pdf"))
        log.info(f"Found {len(scan_pdf_files)} scanned PDF files in {self.new_pdf_dir}")

        for pdf_path in scan_pdf_files:
            log.info(f"Processing scanned PDF with Gemini: {pdf_path.name}")
            chunks = self.process_pdf_with_headings(pdf_path)
            all_chunks.extend(chunks)

        total_files = len(regular_pdf_files) + len(scan_pdf_files)
        if total_files == 0:
            log.warning(f"No PDF files found in {self.pdf_dir} or {self.new_pdf_dir}")
        else:
            log.info(
                f"Successfully processed {total_files} PDF files, created {len(all_chunks)} chunks"
            )

        return all_chunks

    def process_pdfs_with_gemini_priority(self) -> List[DocumentChunk]:
        """
        Process PDFs with Gemini priority for scanned documents
        Regular PDFs use traditional extraction, scanned PDFs use Gemini
        """
        all_chunks = []

        # Process regular PDFs with traditional methods (faster)
        regular_pdf_files = list(self.pdf_dir.glob("*.pdf"))
        if regular_pdf_files:
            log.info(
                f"Processing {len(regular_pdf_files)} regular PDFs with traditional extraction"
            )
            for pdf_path in regular_pdf_files:
                chunks = self.process_pdf_with_headings(pdf_path)
                all_chunks.extend(chunks)

        # Process scanned PDFs with Gemini (better OCR)
        scan_pdf_files = list(self.new_pdf_dir.glob("*.pdf"))
        if scan_pdf_files:
            log.info(
                f"Processing {len(scan_pdf_files)} scanned PDFs with Gemini Vision API"
            )
            for pdf_path in scan_pdf_files:
                # Force Gemini usage for scanned PDFs
                chunks = self.process_pdf_with_headings(pdf_path)
                all_chunks.extend(chunks)

        return all_chunks

    def save_chunks_to_file(self, chunks: List[DocumentChunk]):
        """Save chunks to a JSON file"""
        if not chunks:
            log.warning("No chunks to save.")
            return

        try:
            # Ensure processed directory exists
            self.processed_dir.mkdir(parents=True, exist_ok=True)

            # Define output file path
            chunks_file = self.processed_dir / "heading_chunks.json"

            # Convert chunks to dictionary format for JSON serialization
            chunks_data = [chunk.dict() for chunk in chunks]

            with open(chunks_file, "w", encoding="utf-8") as f:
                json.dump(chunks_data, f, ensure_ascii=False, indent=4)

            log.info(f"Successfully saved {len(chunks)} chunks to {chunks_file}")

        except Exception as e:
            log.error(f"Error saving chunks to file: {e}")
