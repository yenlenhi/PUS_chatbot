"""
Test script for attachment feature
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.postgres_database_service import PostgresDatabaseService
from src.services.attachment_service import AttachmentService
from src.services.smart_attachment_matcher import SmartAttachmentMatcher


def test_attachment_search():
    """Test attachment search functionality"""
    print("=" * 60)
    print("TESTING ATTACHMENT SEARCH")
    print("=" * 60)

    # Initialize services
    db = PostgresDatabaseService()
    attachment_service = AttachmentService(db)

    # List all attachments
    print("\n1. All Attachments:")
    all_attachments = attachment_service.get_all_attachments()
    print(f"   Total: {len(all_attachments)}")
    for att in all_attachments:
        print(f"   - ID {att.id}: {att.file_name}")
        print(f"     Description: {att.description}")
        print(f"     Keywords: {att.keywords}")

    # Test queries
    test_queries = [
        "cho tôi xin form đơn xin nghỉ học",
        "mẫu đơn nghỉ học có phép",
        "form xin phép nghỉ",
        "đơn xin học bổng",
    ]

    print("\n2. Test Queries:")
    for query in test_queries:
        print(f"\n   Query: '{query}'")

        # Extract keywords
        keywords = SmartAttachmentMatcher.extract_keywords_from_query(query)
        print(f"   Extracted keywords: {keywords}")

        # Search attachments
        results = attachment_service.search_attachments(keywords=keywords)
        print(f"   Found {len(results)} attachment(s):")

        for result in results:
            # Calculate relevance score
            score = SmartAttachmentMatcher.score_attachment_relevance(
                result.keywords or [], keywords
            )
            print(f"     - {result.file_name} (score: {score:.2f})")
            print(f"       Keywords: {result.keywords}")
            print(f"       Description: {result.description}")

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_attachment_search()
