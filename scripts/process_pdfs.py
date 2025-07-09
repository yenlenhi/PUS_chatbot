"""
Script to process PDF files and create chunks
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.pdf_processor import PDFProcessor
from src.utils.logger import log


def main():
    """Main function to process PDFs"""
    log.info("Starting PDF processing...")
    
    # Initialize PDF processor
    processor = PDFProcessor()
    
    # Process all PDFs
    chunks = processor.process_all_pdfs()
    
    if not chunks:
        log.error("No chunks were created. Please check your PDF files.")
        return
    
    # Save chunks to file
    processor.save_chunks_to_file(chunks)
    
    # Print summary
    log.info("PDF processing completed!")
    log.info(f"Total chunks created: {len(chunks)}")
    
    # Show sample chunks
    log.info("Sample chunks:")
    for i, chunk in enumerate(chunks[:3]):
        log.info(f"Chunk {i+1}:")
        log.info(f"  Source: {chunk.source_file}")
        log.info(f"  Page: {chunk.page_number}")
        log.info(f"  Content preview: {chunk.content[:100]}...")
        log.info("---")


if __name__ == "__main__":
    main()
