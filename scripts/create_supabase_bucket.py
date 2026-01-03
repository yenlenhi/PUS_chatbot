"""
Create Supabase Storage bucket for chat attachments
"""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Import after load_dotenv
from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY


def create_bucket():
    """Create chat-attachments bucket in Supabase Storage"""
    try:
        # Get Supabase credentials
        supabase_url = SUPABASE_URL
        supabase_key = SUPABASE_SERVICE_KEY

        if not supabase_url or not supabase_key:
            print("❌ Supabase credentials not found in environment variables")
            return False

        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")

        # Check if bucket already exists
        try:
            buckets = supabase.storage.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]

            if "chat-attachments" in bucket_names:
                print("✅ Bucket 'chat-attachments' already exists")
                return True
        except Exception as e:
            print(f"Could not list buckets: {e}")

        # Create bucket
        try:
            result = supabase.storage.create_bucket(
                "chat-attachments",
                options={
                    "public": False,  # Private bucket
                    "file_size_limit": 10485760,  # 10MB limit
                    "allowed_mime_types": [
                        "image/jpeg",
                        "image/png",
                        "image/gif",
                        "image/webp",
                    ],
                },
            )
            print(f"✅ Created bucket 'chat-attachments': {result}")
            return True
        except Exception as e:
            if "already exists" in str(e).lower():
                print("✅ Bucket 'chat-attachments' already exists")
                return True
            else:
                print(f"❌ Failed to create bucket: {e}")
                return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("Creating Supabase Storage Bucket")
    print("=" * 50)

    success = create_bucket()

    if success:
        print("\n✅ Bucket setup completed successfully!")
    else:
        print("\n❌ Bucket setup failed!")
        sys.exit(1)
