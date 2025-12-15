"""
Test RAG service with attachment retrieval
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.services.rag_service import RAGService


def test_rag_with_attachments():
    """Test RAG service to see if attachments are retrieved"""
    print("=" * 60)
    print("TESTING RAG SERVICE WITH ATTACHMENTS")
    print("=" * 60)

    # Initialize RAG service
    print("\n1. Initializing RAG service...")
    rag = RAGService()

    # Test query
    query = "cho tôi xin form đơn xin nghỉ học"
    print(f"\n2. Testing query: '{query}'")

    # Generate answer
    print("\n3. Generating answer...")
    result = rag.generate_answer(query)

    # Check results
    print("\n4. Results:")
    print(f"   Answer preview: {result['answer'][:200]}...")
    print(f"   Sources: {len(result.get('sources', []))}")
    print(f"   Source references: {len(result.get('source_references', []))}")
    print(f"   Attachments: {len(result.get('attachments', []))}")

    # Show attachments
    if result.get("attachments"):
        print("\n5. Attachments found:")
        for att in result["attachments"]:
            print(f"   - {att['file_name']}")
            print(f"     Type: {att['file_type']}")
            print(f"     URL: {att['download_url']}")
            print(f"     Description: {att.get('description', 'N/A')}")
    else:
        print("\n5. ❌ No attachments found!")
        print("   Debugging info:")
        print("   - Check if attachment service is initialized")
        print("   - Check if keywords are extracted correctly")
        print("   - Check if search returns results")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    test_rag_with_attachments()
