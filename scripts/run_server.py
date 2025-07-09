"""
Script to run the FastAPI server
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

import uvicorn
from config.settings import API_HOST, API_PORT, API_RELOAD
from src.utils.logger import log


def main():
    """Main function to run the server"""
    log.info("Starting University Chatbot API server...")
    
    try:
        uvicorn.run(
            "main:app",
            host=API_HOST,
            port=API_PORT,
            reload=API_RELOAD,
            log_level="info"
        )
    except KeyboardInterrupt:
        log.info("Server stopped by user")
    except Exception as e:
        log.error(f"Error running server: {e}")


if __name__ == "__main__":
    main()
