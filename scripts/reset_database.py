"""
Script to reset the database and FAISS index
"""
import os
import sys
import shutil
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.utils.logger import log
from config.settings import DATABASE_PATH, FAISS_INDEX_PATH

def main():
    # Reset SQLite database
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
        log.info(f"Removed database file: {DATABASE_PATH}")
    
    # Reset FAISS index
    if os.path.exists(FAISS_INDEX_PATH):
        shutil.rmtree(FAISS_INDEX_PATH)
        log.info(f"Removed FAISS index directory: {FAISS_INDEX_PATH}")

if __name__ == "__main__":
    main()


