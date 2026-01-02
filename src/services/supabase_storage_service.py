"""
Supabase Storage Service for uploading PDFs to Supabase Storage

This service handles:
- Uploading PDF files to Supabase Storage bucket
- Generating public URLs for uploaded files
- Managing file operations (delete, list, etc.)
"""

import logging
import re
import unicodedata
from typing import Optional, Tuple

import requests

from config.settings import (
    SUPABASE_SERVICE_KEY,
    SUPABASE_STORAGE_BUCKET,
    SUPABASE_URL,
)

log = logging.getLogger(__name__)


class SupabaseStorageService:
    """Service for interacting with Supabase Storage"""

    def __init__(self):
        self.supabase_url = SUPABASE_URL
        self.service_key = SUPABASE_SERVICE_KEY
        self.bucket_name = SUPABASE_STORAGE_BUCKET
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate that required configuration is present"""
        if not self.supabase_url:
            log.warning("SUPABASE_URL not configured - Storage uploads will fail")
        if not self.service_key:
            log.warning(
                "SUPABASE_SERVICE_KEY not configured - Storage uploads will fail"
            )

    def is_configured(self) -> bool:
        """Check if Supabase Storage is properly configured"""
        return bool(self.supabase_url and self.service_key)

    @staticmethod
    def normalize_filename(filename: str) -> str:
        """
        Normalize filename to ASCII-safe characters for URL compatibility.

        - Removes Vietnamese diacritics
        - Replaces spaces and special characters with underscores
        - Ensures the filename is URL-safe

        Args:
            filename: Original filename

        Returns:
            Normalized ASCII-safe filename
        """
        # Remove Vietnamese diacritics using NFKD normalization
        nfkd_form = unicodedata.normalize("NFKD", filename)
        ascii_name = nfkd_form.encode("ASCII", "ignore").decode("ASCII")

        # Replace spaces and special characters with underscores
        # Keep only alphanumeric, dots, underscores, and hyphens
        ascii_name = re.sub(r"[^a-zA-Z0-9._-]", "_", ascii_name)

        # Remove multiple consecutive underscores
        ascii_name = re.sub(r"_+", "_", ascii_name)

        # Remove leading/trailing underscores
        ascii_name = ascii_name.strip("_")

        return ascii_name

    def upload_file(
        self, file_content: bytes, filename: str, content_type: str = "application/pdf"
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Upload a file to Supabase Storage.

        Args:
            file_content: Raw file bytes
            filename: Original filename (will be normalized)
            content_type: MIME type of the file

        Returns:
            Tuple of (success: bool, message: str, public_url: Optional[str])
        """
        if not self.is_configured():
            return (
                False,
                "Supabase Storage không được cấu hình. Kiểm tra SUPABASE_URL và SUPABASE_SERVICE_KEY.",
                None,
            )

        try:
            # Normalize filename for URL safety
            safe_filename = self.normalize_filename(filename)
            log.info(f"📤 Uploading to Supabase: {filename} -> {safe_filename}")

            # Supabase Storage upload URL
            upload_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{safe_filename}"

            headers = {
                "Authorization": f"Bearer {self.service_key}",
                "apikey": self.service_key,
                "Content-Type": content_type,
            }

            # Upload file
            response = requests.post(
                upload_url, headers=headers, data=file_content, timeout=120
            )

            if response.status_code == 200:
                public_url = self.get_public_url(safe_filename)
                log.info(f"✅ Uploaded to Supabase: {public_url}")
                return (
                    True,
                    f"File uploaded successfully: {safe_filename}",
                    public_url,
                )
            else:
                error_msg = response.text
                log.error(
                    f"❌ Supabase upload failed: {response.status_code} - {error_msg}"
                )
                return (
                    False,
                    f"Upload failed: {response.status_code} - {error_msg}",
                    None,
                )

        except requests.exceptions.Timeout:
            log.error("❌ Supabase upload timeout")
            return (False, "Upload timeout - file may be too large", None)
        except Exception as e:
            log.error(f"❌ Supabase upload error: {e}")
            return (False, f"Upload error: {str(e)}", None)

    def get_public_url(self, filename: str) -> str:
        """
        Get the public URL for a file in Supabase Storage.

        Args:
            filename: The filename in storage (already normalized)

        Returns:
            Public URL for the file
        """
        return f"{self.supabase_url}/storage/v1/object/public/{self.bucket_name}/{filename}"

    def delete_file(self, filename: str) -> Tuple[bool, str]:
        """
        Delete a file from Supabase Storage.

        Args:
            filename: The filename to delete

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.is_configured():
            return (False, "Supabase Storage not configured")

        try:
            safe_filename = self.normalize_filename(filename)
            delete_url = f"{self.supabase_url}/storage/v1/object/{self.bucket_name}/{safe_filename}"

            headers = {
                "Authorization": f"Bearer {self.service_key}",
                "apikey": self.service_key,
            }

            response = requests.delete(delete_url, headers=headers, timeout=30)

            if response.status_code in [200, 204]:
                log.info(f"🗑️ Deleted from Supabase: {safe_filename}")
                return (True, f"File deleted: {safe_filename}")
            else:
                log.error(f"❌ Delete failed: {response.status_code}")
                return (False, f"Delete failed: {response.status_code}")

        except Exception as e:
            log.error(f"❌ Delete error: {e}")
            return (False, f"Delete error: {str(e)}")

    def file_exists(self, filename: str) -> bool:
        """
        Check if a file exists in Supabase Storage.

        Args:
            filename: The filename to check

        Returns:
            True if file exists, False otherwise
        """
        try:
            safe_filename = self.normalize_filename(filename)
            url = self.get_public_url(safe_filename)

            response = requests.head(url, timeout=10)
            return response.status_code == 200

        except Exception as e:
            log.warning(f"Error checking file existence: {e}")
            return False


# Singleton instance
_storage_service: Optional[SupabaseStorageService] = None


def get_supabase_storage_service() -> SupabaseStorageService:
    """Get or create the singleton Supabase Storage Service instance"""
    global _storage_service
    if _storage_service is None:
        _storage_service = SupabaseStorageService()
    return _storage_service
