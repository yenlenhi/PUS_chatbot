import sys
import os
import argparse
import logging

# Setup logging to file only to avoid console encoding issues
log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'debug_retrieval.log'))
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=log_file_path,
    filemode='w',
    encoding='utf-8'
)

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.embedding_service import EmbeddingService
from src.services.rag_service import RAGService
from config import settings

def debug_retrieval(question: str, top_k: int):
    """
    Performs a retrieval step and logs the retrieved chunks and their scores.
    """
    logging.info(f"--- Debugging Retrieval for Question ---")
    logging.info(f"Question: {question}")
    logging.info(f"Top K: {top_k}")
    logging.info("----------------------------------------")

    try:
        logging.info("Initializing RAGService...")
        # RAGService initializes its own dependencies
        rag_service = RAGService()
        logging.info("RAGService initialized.")

        logging.info("Performing retrieval...")
        # Use the correct method to retrieve chunks
        results = rag_service.retrieve_relevant_chunks(question, top_k=top_k)
        logging.info("Retrieval complete.")

        if not results:
            logging.warning("No results found.")
            return

        logging.info(f"Found {len(results)} chunks:\n")

        # Process the results which is a list of dictionaries
        for i, chunk in enumerate(results):
            score = chunk.get('similarity_score', 0.0)
            content = chunk.get('content', 'N/A')
            source = chunk.get('source_file', 'N/A')
            page = chunk.get('page_number', 'N/A')
            heading = chunk.get('heading', 'N/A')

            logging.info(f"--- Chunk {i+1} (Score: {score:.4f}) ---")
            logging.info(f"Content: {content}")
            logging.info(f"Source: {source}, Page: {page}, Heading: {heading}\n")

    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Debug the retrieval step of the RAG pipeline.")
    parser.add_argument("question", type=str, help="The question to test retrieval for.")
    parser.add_argument("--top_k", type=int, default=settings.TOP_K_RESULTS, help="Number of chunks to retrieve.")
    args = parser.parse_args()

    debug_retrieval(args.question, args.top_k)

