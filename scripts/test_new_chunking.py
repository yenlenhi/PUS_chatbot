"""
Script to test the new enhanced chunking strategy
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.services.pdf_processor import PDFProcessor
from src.utils.heading_chunker import HeadingChunker
from config.settings import PDF_DIR, PROCESSED_DIR

def test_single_pdf(pdf_path: Path, output_dir: Path):
    """Test chunking on a single PDF file"""
    print(f"\n{'='*60}")
    print(f"Testing: {pdf_path.name}")
    print(f"{'='*60}")
    
    # Initialize processor and chunker
    pdf_processor = PDFProcessor()
    chunker = HeadingChunker(
        min_chunk_size=100,
        max_chunk_size=2500,
        target_chunk_size=1000
    )
    
    # Extract text
    text = pdf_processor.extract_text_from_pdf(pdf_path)
    if not text:
        print(f"❌ No text extracted from {pdf_path.name}")
        return
    
    print(f"📄 Extracted {len(text)} characters from PDF")
    
    # Create chunks using new strategy
    chunks = chunker.chunk_by_headings(text, pdf_path.name)
    
    if not chunks:
        print(f"❌ No chunks created from {pdf_path.name}")
        return
    
    print(f"✅ Created {len(chunks)} chunks")
    
    # Analyze chunks
    analysis = chunker.analyze_chunks(chunks)
    
    print(f"\n📊 CHUNK ANALYSIS:")
    print(f"   Total chunks: {analysis['total_chunks']}")
    print(f"   Average characters: {analysis['avg_char_count']:.1f}")
    print(f"   Average words: {analysis['avg_word_count']:.1f}")
    print(f"   Size range: {analysis['min_char_count']} - {analysis['max_char_count']} chars")
    
    print(f"\n🏷️ Chunks by type:")
    for chunk_type, count in analysis['chunks_by_type'].items():
        print(f"   {chunk_type}: {count}")
    
    print(f"\n📈 Chunks by heading level:")
    for level, count in analysis['chunks_by_heading_level'].items():
        print(f"   Level {level}: {count}")
    
    if analysis['large_chunks']:
        print(f"\n⚠️ Large chunks ({len(analysis['large_chunks'])}):")
        for chunk_info in analysis['large_chunks'][:5]:
            print(f"   #{chunk_info['chunk_index']}: {chunk_info['char_count']} chars - {chunk_info['heading']}")
    
    if analysis['small_chunks']:
        print(f"\n⚠️ Small chunks ({len(analysis['small_chunks'])}):")
        for chunk_info in analysis['small_chunks'][:5]:
            print(f"   #{chunk_info['chunk_index']}: {chunk_info['char_count']} chars - {chunk_info['heading']}")
    
    # Show sample chunks
    print(f"\n📝 SAMPLE CHUNKS:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ---")
        print(f"Type: {chunk.chunk_type}")
        print(f"Heading: {chunk.heading_text or 'None'}")
        print(f"Level: {chunk.heading_level or 'N/A'}")
        print(f"Number: {chunk.heading_number or 'N/A'}")
        print(f"Parent: {chunk.parent_heading or 'N/A'}")
        print(f"Sub-chunk: {chunk.is_sub_chunk} ({chunk.sub_chunk_index}/{chunk.total_sub_chunks})")
        print(f"Size: {chunk.char_count or len(chunk.content)} chars, {chunk.word_count or len(chunk.content.split())} words")
        print(f"Content preview: {chunk.content[:200]}...")
    
    # Save chunks for inspection
    output_file = output_dir / f"test_chunks_{pdf_path.stem}.json"
    chunks_data = [chunk.dict() for chunk in chunks]
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(chunks_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Chunks saved to: {output_file}")
    
    return chunks, analysis

def compare_with_old_chunking(pdf_path: Path):
    """Compare new chunking with old chunking"""
    print(f"\n🔄 COMPARISON WITH OLD CHUNKING:")
    
    # Load old chunks if available
    old_chunks_file = PROCESSED_DIR / "heading_chunks.json"
    if old_chunks_file.exists():
        with open(old_chunks_file, 'r', encoding='utf-8') as f:
            old_chunks_data = json.load(f)
        
        # Filter chunks from this PDF
        old_chunks = [chunk for chunk in old_chunks_data if chunk['source_file'] == pdf_path.name]
        
        if old_chunks:
            print(f"   Old chunking: {len(old_chunks)} chunks")
            old_char_counts = [len(chunk['content']) for chunk in old_chunks]
            print(f"   Old avg size: {sum(old_char_counts) / len(old_char_counts):.1f} chars")
            print(f"   Old size range: {min(old_char_counts)} - {max(old_char_counts)} chars")
        else:
            print(f"   No old chunks found for {pdf_path.name}")
    else:
        print(f"   Old chunks file not found")

def main():
    """Main testing function"""
    print("🧪 TESTING NEW ENHANCED CHUNKING STRATEGY")
    print("="*60)
    
    # Create output directory
    output_dir = PROCESSED_DIR / "test_chunks"
    output_dir.mkdir(exist_ok=True)
    
    # Get PDF files
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    
    if not pdf_files:
        print(f"❌ No PDF files found in {PDF_DIR}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files")
    
    all_chunks = []
    all_analyses = []
    
    # Test each PDF
    for pdf_file in pdf_files:
        try:
            chunks, analysis = test_single_pdf(pdf_file, output_dir)
            all_chunks.extend(chunks)
            all_analyses.append(analysis)
            
            # Compare with old chunking
            compare_with_old_chunking(pdf_file)
            
        except Exception as e:
            print(f"❌ Error processing {pdf_file.name}: {e}")
            log.error(f"Error in test_single_pdf: {e}")
    
    # Overall summary
    if all_chunks:
        print(f"\n{'='*60}")
        print(f"OVERALL SUMMARY")
        print(f"{'='*60}")
        
        total_chunks = len(all_chunks)
        total_chars = sum(chunk.char_count or len(chunk.content) for chunk in all_chunks)
        total_words = sum(chunk.word_count or len(chunk.content.split()) for chunk in all_chunks)
        
        print(f"📊 Total chunks across all PDFs: {total_chunks}")
        print(f"📊 Total characters: {total_chars:,}")
        print(f"📊 Total words: {total_words:,}")
        print(f"📊 Average chunk size: {total_chars / total_chunks:.1f} chars")
        print(f"📊 Average words per chunk: {total_words / total_chunks:.1f}")
        
        # Size distribution
        char_counts = [chunk.char_count or len(chunk.content) for chunk in all_chunks]
        size_dist = {
            'very_small': len([c for c in char_counts if c < 100]),
            'small': len([c for c in char_counts if 100 <= c < 500]),
            'medium': len([c for c in char_counts if 500 <= c < 1500]),
            'large': len([c for c in char_counts if 1500 <= c < 3000]),
            'very_large': len([c for c in char_counts if c >= 3000])
        }
        
        print(f"\n📈 Size distribution:")
        for size_cat, count in size_dist.items():
            percentage = count / total_chunks * 100
            print(f"   {size_cat}: {count} ({percentage:.1f}%)")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if size_dist['very_large'] > total_chunks * 0.1:
            print(f"   ⚠️ {size_dist['very_large']} chunks are very large (≥3000 chars)")
            print(f"      Consider reducing max_chunk_size or improving splitting logic")
        
        if size_dist['very_small'] > total_chunks * 0.2:
            print(f"   ⚠️ {size_dist['very_small']} chunks are very small (<100 chars)")
            print(f"      Consider merging small chunks or adjusting min_chunk_size")
        
        optimal_chunks = size_dist['medium'] + size_dist['large']
        if optimal_chunks / total_chunks >= 0.7:
            print(f"   ✅ {optimal_chunks} chunks ({optimal_chunks/total_chunks*100:.1f}%) are in optimal size range")
        else:
            print(f"   ⚠️ Only {optimal_chunks} chunks ({optimal_chunks/total_chunks*100:.1f}%) are in optimal size range")
        
        # Save overall results
        summary_file = output_dir / "chunking_test_summary.json"
        summary = {
            'total_chunks': total_chunks,
            'total_characters': total_chars,
            'total_words': total_words,
            'average_chunk_size': total_chars / total_chunks,
            'size_distribution': size_dist,
            'analyses': all_analyses
        }
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Summary saved to: {summary_file}")

if __name__ == "__main__":
    main()
