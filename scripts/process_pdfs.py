"""
Script to process PDF files and create chunks using Gemini for enhanced OCR
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.services.pdf_processor import PDFProcessor
from src.utils.logger import log


def main():
    """Main function to process PDFs with Gemini integration"""
    parser = argparse.ArgumentParser(
        description="Process PDF files with Gemini OCR support"
    )
    parser.add_argument(
        "--use-gemini",
        action="store_true",
        default=True,
        help="Use Gemini Vision API for text extraction (default: True)",
    )
    parser.add_argument(
        "--no-gemini",
        action="store_true",
        help="Disable Gemini and use traditional PDF extraction only",
    )
    parser.add_argument(
        "--gemini-priority",
        action="store_true",
        help="Use Gemini primarily for scanned PDFs, traditional methods for regular PDFs",
    )

    args = parser.parse_args()

    # Determine Gemini usage
    use_gemini = args.use_gemini and not args.no_gemini

    log.info("Starting enhanced PDF processing with Gemini integration...")
    log.info(f"Gemini Vision API enabled: {use_gemini}")

    try:
        # Initialize PDF processor with Gemini support
        processor = PDFProcessor(use_gemini=use_gemini)

        # Choose processing method
        if args.gemini_priority:
            log.info(
                "Using Gemini priority mode (Gemini for scanned PDFs, traditional for regular PDFs)"
            )
            chunks = processor.process_pdfs_with_gemini_priority()
        else:
            log.info("Processing all PDFs with unified approach")
            chunks = processor.process_all_pdfs()

        if not chunks:
            log.error(
                "No chunks were created. Please check your PDF files and Gemini API configuration."
            )
            return

        # Save chunks to file
        processor.save_chunks_to_file(chunks)

        # Print detailed summary
        log.info("=== PDF Processing Completed Successfully! ===")
        log.info(f"Total chunks created: {len(chunks)}")

        # Analyze chunks by source
        source_stats = {}
        for chunk in chunks:
            source = chunk.source_file
            if source not in source_stats:
                source_stats[source] = 0
            source_stats[source] += 1

        log.info("Chunks by source file:")
        for source, count in source_stats.items():
            log.info(f"  {source}: {count} chunks")

        # Show sample chunks
        log.info("\nSample chunks:")
        for i, chunk in enumerate(chunks[:3]):
            log.info(f"Chunk {i+1}:")
            log.info(f"  Source: {chunk.source_file}")
            log.info(f"  Page: {chunk.page_number}")
            log.info(f"  Heading: {chunk.heading_text or 'N/A'}")
            log.info(f"  Word count: {chunk.word_count}")
            log.info(f"  Content preview: {chunk.content[:150]}...")
            log.info("---")

        log.info(
            f"\nProcessed chunks saved to: {processor.processed_dir / 'heading_chunks.json'}"
        )
        log.info(
            "Ready for embedding generation! Run: python scripts/build_embeddings.py"
        )

    except Exception as e:
        log.error(f"Error during PDF processing: {e}")
        raise


if __name__ == "__main__":
    main()
