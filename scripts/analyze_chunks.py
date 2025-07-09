"""
Script to analyze chunk quality and provide detailed statistics
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
# import matplotlib.pyplot as plt
# import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from src.models.schemas import DocumentChunk
from src.utils.heading_chunker import HeadingChunker
from config.settings import PROCESSED_DIR

def load_chunks() -> List[DocumentChunk]:
    """Load chunks from the processed file"""
    chunks_file = PROCESSED_DIR / "heading_chunks.json"
    
    if not chunks_file.exists():
        log.error(f"Chunks file not found: {chunks_file}")
        return []
    
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks_data = json.load(f)
    
    chunks = [DocumentChunk(**chunk_data) for chunk_data in chunks_data]
    log.info(f"Loaded {len(chunks)} chunks for analysis")
    
    return chunks

def analyze_chunk_distribution(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """Analyze the distribution of chunk sizes and characteristics"""
    if not chunks:
        return {}
    
    # Calculate basic statistics
    char_counts = []
    word_counts = []
    
    for chunk in chunks:
        char_count = chunk.char_count if chunk.char_count else len(chunk.content)
        word_count = chunk.word_count if chunk.word_count else len(chunk.content.split())
        
        char_counts.append(char_count)
        word_counts.append(word_count)
    
    analysis = {
        'total_chunks': len(chunks),
        'character_stats': {
            'total': sum(char_counts),
            'mean': sum(char_counts) / len(char_counts),
            'min': min(char_counts),
            'max': max(char_counts),
            'median': sorted(char_counts)[len(char_counts) // 2]
        },
        'word_stats': {
            'total': sum(word_counts),
            'mean': sum(word_counts) / len(word_counts),
            'min': min(word_counts),
            'max': max(word_counts),
            'median': sorted(word_counts)[len(word_counts) // 2]
        },
        'size_distribution': {
            'very_small': len([c for c in char_counts if c < 100]),
            'small': len([c for c in char_counts if 100 <= c < 500]),
            'medium': len([c for c in char_counts if 500 <= c < 1500]),
            'large': len([c for c in char_counts if 1500 <= c < 3000]),
            'very_large': len([c for c in char_counts if c >= 3000])
        },
        'chunks_by_source': {},
        'chunks_by_type': {},
        'problematic_chunks': []
    }
    
    # Analyze by source file and type
    for i, chunk in enumerate(chunks):
        source = chunk.source_file
        analysis['chunks_by_source'][source] = analysis['chunks_by_source'].get(source, 0) + 1
        
        chunk_type = getattr(chunk, 'chunk_type', 'unknown')
        analysis['chunks_by_type'][chunk_type] = analysis['chunks_by_type'].get(chunk_type, 0) + 1
        
        # Identify problematic chunks
        char_count = char_counts[i]
        if char_count > 3000:
            analysis['problematic_chunks'].append({
                'index': i,
                'chunk_index': chunk.chunk_index,
                'source_file': chunk.source_file,
                'char_count': char_count,
                'word_count': word_counts[i],
                'heading': getattr(chunk, 'heading_text', 'No heading'),
                'issue': 'Too large for optimal RAG performance'
            })
        elif char_count < 50:
            analysis['problematic_chunks'].append({
                'index': i,
                'chunk_index': chunk.chunk_index,
                'source_file': chunk.source_file,
                'char_count': char_count,
                'word_count': word_counts[i],
                'heading': getattr(chunk, 'heading_text', 'No heading'),
                'issue': 'Very small, might lack context'
            })
    
    return analysis

def print_analysis_report(analysis: Dict[str, Any]):
    """Print a detailed analysis report"""
    print("\n" + "="*80)
    print("CHUNK ANALYSIS REPORT")
    print("="*80)
    
    print(f"\n📊 OVERVIEW:")
    print(f"   Total chunks: {analysis['total_chunks']}")
    print(f"   Total characters: {analysis['character_stats']['total']:,}")
    print(f"   Total words: {analysis['word_stats']['total']:,}")
    
    print(f"\n📏 CHARACTER STATISTICS:")
    char_stats = analysis['character_stats']
    print(f"   Mean: {char_stats['mean']:.1f} chars")
    print(f"   Median: {char_stats['median']} chars")
    print(f"   Range: {char_stats['min']} - {char_stats['max']} chars")
    
    print(f"\n📝 WORD STATISTICS:")
    word_stats = analysis['word_stats']
    print(f"   Mean: {word_stats['mean']:.1f} words")
    print(f"   Median: {word_stats['median']} words")
    print(f"   Range: {word_stats['min']} - {word_stats['max']} words")
    
    print(f"\n📈 SIZE DISTRIBUTION:")
    dist = analysis['size_distribution']
    total = analysis['total_chunks']
    print(f"   Very Small (<100 chars): {dist['very_small']} ({dist['very_small']/total*100:.1f}%)")
    print(f"   Small (100-499 chars): {dist['small']} ({dist['small']/total*100:.1f}%)")
    print(f"   Medium (500-1499 chars): {dist['medium']} ({dist['medium']/total*100:.1f}%)")
    print(f"   Large (1500-2999 chars): {dist['large']} ({dist['large']/total*100:.1f}%)")
    print(f"   Very Large (≥3000 chars): {dist['very_large']} ({dist['very_large']/total*100:.1f}%)")
    
    print(f"\n📁 BY SOURCE FILE:")
    for source, count in analysis['chunks_by_source'].items():
        print(f"   {source}: {count} chunks ({count/total*100:.1f}%)")
    
    print(f"\n🏷️ BY CHUNK TYPE:")
    for chunk_type, count in analysis['chunks_by_type'].items():
        print(f"   {chunk_type}: {count} chunks ({count/total*100:.1f}%)")
    
    if analysis['problematic_chunks']:
        print(f"\n⚠️ PROBLEMATIC CHUNKS ({len(analysis['problematic_chunks'])}):")
        for chunk in analysis['problematic_chunks'][:10]:  # Show first 10
            print(f"   #{chunk['chunk_index']} ({chunk['source_file']}): {chunk['char_count']} chars")
            print(f"      Heading: {chunk['heading']}")
            print(f"      Issue: {chunk['issue']}")
            print()
        
        if len(analysis['problematic_chunks']) > 10:
            print(f"   ... and {len(analysis['problematic_chunks']) - 10} more")
    
    print("\n" + "="*80)

def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """Generate recommendations based on analysis"""
    recommendations = []
    
    char_stats = analysis['character_stats']
    dist = analysis['size_distribution']
    total = analysis['total_chunks']
    
    # Check average size
    if char_stats['mean'] > 2000:
        recommendations.append("📏 Average chunk size is quite large. Consider reducing target_chunk_size.")
    elif char_stats['mean'] < 300:
        recommendations.append("📏 Average chunk size is small. Consider increasing min_chunk_size.")
    
    # Check distribution
    if dist['very_large'] / total > 0.1:
        recommendations.append("📈 Too many very large chunks (>3000 chars). Improve splitting logic.")
    
    if dist['very_small'] / total > 0.2:
        recommendations.append("📈 Many very small chunks. Consider merging or improving content detection.")
    
    # Check for optimal RAG distribution
    optimal_range = dist['medium'] + dist['large']
    if optimal_range / total < 0.6:
        recommendations.append("🎯 Less than 60% of chunks are in optimal size range (500-3000 chars).")
    
    # Check problematic chunks
    if len(analysis['problematic_chunks']) > total * 0.1:
        recommendations.append("⚠️ More than 10% of chunks have issues. Review chunking strategy.")
    
    if not recommendations:
        recommendations.append("✅ Chunk distribution looks good for RAG performance!")
    
    return recommendations

def main():
    """Main analysis function"""
    print("Starting chunk analysis...")
    
    # Load chunks
    chunks = load_chunks()
    
    if not chunks:
        print("No chunks found to analyze.")
        return
    
    # Perform analysis
    analysis = analyze_chunk_distribution(chunks)
    
    # Print report
    print_analysis_report(analysis)
    
    # Generate recommendations
    recommendations = generate_recommendations(analysis)
    print("\n🎯 RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Save analysis to file
    output_file = PROCESSED_DIR / "chunk_analysis.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")

if __name__ == "__main__":
    main()
