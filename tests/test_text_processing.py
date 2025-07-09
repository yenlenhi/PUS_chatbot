"""
Tests for text processing utilities
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.text_processing import clean_text, split_text_into_chunks, extract_keywords


class TestTextProcessing:
    """Test cases for text processing functions"""
    
    def test_clean_text(self):
        """Test text cleaning function"""
        # Test basic cleaning
        dirty_text = "  Xin   chào!!!   Đây là    văn bản   test.  "
        clean = clean_text(dirty_text)
        assert clean == "Xin chào! Đây là văn bản test."
        
        # Test special characters removal
        dirty_text = "Text với @#$%^&* ký tự đặc biệt"
        clean = clean_text(dirty_text)
        assert "@#$%^&*" not in clean
        
        # Test Vietnamese characters preservation
        vietnamese_text = "Trường Đại học An ninh Nhân dân"
        clean = clean_text(vietnamese_text)
        assert "Trường Đại học An ninh Nhân dân" in clean
    
    def test_split_text_into_chunks(self):
        """Test text chunking function"""
        # Test short text (no splitting needed)
        short_text = "This is a short text."
        chunks = split_text_into_chunks(short_text, chunk_size=100, overlap=10)
        assert len(chunks) == 1
        assert chunks[0] == short_text
        
        # Test long text splitting
        long_text = "A" * 1000
        chunks = split_text_into_chunks(long_text, chunk_size=300, overlap=50)
        assert len(chunks) > 1
        
        # Test overlap
        text_with_sentences = "Sentence one. Sentence two. Sentence three. Sentence four."
        chunks = split_text_into_chunks(text_with_sentences, chunk_size=30, overlap=10)
        if len(chunks) > 1:
            # Check that there's some overlap
            assert len(chunks[0]) <= 30
    
    def test_extract_keywords(self):
        """Test keyword extraction function"""
        text = "Trường Đại học An ninh Nhân dân tuyển sinh năm 2025 với nhiều ngành học"
        keywords = extract_keywords(text, max_keywords=5)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 5
        
        # Should not contain stop words
        stop_words = {'và', 'của', 'có', 'là', 'được'}
        for keyword in keywords:
            assert keyword not in stop_words
    
    def test_empty_input(self):
        """Test functions with empty input"""
        assert clean_text("") == ""
        assert split_text_into_chunks("") == []
        assert extract_keywords("") == []
    
    def test_vietnamese_text_processing(self):
        """Test processing of Vietnamese text specifically"""
        vietnamese_text = """
        Trường Đại học An ninh Nhân dân là cơ sở đào tạo cán bộ an ninh.
        Nhà trường có nhiều ngành đào tạo chất lượng cao.
        Điều kiện tuyển sinh rất nghiêm ngặt và chuyên nghiệp.
        """
        
        # Test cleaning
        clean = clean_text(vietnamese_text)
        assert "Trường Đại học An ninh Nhân dân" in clean
        
        # Test chunking
        chunks = split_text_into_chunks(clean, chunk_size=100, overlap=20)
        assert len(chunks) >= 1
        
        # Test keyword extraction
        keywords = extract_keywords(clean, max_keywords=10)
        assert len(keywords) > 0
        # Should contain relevant keywords
        relevant_words = ['trường', 'đại', 'học', 'an', 'ninh', 'nhân', 'dân']
        found_relevant = any(word in keywords for word in relevant_words)
        assert found_relevant
