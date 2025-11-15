"""
Test script for Gemini PDF processing functionality
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.gemini_pdf_service import GeminiPDFService
from src.services.pdf_processor import PDFProcessor
from src.utils.logger import log
from config.settings import PDF_DIR, NEW_PDF_DIR, GEMINI_API_KEY


def test_gemini_api_connection():
    """Test if Gemini API is properly configured and accessible"""
    log.info("Testing Gemini API connection...")
    
    if not GEMINI_API_KEY:
        log.error("GEMINI_API_KEY is not set in environment variables")
        return False
    
    try:
        gemini_service = GeminiPDFService()
        log.info("✓ Gemini PDF service initialized successfully")
        return True
    except Exception as e:
        log.error(f"✗ Failed to initialize Gemini service: {e}")
        return False


def test_pdf_directories():
    """Test if PDF directories exist and contain files"""
    log.info("Checking PDF directories...")
    
    # Check regular PDF directory
    regular_pdfs = list(PDF_DIR.glob("*.pdf"))
    log.info(f"Regular PDFs in {PDF_DIR}: {len(regular_pdfs)} files")
    for pdf in regular_pdfs[:3]:  # Show first 3
        log.info(f"  - {pdf.name}")
    
    # Check scanned PDF directory
    scan_pdfs = list(NEW_PDF_DIR.glob("*.pdf"))
    log.info(f"Scanned PDFs in {NEW_PDF_DIR}: {len(scan_pdfs)} files")
    for pdf in scan_pdfs[:3]:  # Show first 3
        log.info(f"  - {pdf.name}")
    
    return len(regular_pdfs) > 0 or len(scan_pdfs) > 0


def test_single_pdf_extraction(pdf_path: Path, use_gemini: bool = True):
    """Test text extraction from a single PDF"""
    log.info(f"Testing text extraction from: {pdf_path.name}")
    log.info(f"Using Gemini: {use_gemini}")
    
    try:
        processor = PDFProcessor(use_gemini=use_gemini)
        pages = processor.extract_text_from_pdf(pdf_path, use_gemini=use_gemini)
        
        if pages:
            log.info(f"✓ Successfully extracted text from {len(pages)} pages")
            
            # Show sample from first page
            if pages:
                page_num, text = pages[0]
                preview = text[:200] + "..." if len(text) > 200 else text
                log.info(f"Sample from page {page_num}: {preview}")
            
            return True
        else:
            log.warning("✗ No text extracted")
            return False
            
    except Exception as e:
        log.error(f"✗ Error extracting text: {e}")
        return False


def test_chunk_creation():
    """Test the complete chunk creation process"""
    log.info("Testing complete chunk creation process...")
    
    try:
        processor = PDFProcessor(use_gemini=True)
        
        # Test with a small subset first
        regular_pdfs = list(PDF_DIR.glob("*.pdf"))
        scan_pdfs = list(NEW_PDF_DIR.glob("*.pdf"))
        
        test_files = []
        if regular_pdfs:
            test_files.append(regular_pdfs[0])  # First regular PDF
        if scan_pdfs:
            test_files.append(scan_pdfs[0])     # First scanned PDF
        
        if not test_files:
            log.warning("No PDF files found for testing")
            return False
        
        all_chunks = []
        for pdf_path in test_files:
            log.info(f"Processing: {pdf_path.name}")
            chunks = processor.process_pdf_with_headings(pdf_path)
            all_chunks.extend(chunks)
            log.info(f"Created {len(chunks)} chunks from {pdf_path.name}")
        
        if all_chunks:
            log.info(f"✓ Total chunks created: {len(all_chunks)}")
            
            # Show sample chunk
            sample_chunk = all_chunks[0]
            log.info("Sample chunk:")
            log.info(f"  Source: {sample_chunk.source_file}")
            log.info(f"  Page: {sample_chunk.page_number}")
            log.info(f"  Heading: {sample_chunk.heading_text}")
            log.info(f"  Content: {sample_chunk.content[:150]}...")
            
            return True
        else:
            log.warning("✗ No chunks created")
            return False
            
    except Exception as e:
        log.error(f"✗ Error in chunk creation: {e}")
        return False


def main():
    """Run all tests"""
    log.info("=== Starting Gemini PDF Processing Tests ===")
    
    results = {}
    
    # Test 1: API Connection
    results['api_connection'] = test_gemini_api_connection()
    
    # Test 2: PDF Directories
    results['pdf_directories'] = test_pdf_directories()
    
    if not results['pdf_directories']:
        log.error("No PDF files found. Please add PDF files to test directories.")
        return
    
    # Test 3: Single PDF extraction (traditional)
    regular_pdfs = list(PDF_DIR.glob("*.pdf"))
    if regular_pdfs:
        log.info("\n--- Testing Traditional PDF Extraction ---")
        results['traditional_extraction'] = test_single_pdf_extraction(
            regular_pdfs[0], use_gemini=False
        )
    
    # Test 4: Single PDF extraction (Gemini)
    if results['api_connection']:
        scan_pdfs = list(NEW_PDF_DIR.glob("*.pdf"))
        if scan_pdfs:
            log.info("\n--- Testing Gemini PDF Extraction ---")
            results['gemini_extraction'] = test_single_pdf_extraction(
                scan_pdfs[0], use_gemini=True
            )
        else:
            log.info("No scanned PDFs found, testing Gemini with regular PDF")
            if regular_pdfs:
                results['gemini_extraction'] = test_single_pdf_extraction(
                    regular_pdfs[0], use_gemini=True
                )
    
    # Test 5: Complete chunk creation
    if results['api_connection']:
        log.info("\n--- Testing Complete Chunk Creation ---")
        results['chunk_creation'] = test_chunk_creation()
    
    # Summary
    log.info("\n=== Test Results Summary ===")
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        log.info(f"{test_name}: {status}")
    
    # Recommendations
    log.info("\n=== Recommendations ===")
    if not results.get('api_connection'):
        log.info("- Set GEMINI_API_KEY environment variable")
        log.info("- Verify Gemini API access and quota")
    
    if results.get('api_connection') and results.get('pdf_directories'):
        log.info("- System is ready for full PDF processing")
        log.info("- Run: python scripts/process_pdfs.py --gemini-priority")
    
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    log.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")


if __name__ == "__main__":
    main()
