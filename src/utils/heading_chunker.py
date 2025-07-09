"""
Module for chunking text based on headings and sections
"""
import re
from typing import List, Dict, Any, Optional
from src.models.schemas import DocumentChunk
from src.utils.logger import log

class HeadingChunker:
    """
    Enhanced class for chunking text based on headings and sections
    Ensures complete content preservation and intelligent sub-chunking
    """

    def __init__(self, min_chunk_size: int = 100, max_chunk_size: int = 2500, target_chunk_size: int = 1000):
        """
        Initialize the heading chunker

        Args:
            min_chunk_size: Minimum size of a chunk in characters (will be preserved even if smaller)
            max_chunk_size: Maximum size before forcing a split
            target_chunk_size: Target size for optimal RAG performance
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.target_chunk_size = target_chunk_size

        # Enhanced regex patterns for different heading levels
        self.heading_patterns = [
            # Level 1 headings (e.g., "1. Khu vực tuyển sinh")
            r'^\s*(\d+)\.\s+(.+)$',

            # Level 2 headings (e.g., "7.1. Đối tượng dự tuyển")
            r'^\s*(\d+\.\d+)\.\s+(.+)$',

            # Level 3 headings (e.g., "7.3.1. Đối với thí sinh dự tuyển theo Phương thức 1")
            r'^\s*(\d+\.\d+\.\d+)\.\s+(.+)$',

            # Level 4 headings (e.g., "7.3.1.1. Sub-section")
            r'^\s*(\d+\.\d+\.\d+\.\d+)\.\s+(.+)$'
        ]

        # Additional patterns for non-numbered headings
        self.additional_patterns = [
            # Roman numerals (I., II., III.)
            r'^\s*([IVX]+)\.\s+(.+)$',

            # Letters (A., B., C.)
            r'^\s*([A-Z])\.\s+(.+)$',

            # Bullet points with emphasis
            r'^\s*[-•]\s*(.+):$',

            # All caps headings
            r'^([A-ZÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ\s]+)$'
        ]
    
    def extract_headings(self, text: str) -> List[Dict[str, Any]]:
        """
        Enhanced heading extraction with support for various heading formats

        Args:
            text: Input text

        Returns:
            List of dictionaries with heading information
        """
        lines = text.split('\n')
        headings = []

        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Try numbered heading patterns first
            for level, pattern in enumerate(self.heading_patterns, 1):
                match = re.match(pattern, line_stripped)
                if match:
                    heading_num = match.group(1)
                    heading_text = match.group(2)

                    # Calculate accurate start position
                    start_pos = self._calculate_line_start_pos(text, i)

                    headings.append({
                        'level': level,
                        'number': heading_num,
                        'text': heading_text,
                        'full_text': line_stripped,
                        'line_index': i,
                        'start_pos': start_pos,
                        'parent_number': self._get_parent_number(heading_num),
                        'heading_type': 'numbered'
                    })
                    break
            else:
                # Try additional patterns for non-numbered headings
                for pattern in self.additional_patterns:
                    match = re.match(pattern, line_stripped)
                    if match:
                        start_pos = self._calculate_line_start_pos(text, i)

                        headings.append({
                            'level': 99,  # Lower priority for non-numbered headings
                            'number': None,
                            'text': match.group(1) if match.lastindex >= 1 else line_stripped,
                            'full_text': line_stripped,
                            'line_index': i,
                            'start_pos': start_pos,
                            'parent_number': None,
                            'heading_type': 'unnumbered'
                        })
                        break

        return headings

    def _calculate_line_start_pos(self, text: str, line_index: int) -> int:
        """Calculate the accurate start position of a line in the text"""
        lines = text.split('\n')
        pos = 0
        for i in range(line_index):
            pos += len(lines[i]) + 1  # +1 for newline character
        return pos

    def _get_parent_number(self, heading_num: str) -> Optional[str]:
        """Get parent heading number (e.g., '7.3' for '7.3.1')"""
        if not heading_num or '.' not in heading_num:
            return None
        parts = heading_num.split('.')
        if len(parts) <= 1:
            return None
        return '.'.join(parts[:-1])
    
    def chunk_by_headings(self, text: str, source_file: str, page_number: Optional[int] = None) -> List[DocumentChunk]:
        """
        Enhanced chunking that preserves all content and handles large sections intelligently

        Args:
            text: Input text
            source_file: Source file name
            page_number: Page number

        Returns:
            List of document chunks with enhanced metadata
        """
        # Extract headings
        headings = self.extract_headings(text)

        if not headings:
            # If no headings found, split by paragraphs or sentences
            return self._chunk_without_headings(text, source_file, page_number)

        # Sort headings by position
        headings.sort(key=lambda h: h['start_pos'])

        chunks = []
        chunk_index = 0

        # Handle text before first heading (introduction)
        if headings[0]['start_pos'] > 0:
            intro_text = text[:headings[0]['start_pos']].strip()
            if intro_text:  # Always preserve intro text, regardless of size
                word_count = len(intro_text.split())
                char_count = len(intro_text)

                chunks.append(DocumentChunk(
                    content=intro_text,
                    source_file=source_file,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    heading_text=None,
                    heading_level=None,
                    heading_number=None,
                    parent_heading=None,
                    is_sub_chunk=False,
                    chunk_type="intro",
                    word_count=word_count,
                    char_count=char_count
                ))
                chunk_index += 1

        # Process each heading and its content
        for i, heading in enumerate(headings):
            # Determine end position of this section
            if i < len(headings) - 1:
                end_pos = headings[i+1]['start_pos']
            else:
                end_pos = len(text)

            # Extract section content
            section_text = text[heading['start_pos']:end_pos].strip()

            if not section_text:
                continue

            # Always preserve content, but split if too large
            section_chunks = self._process_section(
                section_text, heading, source_file, page_number, chunk_index
            )

            chunks.extend(section_chunks)
            chunk_index += len(section_chunks)

        # Post-process: merge small chunks with adjacent chunks
        chunks = self._merge_small_chunks(chunks)

        log.info(f"Created {len(chunks)} enhanced heading-based chunks from text")
        return chunks

    def _chunk_without_headings(self, text: str, source_file: str, page_number: Optional[int]) -> List[DocumentChunk]:
        """Handle text without clear headings by splitting into reasonable chunks"""
        chunks = []

        # Split by double newlines (paragraphs) first
        paragraphs = text.split('\n\n')
        current_chunk = ""
        chunk_index = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # If adding this paragraph would exceed target size, create a chunk
            if current_chunk and len(current_chunk + "\n\n" + paragraph) > self.target_chunk_size:
                if current_chunk:
                    word_count = len(current_chunk.split())
                    char_count = len(current_chunk)

                    chunks.append(DocumentChunk(
                        content=current_chunk.strip(),
                        source_file=source_file,
                        page_number=page_number,
                        chunk_index=chunk_index,
                        chunk_type="content",
                        word_count=word_count,
                        char_count=char_count
                    ))
                    chunk_index += 1
                    current_chunk = paragraph
                else:
                    current_chunk = paragraph
            else:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph

        # Add the last chunk
        if current_chunk:
            word_count = len(current_chunk.split())
            char_count = len(current_chunk)

            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source_file=source_file,
                page_number=page_number,
                chunk_index=chunk_index,
                chunk_type="content",
                word_count=word_count,
                char_count=char_count
            ))

        return chunks

    def _process_section(self, section_text: str, heading: Dict[str, Any],
                        source_file: str, page_number: Optional[int],
                        start_chunk_index: int) -> List[DocumentChunk]:
        """
        Process a section with intelligent splitting if needed

        Args:
            section_text: The complete section text
            heading: Heading information dictionary
            source_file: Source file name
            page_number: Page number
            start_chunk_index: Starting chunk index

        Returns:
            List of chunks for this section
        """
        word_count = len(section_text.split())
        char_count = len(section_text)

        # If section is within target size, keep as single chunk
        if char_count <= self.max_chunk_size:
            return [DocumentChunk(
                content=section_text,
                source_file=source_file,
                page_number=page_number,
                chunk_index=start_chunk_index,
                heading_text=heading.get('text'),
                heading_level=heading.get('level'),
                heading_number=heading.get('number'),
                parent_heading=heading.get('parent_number'),
                is_sub_chunk=False,
                chunk_type="heading",
                word_count=word_count,
                char_count=char_count
            )]

        # Section is too large, need to split intelligently
        log.info(f"Section '{heading.get('text', 'Unknown')}' is large ({char_count} chars), splitting...")

        # Try to find sub-headings within this section
        sub_chunks = self._split_large_section(section_text, heading, source_file, page_number, start_chunk_index)

        return sub_chunks

    def _split_large_section(self, section_text: str, main_heading: Dict[str, Any],
                           source_file: str, page_number: Optional[int],
                           start_chunk_index: int) -> List[DocumentChunk]:
        """
        Split a large section into smaller chunks while preserving structure
        """
        chunks = []

        # First, try to find sub-headings within this section
        sub_headings = self.extract_headings(section_text)

        # Filter sub-headings that are actually sub-headings of the main heading
        main_number = main_heading.get('number', '')
        relevant_sub_headings = []

        if main_number:
            for sub_heading in sub_headings:
                sub_number = sub_heading.get('number', '')
                if sub_number and sub_number.startswith(main_number + '.'):
                    relevant_sub_headings.append(sub_heading)

        if relevant_sub_headings:
            # Split by sub-headings
            chunks = self._split_by_sub_headings(
                section_text, main_heading, relevant_sub_headings,
                source_file, page_number, start_chunk_index
            )
        else:
            # No sub-headings found, split by paragraphs/sentences
            chunks = self._split_by_paragraphs(
                section_text, main_heading, source_file, page_number, start_chunk_index
            )

        return chunks

    def _split_by_sub_headings(self, section_text: str, main_heading: Dict[str, Any],
                              sub_headings: List[Dict[str, Any]], source_file: str,
                              page_number: Optional[int], start_chunk_index: int) -> List[DocumentChunk]:
        """Split section by its sub-headings"""
        chunks = []
        chunk_index = start_chunk_index

        # Sort sub-headings by position
        sub_headings.sort(key=lambda h: h['start_pos'])

        # Handle content before first sub-heading
        if sub_headings[0]['start_pos'] > 0:
            intro_content = section_text[:sub_headings[0]['start_pos']].strip()
            if intro_content:
                word_count = len(intro_content.split())
                char_count = len(intro_content)

                chunks.append(DocumentChunk(
                    content=intro_content,
                    source_file=source_file,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    heading_text=main_heading.get('text'),
                    heading_level=main_heading.get('level'),
                    heading_number=main_heading.get('number'),
                    parent_heading=main_heading.get('parent_number'),
                    is_sub_chunk=True,
                    sub_chunk_index=0,
                    chunk_type="heading",
                    word_count=word_count,
                    char_count=char_count
                ))
                chunk_index += 1

        # Process each sub-heading
        for i, sub_heading in enumerate(sub_headings):
            # Determine end position
            if i < len(sub_headings) - 1:
                end_pos = sub_headings[i+1]['start_pos']
            else:
                end_pos = len(section_text)

            sub_content = section_text[sub_heading['start_pos']:end_pos].strip()
            if sub_content:
                word_count = len(sub_content.split())
                char_count = len(sub_content)

                chunks.append(DocumentChunk(
                    content=sub_content,
                    source_file=source_file,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    heading_text=sub_heading.get('text'),
                    heading_level=sub_heading.get('level'),
                    heading_number=sub_heading.get('number'),
                    parent_heading=main_heading.get('number'),
                    is_sub_chunk=True,
                    sub_chunk_index=i + 1,
                    chunk_type="heading",
                    word_count=word_count,
                    char_count=char_count
                ))
                chunk_index += 1

        # Update total_sub_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_sub_chunks = total_chunks

        return chunks

    def _split_by_paragraphs(self, section_text: str, main_heading: Dict[str, Any],
                           source_file: str, page_number: Optional[int],
                           start_chunk_index: int) -> List[DocumentChunk]:
        """Split section by paragraphs when no sub-headings are found"""
        chunks = []
        chunk_index = start_chunk_index

        # Split by double newlines (paragraphs)
        paragraphs = section_text.split('\n\n')
        current_chunk = ""
        sub_chunk_index = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Check if adding this paragraph would exceed target size
            potential_chunk = current_chunk + "\n\n" + paragraph if current_chunk else paragraph

            if len(potential_chunk) > self.target_chunk_size and current_chunk:
                # Create chunk with current content
                word_count = len(current_chunk.split())
                char_count = len(current_chunk)

                chunks.append(DocumentChunk(
                    content=current_chunk.strip(),
                    source_file=source_file,
                    page_number=page_number,
                    chunk_index=chunk_index,
                    heading_text=main_heading.get('text'),
                    heading_level=main_heading.get('level'),
                    heading_number=main_heading.get('number'),
                    parent_heading=main_heading.get('parent_number'),
                    is_sub_chunk=True,
                    sub_chunk_index=sub_chunk_index,
                    chunk_type="heading",
                    word_count=word_count,
                    char_count=char_count
                ))

                chunk_index += 1
                sub_chunk_index += 1
                current_chunk = paragraph
            else:
                current_chunk = potential_chunk

        # Add the last chunk
        if current_chunk:
            word_count = len(current_chunk.split())
            char_count = len(current_chunk)

            chunks.append(DocumentChunk(
                content=current_chunk.strip(),
                source_file=source_file,
                page_number=page_number,
                chunk_index=chunk_index,
                heading_text=main_heading.get('text'),
                heading_level=main_heading.get('level'),
                heading_number=main_heading.get('number'),
                parent_heading=main_heading.get('parent_number'),
                is_sub_chunk=True,
                sub_chunk_index=sub_chunk_index,
                chunk_type="heading",
                word_count=word_count,
                char_count=char_count
            ))

        # Update total_sub_chunks for all chunks
        total_chunks = len(chunks)
        for chunk in chunks:
            chunk.total_sub_chunks = total_chunks

        return chunks

    def analyze_chunks(self, chunks: List[DocumentChunk]) -> Dict[str, Any]:
        """
        Analyze chunk statistics for quality assessment

        Args:
            chunks: List of document chunks

        Returns:
            Dictionary with analysis results
        """
        if not chunks:
            return {}

        char_counts = [chunk.char_count or len(chunk.content) for chunk in chunks]
        word_counts = [chunk.word_count or len(chunk.content.split()) for chunk in chunks]

        analysis = {
            'total_chunks': len(chunks),
            'total_characters': sum(char_counts),
            'total_words': sum(word_counts),
            'avg_char_count': sum(char_counts) / len(char_counts),
            'avg_word_count': sum(word_counts) / len(word_counts),
            'min_char_count': min(char_counts),
            'max_char_count': max(char_counts),
            'min_word_count': min(word_counts),
            'max_word_count': max(word_counts),
            'chunks_by_type': {},
            'chunks_by_heading_level': {},
            'large_chunks': [],
            'small_chunks': []
        }

        # Analyze by type and level
        for chunk in chunks:
            chunk_type = chunk.chunk_type
            analysis['chunks_by_type'][chunk_type] = analysis['chunks_by_type'].get(chunk_type, 0) + 1

            if chunk.heading_level:
                level = chunk.heading_level
                analysis['chunks_by_heading_level'][level] = analysis['chunks_by_heading_level'].get(level, 0) + 1

            char_count = chunk.char_count or len(chunk.content)
            if char_count > self.max_chunk_size:
                analysis['large_chunks'].append({
                    'chunk_index': chunk.chunk_index,
                    'heading': chunk.heading_text,
                    'char_count': char_count
                })
            elif char_count < self.min_chunk_size:
                analysis['small_chunks'].append({
                    'chunk_index': chunk.chunk_index,
                    'heading': chunk.heading_text,
                    'char_count': char_count
                })

        return analysis

    def _merge_small_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """
        Merge small chunks with adjacent chunks to improve context

        Args:
            chunks: List of chunks to process

        Returns:
            List of chunks with small chunks merged
        """
        if len(chunks) <= 1:
            return chunks

        merged_chunks = []
        i = 0

        while i < len(chunks):
            current_chunk = chunks[i]
            current_size = current_chunk.char_count or len(current_chunk.content)

            # If current chunk is small, try to merge with next chunk
            if current_size < self.min_chunk_size and i < len(chunks) - 1:
                next_chunk = chunks[i + 1]
                next_size = next_chunk.char_count or len(next_chunk.content)

                # Only merge if combined size is reasonable and they're related
                combined_size = current_size + next_size
                if combined_size <= self.max_chunk_size and self._can_merge_chunks(current_chunk, next_chunk):
                    # Merge the chunks
                    merged_content = current_chunk.content + "\n\n" + next_chunk.content
                    merged_word_count = len(merged_content.split())
                    merged_char_count = len(merged_content)

                    # Create merged chunk with metadata from the larger chunk
                    primary_chunk = next_chunk if next_size > current_size else current_chunk

                    merged_chunk = DocumentChunk(
                        content=merged_content,
                        source_file=current_chunk.source_file,
                        page_number=current_chunk.page_number,
                        chunk_index=current_chunk.chunk_index,
                        heading_text=primary_chunk.heading_text,
                        heading_level=primary_chunk.heading_level,
                        heading_number=primary_chunk.heading_number,
                        parent_heading=primary_chunk.parent_heading,
                        is_sub_chunk=primary_chunk.is_sub_chunk,
                        sub_chunk_index=primary_chunk.sub_chunk_index,
                        total_sub_chunks=primary_chunk.total_sub_chunks,
                        chunk_type=primary_chunk.chunk_type,
                        word_count=merged_word_count,
                        char_count=merged_char_count
                    )

                    merged_chunks.append(merged_chunk)
                    i += 2  # Skip both chunks
                    continue

            # If we can't merge or chunk is not small, keep as is
            merged_chunks.append(current_chunk)
            i += 1

        # Update chunk indices
        for idx, chunk in enumerate(merged_chunks):
            chunk.chunk_index = idx

        return merged_chunks

    def _can_merge_chunks(self, chunk1: DocumentChunk, chunk2: DocumentChunk) -> bool:
        """
        Determine if two chunks can be merged based on their metadata

        Args:
            chunk1: First chunk
            chunk2: Second chunk

        Returns:
            True if chunks can be merged
        """
        # Same source file
        if chunk1.source_file != chunk2.source_file:
            return False

        # Same page (if available)
        if chunk1.page_number and chunk2.page_number and chunk1.page_number != chunk2.page_number:
            return False

        # If both have headings, they should be related
        if chunk1.heading_number and chunk2.heading_number:
            # Same parent heading or one is parent of the other
            if chunk1.parent_heading == chunk2.heading_number or chunk2.parent_heading == chunk1.heading_number:
                return True
            if chunk1.parent_heading == chunk2.parent_heading:
                return True
            return False

        # If one has heading and other doesn't, they can be merged if they're adjacent content
        if (chunk1.heading_text and not chunk2.heading_text) or (chunk2.heading_text and not chunk1.heading_text):
            return True

        # Both are content chunks without specific headings
        if not chunk1.heading_text and not chunk2.heading_text:
            return True

        return True