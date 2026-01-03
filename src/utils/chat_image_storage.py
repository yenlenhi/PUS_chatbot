"""
Helper functions for uploading and managing chat images in Supabase Storage
"""

import base64
import uuid
from typing import List, Optional
from supabase import create_client, Client
from src.utils.logger import log
from config.settings import SUPABASE_URL, SUPABASE_SERVICE_KEY


def get_supabase_client() -> Client:
    """Get Supabase client instance"""
    supabase_url = SUPABASE_URL
    supabase_key = SUPABASE_SERVICE_KEY

    if not supabase_url or not supabase_key:
        raise ValueError("Supabase credentials not found in environment variables")

    return create_client(supabase_url, supabase_key)


def upload_chat_image(image_data: str, conversation_id: str) -> Optional[str]:
    """
    Upload a chat image to Supabase Storage

    Args:
        image_data: Base64 encoded image data (with data:image/...;base64, prefix)
        conversation_id: Conversation ID for organizing images

    Returns:
        Public URL of the uploaded image, or None if failed
    """
    try:
        # Parse base64 data
        if "," in image_data:
            header, data = image_data.split(",", 1)
            # Extract format from header (e.g., "data:image/png;base64" -> "png")
            format = header.split("/")[1].split(";")[0]
        else:
            data = image_data
            format = "png"  # default format

        # Decode base64
        image_bytes = base64.b64decode(data)

        # Generate unique filename
        file_id = str(uuid.uuid4())
        filename = f"chat-images/{conversation_id}/{file_id}.{format}"

        # Upload to Supabase Storage
        supabase = get_supabase_client()

        response = supabase.storage.from_("chat-attachments").upload(
            filename,
            image_bytes,
            {
                "content-type": f"image/{format}",
                "cache-control": "3600",
                "upsert": "false",
            },
        )

        if response:
            # Get public URL
            public_url = supabase.storage.from_("chat-attachments").get_public_url(
                filename
            )
            log.info(f"✅ Uploaded chat image: {filename}")
            return public_url
        else:
            log.error(f"❌ Failed to upload image: {response}")
            return None

    except Exception as e:
        log.error(f"❌ Error uploading chat image: {e}")
        return None


def upload_chat_images(images: List[str], conversation_id: str) -> List[str]:
    """
    Upload multiple chat images to Supabase Storage

    Args:
        images: List of base64 encoded image data
        conversation_id: Conversation ID for organizing images

    Returns:
        List of public URLs for successfully uploaded images
    """
    uploaded_urls = []

    for image_data in images:
        url = upload_chat_image(image_data, conversation_id)
        if url:
            uploaded_urls.append(url)

    return uploaded_urls


def delete_chat_images(conversation_id: str) -> bool:
    """
    Delete all images for a conversation

    Args:
        conversation_id: Conversation ID

    Returns:
        True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()

        # List all files in the conversation folder
        files = supabase.storage.from_("chat-attachments").list(
            f"chat-images/{conversation_id}"
        )

        if files:
            # Delete all files
            file_paths = [
                f"chat-images/{conversation_id}/{file['name']}" for file in files
            ]
            supabase.storage.from_("chat-attachments").remove(file_paths)
            log.info(
                f"✅ Deleted {len(file_paths)} images for conversation: {conversation_id}"
            )
            return True

        return True  # No files to delete

    except Exception as e:
        log.error(f"❌ Error deleting chat images: {e}")
        return False
