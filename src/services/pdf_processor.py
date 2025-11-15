"""
Service for processing PDF files
"""

import json
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List
from src.models.schemas import DocumentChunk
from src.utils.logger import log
from src.utils.heading_chunker import HeadingChunker
from src.services.gemini_pdf_service import GeminiPDFService
from config.settings import PDF_DIR, NEW_PDF_DIR, PROCESSED_DIR


class PDFProcessor:
    """Service for processing PDF files"""

    def __init__(self, use_gemini: bool = True):
        """Initialize PDF processor"""
        self.pdf_dir = PDF_DIR
        self.new_pdf_dir = NEW_PDF_DIR
        self.processed_dir = PROCESSED_DIR
        self.heading_chunker = HeadingChunker()
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
                    all_chunks.extend(chunks)

            log.info(
                f"Created {len(all_chunks)} heading-based chunks from {pdf_path.name}"
            )
            return all_chunks

        except Exception as e:
            log.error(f"Error processing PDF with headings: {e}")
            return []

    def extract_text_from_pdf(
        self, pdf_path: Path, use_gemini: bool = None
    ) -> List[tuple[int, str]]:
        """
        Extract text from each page of a PDF file.
        Uses Gemini Vision API for better OCR, falls back to traditional methods.

        Args:
            pdf_path: Path to PDF file
            use_gemini: Override to force Gemini usage (None uses instance setting)

        Returns:
            A list of tuples, where each tuple contains (page_number, page_text).
        """
        # Determine whether to use Gemini
        should_use_gemini = use_gemini if use_gemini is not None else self.use_gemini

        # Try Gemini first if available and enabled
        if should_use_gemini and self.gemini_service:
            try:
                log.info(
                    f"Attempting to extract text using Gemini Vision API: {pdf_path.name}"
                )
                pages = self.gemini_service.extract_text_from_pdf(pdf_path)
                if pages:
                    log.info(
                        f"Successfully extracted text using Gemini from {len(pages)} pages"
                    )
                    return pages
                else:
                    log.warning(
                        "Gemini extraction returned no results, falling back to traditional methods"
                    )
            except Exception as e:
                log.warning(
                    f"Gemini extraction failed: {e}, falling back to traditional methods"
                )

        # Fallback to traditional PDF text extraction
        pages = []
        try:
            # Try with pdfplumber first (better for formatted text)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text(x_tolerance=3)
                        if page_text:
                            pages.append((i + 1, page_text))
            except Exception as e:
                log.warning(
                    f"Error extracting text with pdfplumber: {e}, falling back to PyPDF2"
                )
                # Fallback to PyPDF2
                with open(pdf_path, "rb") as file:
                    reader = PyPDF2.PdfReader(file)
                    for i, page in enumerate(reader.pages):
                        page_text = page.extract_text()
                        if page_text:
                            pages.append((i + 1, page_text))
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
