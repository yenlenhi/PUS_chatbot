"""
Vietnamese text formatting and normalization utilities
"""
import re
import unicodedata


class VietnameseTextFormatter:
    """Vietnamese text formatting and normalization"""
    
    def __init__(self):
        """Initialize Vietnamese text formatter"""
        # Vietnamese text corrections (both with and without diacritics)
        self.spelling_corrections = {
            # Without diacritics -> with diacritics
            'tuyen sinh': 'tuyển sinh',
            'tuyển sinh': 'tuyển sinh',
            'dai hoc': 'đại học',
            'đại học': 'đại học',
            'an ninh': 'an ninh',
            'nhan dan': 'nhân dân',
            'nhân dân': 'nhân dân',
            'phuong thuc': 'phương thức',
            'phương thức': 'phương thức',
            'dieu kien': 'điều kiện',
            'điều kiện': 'điều kiện',
            'chuong trinh': 'chương trình',
            'chương trình': 'chương trình',
            'dao tao': 'đào tạo',
            'đào tạo': 'đào tạo',
            'hoc phi': 'học phí',
            'học phí': 'học phí',
            'thi sinh': 'thí sinh',
            'thí sinh': 'thí sinh',
            'nganh hoc': 'ngành học',
            'ngành học': 'ngành học',
            'bang cap': 'bằng cấp',
            'bằng cấp': 'bằng cấp',
            'chung chi': 'chứng chỉ',
            'chứng chỉ': 'chứng chỉ',
            'ket qua': 'kết quả',
            'kết quả': 'kết quả',
            'diem so': 'điểm số',
            'điểm số': 'điểm số',
            'ho so': 'hồ sơ',
            'hồ sơ': 'hồ sơ',
            'dang ky': 'đăng ký',
            'đăng ký': 'đăng ký',
            'xet tuyen': 'xét tuyển',
            'xét tuyển': 'xét tuyển',
            'tot nghiep': 'tốt nghiệp',
            'tốt nghiệp': 'tốt nghiệp',
            'trung hoc': 'trung học',
            'trung học': 'trung học',
            'pho thong': 'phổ thông',
            'phổ thông': 'phổ thông',
            'cao dang': 'cao đẳng',
            'cao đẳng': 'cao đẳng',
            'trinh do': 'trình độ',
            'trình độ': 'trình độ',
            'chinh quy': 'chính quy',
            'chính quy': 'chính quy',
            'lien thong': 'liên thông',
            'liên thông': 'liên thông',
            'tu xa': 'từ xa',
            'từ xa': 'từ xa',
            'tai chuc': 'tại chức',
            'tại chức': 'tại chức',
            'cong an': 'công an',
            'công an': 'công an',
            'bo cong an': 'Bộ Công an',
            'bộ công an': 'Bộ Công an',
            'bo giao duc': 'Bộ Giáo dục',
            'bộ giáo dục': 'Bộ Giáo dục',
            'quoc te': 'quốc tế',
            'quốc tế': 'quốc tế',
            'ngoai ngu': 'ngoại ngữ',
            'ngoại ngữ': 'ngoại ngữ',
            'tieng anh': 'tiếng Anh',
            'tiếng anh': 'tiếng Anh',
            'tieng viet': 'tiếng Việt',
            'tiếng việt': 'tiếng Việt',
            'truong dai hoc an ninh nhan dan': 'Trường Đại học An ninh Nhân dân',
            'trường đại học an ninh nhân dân': 'Trường Đại học An ninh Nhân dân',
            'dai hoc an ninh nhan dan': 'Đại học An ninh Nhân dân',
            'đại học an ninh nhân dân': 'Đại học An ninh Nhân dân',
            'tuyen thang': 'tuyển thẳng',
            'tuyển thẳng': 'tuyển thẳng',
            'quy che': 'quy chế',
            'quy chế': 'quy chế',
            'du tuyen': 'dự tuyển',
            'dự tuyển': 'dự tuyển',
            'co': 'có',
            'có': 'có',
            'ket hop': 'kết hợp',
            'kết hợp': 'kết hợp',
            'theo': 'theo',
            'voi': 'với',
            'với': 'với',
        }
        
        # Vietnamese punctuation rules
        self.punctuation_rules = [
            # Space before opening parentheses/brackets
            (r'(\w)\(', r'\1 ('),
            (r'(\w)\[', r'\1 ['),
            # Space after closing parentheses/brackets if followed by word
            (r'\)(\w)', r') \1'),
            (r'\](\w)', r'] \1'),
            # No space before punctuation
            (r'\s+([.,!?;:])', r'\1'),
            # Space after punctuation if followed by word
            (r'([.,!?;:])(\w)', r'\1 \2'),
            # No space before closing quotes
            (r'\s+"', r'"'),
            # Space after opening quotes
            (r'"\s*(\w)', r'" \1'),
        ]
        
        # Vietnamese capitalization rules
        self.capitalization_rules = {
            'trường đại học an ninh nhân dân': 'Trường Đại học An ninh Nhân dân',
            'đại học an ninh nhân dân': 'Đại học An ninh Nhân dân',
            'bộ công an': 'Bộ Công an',
            'bộ giáo dục và đào tạo': 'Bộ Giáo dục và Đào tạo',
            'công an nhân dân': 'Công an nhân dân',
            'trung học phổ thông': 'trung học phổ thông',
            'cao đẳng': 'cao đẳng',
            'đại học': 'đại học',
            'thạc sĩ': 'thạc sĩ',
            'tiến sĩ': 'tiến sĩ',
            'việt nam': 'Việt Nam',
            'hà nội': 'Hà Nội',
            'thành phố hồ chí minh': 'Thành phố Hồ Chí Minh',
            'đà nẵng': 'Đà Nẵng',
        }

    def normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters to standard Vietnamese form
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Normalize to NFC form (canonical composition)
        text = unicodedata.normalize('NFC', text)
        
        # Fix common Unicode issues in Vietnamese
        replacements = {
            'à': 'à', 'á': 'á', 'ả': 'ả', 'ã': 'ã', 'ạ': 'ạ',
            'ă': 'ă', 'ằ': 'ằ', 'ắ': 'ắ', 'ẳ': 'ẳ', 'ẵ': 'ẵ', 'ặ': 'ặ',
            'â': 'â', 'ầ': 'ầ', 'ấ': 'ấ', 'ẩ': 'ẩ', 'ẫ': 'ẫ', 'ậ': 'ậ',
            'è': 'è', 'é': 'é', 'ẻ': 'ẻ', 'ẽ': 'ẽ', 'ẹ': 'ẹ',
            'ê': 'ê', 'ề': 'ề', 'ế': 'ế', 'ể': 'ể', 'ễ': 'ễ', 'ệ': 'ệ',
            'ì': 'ì', 'í': 'í', 'ỉ': 'ỉ', 'ĩ': 'ĩ', 'ị': 'ị',
            'ò': 'ò', 'ó': 'ó', 'ỏ': 'ỏ', 'õ': 'õ', 'ọ': 'ọ',
            'ô': 'ô', 'ồ': 'ồ', 'ố': 'ố', 'ổ': 'ổ', 'ỗ': 'ỗ', 'ộ': 'ộ',
            'ơ': 'ơ', 'ờ': 'ờ', 'ớ': 'ớ', 'ở': 'ở', 'ỡ': 'ỡ', 'ợ': 'ợ',
            'ù': 'ù', 'ú': 'ú', 'ủ': 'ủ', 'ũ': 'ũ', 'ụ': 'ụ',
            'ư': 'ư', 'ừ': 'ừ', 'ứ': 'ứ', 'ử': 'ử', 'ữ': 'ữ', 'ự': 'ự',
            'ỳ': 'ỳ', 'ý': 'ý', 'ỷ': 'ỷ', 'ỹ': 'ỹ', 'ỵ': 'ỵ',
            'đ': 'đ', 'Đ': 'Đ'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
            
        return text

    def fix_spacing(self, text: str) -> str:
        """
        Fix spacing issues in Vietnamese text
        
        Args:
            text: Input text
            
        Returns:
            Text with corrected spacing
        """
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Apply punctuation rules
        for pattern, replacement in self.punctuation_rules:
            text = re.sub(pattern, replacement, text)
        
        # Fix spacing around Vietnamese punctuation
        text = re.sub(r'\s*:\s*', ': ', text)
        text = re.sub(r'\s*;\s*', '; ', text)
        text = re.sub(r'\s*,\s*', ', ', text)
        text = re.sub(r'\s*\.\s*', '. ', text)
        text = re.sub(r'\s*\?\s*', '? ', text)
        text = re.sub(r'\s*!\s*', '! ', text)
        
        # Fix spacing around dashes
        text = re.sub(r'\s*-\s*', ' - ', text)
        text = re.sub(r'\s*–\s*', ' – ', text)
        text = re.sub(r'\s*—\s*', ' — ', text)
        
        # Remove trailing spaces
        text = text.strip()
        
        return text

    def fix_capitalization(self, text: str) -> str:
        """
        Fix capitalization according to Vietnamese rules
        
        Args:
            text: Input text
            
        Returns:
            Text with corrected capitalization
        """
        # Apply specific capitalization rules
        text_lower = text.lower()
        for incorrect, correct in self.capitalization_rules.items():
            # Case-insensitive replacement
            pattern = re.escape(incorrect)
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)
        
        # Capitalize first letter of sentences
        text = re.sub(r'(^|[.!?]\s+)([a-záàảãạăằắẳẵặâầấẩẫậéèẻẽẹêềếểễệíìỉĩịóòỏõọôồốổỗộơờớởỡợúùủũụưừứửữựýỳỷỹỵđ])', 
                     lambda m: m.group(1) + m.group(2).upper(), text)
        
        return text

    def correct_spelling(self, text: str) -> str:
        """
        Correct common spelling mistakes in Vietnamese

        Args:
            text: Input text

        Returns:
            Text with corrected spelling
        """
        # Sort by length (longest first) to avoid partial replacements
        sorted_corrections = sorted(self.spelling_corrections.items(),
                                  key=lambda x: len(x[0]), reverse=True)

        for incorrect, correct in sorted_corrections:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(incorrect) + r'\b'
            text = re.sub(pattern, correct, text, flags=re.IGNORECASE)

        return text

    def format_numbers_and_dates(self, text: str) -> str:
        """
        Format numbers and dates according to Vietnamese standards
        
        Args:
            text: Input text
            
        Returns:
            Text with formatted numbers and dates
        """
        # Format years
        text = re.sub(r'\b(\d{4})\b', r'\1', text)
        
        # Format dates (dd/mm/yyyy or dd-mm-yyyy)
        text = re.sub(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b', r'\1/\2/\3', text)
        
        # Format percentages
        text = re.sub(r'(\d+)\s*%', r'\1%', text)
        
        # Format currency (VND)
        text = re.sub(r'(\d+)\s*(VND|vnđ|đồng)', r'\1 VND', text, flags=re.IGNORECASE)
        
        return text

    def format_text(self, text: str) -> str:
        """
        Apply comprehensive Vietnamese text formatting
        
        Args:
            text: Input text
            
        Returns:
            Formatted text
        """
        if not text or not text.strip():
            return text
        
        # Apply all formatting steps
        text = self.normalize_unicode(text)
        text = self.fix_spacing(text)
        text = self.correct_spelling(text)
        text = self.fix_capitalization(text)
        text = self.format_numbers_and_dates(text)
        
        # Final cleanup
        text = text.strip()
        
        return text


# Global formatter instance
vietnamese_formatter = VietnameseTextFormatter()


def format_vietnamese_text(text: str) -> str:
    """
    Convenience function to format Vietnamese text
    
    Args:
        text: Input text
        
    Returns:
        Formatted text
    """
    return vietnamese_formatter.format_text(text)
