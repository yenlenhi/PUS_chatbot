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
        ]

        for pattern in patterns:
            matches = re.findall(pattern, query_lower)
            if matches:
                keywords.extend(
                    matches[0] if isinstance(matches[0], list) else [matches[0]]
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

        # Calculate overlap
        intersection = att_set.intersection(query_set)
        if not intersection:
            return 0.0

        # Jaccard similarity
        union = att_set.union(query_set)
        score = len(intersection) / len(union) if union else 0.0

        return min(score, 1.0)
