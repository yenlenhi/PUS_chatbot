"""
Service extension for smart attachment retrieval
"""

from typing import List
import re


class SmartAttachmentMatcher:
    """Match attachments to queries using multiple strategies"""

    @staticmethod
    def extract_keywords_from_query(query: str) -> List[str]:
        """
        Extract potential keywords from user query

        Args:
            query: User query string

        Returns:
            List of keywords
        """
        # Common keywords related to forms/documents
        form_keywords = [
            "form",
            "mẫu",
            "đơn",
            "giấy",
            "biểu mẫu",
            "tờ khai",
            "template",
            "document",
        ]

        # Normalize query
        query_lower = query.lower()

        # Extract keywords that appear in query
        keywords = []

        # Check for form-related terms
        for keyword in form_keywords:
            if keyword in query_lower:
                keywords.append(keyword)

        # Extract specific phrases
        patterns = [
            r"(xin nghỉ|nghỉ học|nghỉ phép)",
            r"(học bổng|khuyến khích học tập)",
            r"(chuyển trường|chuyển môn|đổi ngành)",
            r"(bảo lưu|tạm dừng học)",
            r"(thôi học|rút hồ sơ)",
            r"(đăng ký môn|đăng ký học phần)",
            r"(gia hạn|miễn giảm)",
            r"(tiếp tục học|nhập học lại|quay lại học)",
            r"(xác nhận|chứng nhận)",
        ]

        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                keywords.extend(
                    matches if isinstance(matches, list) else [matches]
                )

        return list(set(keywords))  # Remove duplicates

    @staticmethod
    def score_attachment_relevance(
        attachment_keywords: List[str], query_keywords: List[str]
    ) -> float:
        """
        Calculate relevance score between attachment keywords and query keywords

        Args:
            attachment_keywords: Keywords from attachment
            query_keywords: Keywords extracted from query

        Returns:
            Relevance score (0-1)
        """
        if not attachment_keywords or not query_keywords:
            return 0.0

        # Convert to lowercase sets
        att_set = set(kw.lower() for kw in attachment_keywords)
        query_set = set(kw.lower() for kw in query_keywords)
        
        # Check for direct overlap first
        intersection = att_set.intersection(query_set)
        if intersection:
            union = att_set.union(query_set)
            return len(intersection) / len(union)

        # Check for partial matches (substrings)
        partial_matches = 0
        total_checks = 0
        
        for q_kw in query_set:
            match_found = False
            for att_kw in att_set:
                # Check if query keyword is in attachment keyword or vice versa
                if q_kw in att_kw or att_kw in q_kw:
                    match_found = True
                    break
            
            if match_found:
                partial_matches += 1
            total_checks += 1
            
        if partial_matches > 0:
            # Return a score based on how many query keywords found a match
            return (partial_matches / len(query_set)) * 0.9  # Slightly lower confidence than exact match
            
        return 0.0
