"""
Text processing utilities
"""
import re
from typing import List
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.vietnamese_text_formatter import format_vietnamese_text


def clean_text(text: str) -> str:
    """
    Clean and normalize text with Vietnamese formatting

    Args:
        text: Raw text to clean

    Returns:
        Cleaned and formatted text
    """
    # Replace multiple spaces/tabs with single space, but preserve newlines
    text = re.sub(r'[ \t]+', ' ', text)

    # Remove special characters but keep Vietnamese characters
    text = re.sub(r'[^\w\s\u00C0-\u024F\u1E00-\u1EFF.,!?;:()\-]', '', text)

    # Remove multiple punctuation
    text = re.sub(r'[.,!?;:]{2,}', '.', text)

    # Apply Vietnamese text formatting
    text = format_vietnamese_text(text)

    # Strip and return
    return text.strip()


def split_text_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to split
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # If this is not the last chunk, try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings within the last 100 characters
            sentence_end = text.rfind('.', start + chunk_size - 100, end)
            if sentence_end != -1 and sentence_end > start:
                end = sentence_end + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from text (simple implementation)
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction based on word frequency
    # Remove common Vietnamese stop words
    stop_words = {
        'và', 'của', 'có', 'là', 'được', 'trong', 'với', 'để', 'cho', 'từ',
        'về', 'theo', 'như', 'khi', 'nếu', 'sẽ', 'đã', 'đang', 'các', 'những',
        'này', 'đó', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín', 'mười'
    }
    
    # Extract words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [word for word in words if len(word) > 2 and word not in stop_words]
    
    # Count frequency
    word_freq = {}
    for word in keywords:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, freq in sorted_keywords[:max_keywords]]
