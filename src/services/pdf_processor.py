"""
Service for processing PDF files
"""
import json
import PyPDF2
import pdfplumber
from pathlib import Path
from typing import List, Optional
from src.models.schemas import DocumentChunk
from src.utils.logger import log
from src.utils.heading_chunker import HeadingChunker
from config.settings import PDF_DIR, PROCESSED_DIR

class PDFProcessor:
    """Service for processing PDF files"""
    
    def __init__(self):
        """Initialize PDF processor"""
        self.pdf_dir = PDF_DIR
        self.processed_dir = PROCESSED_DIR
        self.heading_chunker = HeadingChunker()
        
    def process_pdf_with_headings(self, pdf_path: Path) -> List[DocumentChunk]:
        """
        Process a PDF file using heading-based chunking
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of document chunks
        """
        try:
            log.info(f"Processing PDF with headings: {pdf_path.name}")
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text:
                log.warning(f"No text extracted from {pdf_path.name}")
                return []
            
            # Use heading chunker to create chunks
            chunks = self.heading_chunker.chunk_by_headings(text, pdf_path.name)
            
            log.info(f"Created {len(chunks)} heading-based chunks from {pdf_path.name}")
            return chunks
            
        except Exception as e:
            log.error(f"Error processing PDF with headings: {e}")
            return []
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Extracted text
        """
        try:
            text = ""
            
            # Try with pdfplumber first (better for formatted text)
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text(x_tolerance=3)
                        if page_text:
                            text += page_text + "\n\n"
            except Exception as e:
                log.warning(f"Error extracting text with pdfplumber: {e}")
                
                # Fallback to PyPDF2
                with open(pdf_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            log.error(f"Error extracting text from PDF: {e}")
            return ""
    
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
            
            with open(chunks_file, 'r', encoding='utf-8') as f:
                chunks_data = json.load(f)
            
            chunks = [DocumentChunk(**chunk_data) for chunk_data in chunks_data]
            log.info(f"Loaded {len(chunks)} heading-based chunks from {chunks_file}")
            
            return chunks
            
        except Exception as e:
            log.error(f"Error loading heading chunks: {e}")
            return []
    
    # Existing methods from the original PDFProcessor
    def process_all_pdfs(self):
        """Process all PDFs in the PDF directory"""
        # Existing implementation...
        pass
    
    def process_pdf_to_chunks(self, pdf_path):
        """Process a PDF file to chunks"""
        # Existing implementation...
        pass
    
    def save_chunks_to_file(self, chunks):
        """Save chunks to file"""
        # Existing implementation...
        pass
    
    def load_chunks_from_file(self):
        """Load chunks from file"""
        # Existing implementation...
        pass



