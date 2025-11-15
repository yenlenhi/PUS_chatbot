"""
Gemini PDF Service for extracting text from both regular PDFs and scanned PDFs
"""

import base64
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import pymupdf as fitz  # PyMuPDF for PDF to image conversion
from PIL import Image
import io
import time

from config.settings import GEMINI_API_KEY, GEMINI_API_URL
from src.utils.logger import log


class GeminiPDFService:
    """Service for extracting text from PDFs using Gemini Vision API"""

    def __init__(self):
        """Initialize Gemini PDF service"""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")

        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL
        self.max_retries = 3
        self.retry_delay = 2  # seconds

    def extract_text_from_pdf(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Extract text from PDF using Gemini Vision API

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tuples (page_number, extracted_text)
        """
        try:
            log.info(f"Extracting text from PDF using Gemini: {pdf_path.name}")

            # Convert PDF pages to images
            images = self._pdf_to_images(pdf_path)
            if not images:
                log.warning(f"No images extracted from {pdf_path.name}")
                return []

            extracted_pages = []

            # Process each page image with Gemini
            for page_num, image_data in images:
                log.info(f"Processing page {page_num} of {pdf_path.name}")

                text = self._extract_text_from_image(image_data, page_num)
                if text:
                    extracted_pages.append((page_num, text))

                # Add delay to avoid rate limiting
                time.sleep(0.5)

            log.info(f"Successfully extracted text from {len(extracted_pages)} pages")
            return extracted_pages

        except Exception as e:
            log.error(f"Error extracting text from PDF {pdf_path.name}: {e}")
            return []

    def _pdf_to_images(self, pdf_path: Path) -> List[Tuple[int, str]]:
        """
        Convert PDF pages to base64 encoded images

        Args:
            pdf_path: Path to PDF file

        Returns:
            List of tuples (page_number, base64_image_data)
        """
        try:
            images = []
            pdf_document = fitz.open(pdf_path)

            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]

                # Convert page to image with high DPI for better OCR
                mat = fitz.Matrix(2.0, 2.0)  # 2x zoom for better quality
                pix = page.get_pixmap(matrix=mat)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                image = Image.open(io.BytesIO(img_data))

                # Convert to RGB if necessary
                if image.mode != "RGB":
                    image = image.convert("RGB")

                # Convert to base64
                buffer = io.BytesIO()
                image.save(buffer, format="PNG", optimize=True, quality=85)
                img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

                images.append((page_num + 1, img_base64))

            pdf_document.close()
            log.info(f"Converted {len(images)} pages to images")
            return images

        except Exception as e:
            log.error(f"Error converting PDF to images: {e}")
            return []

    def _extract_text_from_image(
        self, image_base64: str, page_num: int
    ) -> Optional[str]:
        """
        Extract text from image using Gemini Vision API

        Args:
            image_base64: Base64 encoded image data
            page_num: Page number for logging

        Returns:
            Extracted text or None if failed
        """
        prompt = """
        Hãy trích xuất toàn bộ văn bản từ hình ảnh này một cách chính xác nhất có thể.
        
        Yêu cầu:
        1. Giữ nguyên định dạng và cấu trúc của văn bản
        2. Bao gồm tất cả tiêu đề, đoạn văn, danh sách, bảng biểu
        3. Giữ nguyên số trang, số thứ tự nếu có
        4. Không thêm bình luận hay giải thích
        5. Chỉ trả về văn bản được trích xuất
        
        Nếu không có văn bản trong hình ảnh, hãy trả về "NO_TEXT_FOUND"
        """

        headers = {
            "Content-Type": "application/json",
        }

        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64,
                            }
                        },
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,  # Low temperature for consistent extraction
                "maxOutputTokens": 4096,
            },
        }

        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers=headers,
                    data=json.dumps(data),
                    timeout=60,
                )

                if response.status_code == 200:
                    result = response.json()

                    if "candidates" in result and result["candidates"]:
                        content = result["candidates"][0].get("content", {})
                        if "parts" in content and content["parts"]:
                            extracted_text = content["parts"][0].get("text", "").strip()

                            if extracted_text and extracted_text != "NO_TEXT_FOUND":
                                log.info(
                                    f"Successfully extracted text from page {page_num}"
                                )
                                return extracted_text
                            else:
                                log.warning(f"No text found on page {page_num}")
                                return None

                    log.warning(
                        f"Unexpected response format from Gemini for page {page_num}"
                    )
                    return None

                elif response.status_code == 429:  # Rate limit
                    wait_time = self.retry_delay * (2**attempt)
                    log.warning(
                        f"Rate limited, waiting {wait_time}s before retry {attempt + 1}"
                    )
                    time.sleep(wait_time)
                    continue

                else:
                    log.error(
                        f"Gemini API error for page {page_num}: {response.status_code} - {response.text}"
                    )
                    return None

            except requests.exceptions.RequestException as e:
                log.error(
                    f"Request error for page {page_num}, attempt {attempt + 1}: {e}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return None
            except Exception as e:
                log.error(f"Unexpected error for page {page_num}: {e}")
                return None

        log.error(
            f"Failed to extract text from page {page_num} after {self.max_retries} attempts"
        )
        return None

    def batch_extract_from_directory(
        self, pdf_dir: Path
    ) -> Dict[str, List[Tuple[int, str]]]:
        """
        Extract text from all PDFs in a directory

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            Dictionary mapping filename to extracted pages
        """
        results = {}
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            log.warning(f"No PDF files found in {pdf_dir}")
            return results

        log.info(f"Processing {len(pdf_files)} PDF files from {pdf_dir}")

        for pdf_path in pdf_files:
            try:
                extracted_pages = self.extract_text_from_pdf(pdf_path)
                results[pdf_path.name] = extracted_pages

                # Add delay between files to avoid rate limiting
                time.sleep(1)

            except Exception as e:
                log.error(f"Error processing {pdf_path.name}: {e}")
                results[pdf_path.name] = []

        return results
