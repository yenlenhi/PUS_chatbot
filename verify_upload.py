import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from src.services.supabase_storage_service import SupabaseStorageService

async def verify_upload():
    print("Starting Supabase Storage Verification...")
    
    # 1. Initialize Service
    try:
        storage = SupabaseStorageService()
        print("Service initialized")
    except Exception as e:
        print(f"Failed to initialize service: {e}")
        return

    if not storage.is_configured():
        print("Supabase is not configured in .env")
        return

    # 2. Create a dummy test file
    test_filename = "test_upload_verify.txt"
    test_content = b"This is a test file to verify Supabase Storage integration."
    
    print(f"Preparing to upload {test_filename}...")

    # 3. Upload File
    try:
        success, message, url = storage.upload_file(
            file_content=test_content,
            filename=test_filename,
            content_type="text/plain"
        )
        
        if success:
            print(f"Upload successful!")
            print(f"Public URL: {url}")
        else:
            print(f"Upload failed: {message}")
            return
            
    except Exception as e:
        print(f"Exception during upload: {e}")
        return

    # 4. Verify Existence
    try:
        exists = storage.file_exists(test_filename)
        if exists:
            print(f"File existence check passed")
        else:
            print(f"File uploaded but existence check failed (might be delay)")
    except Exception as e:
        print(f"Error checking existence: {e}")

    # 5. Clean up (Delete file)
    print("Cleaning up (Deleting test file)...")
    try:
        success, message = storage.delete_file(test_filename)
        if success:
            print(f"Delete successful")
        else:
            print(f"Delete failed: {message}")
    except Exception as e:
        print(f"Exception during delete: {e}")

    print("\nVerification finished!")

if __name__ == "__main__":
    asyncio.run(verify_upload())
