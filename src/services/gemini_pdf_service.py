"""
Gemini PDF Service for extracting text from both regular PDFs and scanned PDFs.
"""

import base64
import io
import json
import re
import threading
import time
import codecs
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pymupdf as fitz  # PyMuPDF for PDF to image conversion
import requests
from PIL import Image, ImageFilter, ImageOps

from config.settings import (
    GEMINI_API_KEY,
    GEMINI_API_URL,
    PDF_GEMINI_MAX_BACKOFF_SECONDS,
    PDF_GEMINI_MAX_RETRIES,
    PDF_GEMINI_PAGE_DELAY_SECONDS,
    GEMINI_MAX_OUTPUT_TOKENS,
    PDF_GEMINI_RENDER_SCALE,
    PDF_GEMINI_REQUEST_INTERVAL_SECONDS,
    PDF_GEMINI_RETRY_DELAY_SECONDS,
    PDF_GEMINI_RATE_LIMIT_COOLDOWN_SECONDS,
)
from src.utils.logger import log

OCR_PROMPT = (
    "Extract every visible character from this Vietnamese administrative/legal PDF page image.\n\n"
    "Requirements:\n"
    "1. Preserve Vietnamese diacritics, numbers, symbols, punctuation, quotation marks, headings, bullets, page numbers, and meaningful line breaks exactly as shown.\n"
    "2. Treat the page as an official legal/administrative document. Preserve the full hierarchy and wording of titles, appendices, articles (Dieu), clauses (Khoan), points (Diem), sub-points, references, dates, and document numbers exactly. Do not skip or compress repeated legal phrasing.\n"
    "3. Never summarize, translate, paraphrase, normalize, modernize, infer missing text, or rewrite citations. Keep quoted passages intact and do not break legal references across unrelated lines.\n"
    "4. Reproduce every table in GitHub-flavored Markdown table format whenever the columns are readable. Keep the original column order, keep each row on one line, preserve blank cells when visible, and preserve captions, notes, and footnotes outside the table.\n"
    "5. If a table cell spans multiple visual lines, join the cell text with <br> instead of dropping content. Do not merge two different rows or two different cells together.\n"
    "6. Keep non-table text in natural reading order and preserve section boundaries so long documents with many numbered items remain complete and traceable.\n"
    "7. Return only the extracted page text in the JSON schema. Do not add commentary, confidence notes, or Markdown fences.\n"
    "8. If no readable text is visible, return has_text=false and an empty text field."
)

OCR_RESPONSE_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "has_text": {"type": "boolean"},
        "text": {"type": "string"},
    },
    "required": ["has_text", "text"],
}

TRANSIENT_STATUS_CODES = {408, 429, 500, 502, 503, 504}


class GeminiPDFService:
    """Service for extracting text from PDFs using Gemini Vision API."""

    _request_gate_lock = threading.Lock()
    _global_next_request_at = 0.0
    _global_cooldown_until = 0.0

    def __init__(self):
        """Initialize Gemini PDF service."""
        if not GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")

        self.api_key = GEMINI_API_KEY
        self.api_url = GEMINI_API_URL
        self.max_retries = max(1, PDF_GEMINI_MAX_RETRIES)
        self.retry_delay = max(0.0, PDF_GEMINI_RETRY_DELAY_SECONDS)
        self.page_delay = max(0.0, PDF_GEMINI_PAGE_DELAY_SECONDS)
        self.min_request_interval = max(0.0, PDF_GEMINI_REQUEST_INTERVAL_SECONDS)
        self.rate_limit_cooldown = max(0.0, PDF_GEMINI_RATE_LIMIT_COOLDOWN_SECONDS)
        self.max_backoff_seconds = max(0.0, PDF_GEMINI_MAX_BACKOFF_SECONDS)
        self.request_timeout = 90
        self.max_output_tokens = max(8192, GEMINI_MAX_OUTPUT_TOKENS)
        self.render_scale = max(1.0, PDF_GEMINI_RENDER_SCALE)
        self.had_rate_limit_errors = False
        self.rate_limited_pages: set[int] = set()

    def _reset_run_state(self) -> None:
        self.had_rate_limit_errors = False
        self.rate_limited_pages = set()

    def _reserve_request_slot(self) -> float:
        """Coordinate OCR requests across concurrent service instances."""
        with self.__class__._request_gate_lock:
            now = time.monotonic()
            available_at = max(
                now,
                self.__class__._global_next_request_at,
                self.__class__._global_cooldown_until,
            )
            self.__class__._global_next_request_at = (
                available_at + self.min_request_interval
            )
        return max(0.0, available_at - now)

    def _wait_for_request_slot(self, page_num: int, attempt_number: int) -> None:
        wait_time = self._reserve_request_slot()
        if wait_time <= 0:
            return
        if wait_time >= 1:
            log.info(
                f"Gemini OCR throttle active on page {page_num}; "
                f"waiting {wait_time:.1f}s before attempt {attempt_number}"
            )
        time.sleep(wait_time)

    def _apply_global_cooldown(self, wait_seconds: float) -> None:
        if wait_seconds <= 0:
            return
        cooldown_until = time.monotonic() + wait_seconds
        with self.__class__._request_gate_lock:
            self.__class__._global_cooldown_until = max(
                self.__class__._global_cooldown_until,
                cooldown_until,
            )

    def _parse_retry_after_seconds(self, response: requests.Response) -> Optional[float]:
        retry_after = getattr(response, "headers", {}).get("Retry-After")
        if not retry_after:
            return None
        try:
            return max(0.0, float(retry_after))
        except (TypeError, ValueError):
            return None

    def _get_transient_wait_seconds(
        self,
        attempt: int,
        status_code: Optional[int] = None,
        response: Optional[requests.Response] = None,
    ) -> float:
        wait_time = self.retry_delay * (2**attempt)
        retry_after_seconds = (
            self._parse_retry_after_seconds(response) if response is not None else None
        )
        if retry_after_seconds is not None:
            wait_time = max(wait_time, retry_after_seconds)
        if status_code == 429:
            wait_time = max(wait_time, self.rate_limit_cooldown)
        if self.max_backoff_seconds > 0:
            wait_time = min(wait_time, self.max_backoff_seconds)
        return max(0.0, wait_time)

    def extract_text_from_pdf(
        self, pdf_path: Path, page_numbers: Optional[Iterable[int]] = None
    ) -> List[Tuple[int, str]]:
        """
        Extract text from PDF using Gemini Vision API.

        Args:
            pdf_path: Path to PDF file
            page_numbers: Optional 1-based page numbers to OCR

        Returns:
            List of tuples (page_number, extracted_text)
        """
        try:
            log.info(f"Extracting text from PDF using Gemini: {pdf_path.name}")
            self._reset_run_state()

            images = self._pdf_to_images(pdf_path, page_numbers=page_numbers)
            if not images:
                log.warning(f"No images extracted from {pdf_path.name}")
                return []

            extracted_pages: List[Tuple[int, str]] = []
            for page_num, image_data in images:
                log.info(f"Processing page {page_num} of {pdf_path.name}")
                text = self._extract_text_from_image(image_data, page_num)
                if text:
                    extracted_pages.append((page_num, text))
                time.sleep(self.page_delay)

            if self.rate_limited_pages:
                affected_pages = sorted(self.rate_limited_pages)
                preview_pages = ", ".join(str(page) for page in affected_pages[:10])
                suffix = "..." if len(affected_pages) > 10 else ""
                log.warning(
                    f"Gemini OCR hit rate limits while processing {pdf_path.name}; "
                    f"affected pages: {preview_pages}{suffix}"
                )

            log.info(f"Successfully extracted text from {len(extracted_pages)} pages")
            return extracted_pages

        except Exception as exc:
            log.error(f"Error extracting text from PDF {pdf_path.name}: {exc}")
            return []

    def _pdf_to_images(
        self, pdf_path: Path, page_numbers: Optional[Iterable[int]] = None
    ) -> List[Tuple[int, str]]:
        """
        Convert PDF pages to base64 encoded images.

        Args:
            pdf_path: Path to PDF file
            page_numbers: Optional 1-based page numbers to convert

        Returns:
            List of tuples (page_number, base64_image_data)
        """
        try:
            images: List[Tuple[int, str]] = []
            selected_pages = set(page_numbers or [])

            with fitz.open(str(pdf_path)) as pdf_document:
                for page_index in range(pdf_document.page_count):
                    page_number = page_index + 1
                    if selected_pages and page_number not in selected_pages:
                        continue

                    page = pdf_document[page_index]
                    matrix = fitz.Matrix(self.render_scale, self.render_scale)
                    pixmap = page.get_pixmap(matrix=matrix, alpha=False)

                    image = Image.open(io.BytesIO(pixmap.tobytes("png")))
                    prepared_image = self._prepare_page_image(image)

                    buffer = io.BytesIO()
                    prepared_image.save(
                        buffer,
                        format="PNG",
                        optimize=True,
                        compress_level=9,
                    )
                    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
                    images.append((page_number, image_base64))

            log.info(f"Converted {len(images)} pages to images")
            return images

        except Exception as exc:
            log.error(f"Error converting PDF to images: {exc}")
            return []

    def _prepare_page_image(self, image: Image.Image) -> Image.Image:
        """Improve scan readability before sending the page image to Gemini."""
        prepared_image = ImageOps.exif_transpose(image)
        grayscale_image = ImageOps.grayscale(prepared_image)
        grayscale_image = ImageOps.autocontrast(grayscale_image)
        grayscale_image = grayscale_image.filter(ImageFilter.SHARPEN)
        return grayscale_image.convert("RGB")

    def _build_ocr_request(self, image_base64: str) -> Dict[str, Any]:
        """Build the OCR request payload with image-first ordering."""
        return {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64,
                            }
                        },
                        {"text": OCR_PROMPT},
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.0,
                "maxOutputTokens": self.max_output_tokens,
                "responseMimeType": "application/json",
                "responseJsonSchema": OCR_RESPONSE_SCHEMA,
            },
        }

    def _normalize_extracted_text(self, text: Optional[str]) -> str:
        if not text:
            return ""
        return str(text).replace("\r\n", "\n").strip()

    def _decode_json_like_string(self, value: str) -> str:
        if not value:
            return ""

        sanitized_value = value.replace("\r\n", "\n").replace("\r", "\n")
        try:
            return json.loads(f'"{sanitized_value}"')
        except json.JSONDecodeError:
            sanitized_value = re.sub(r"\\u([0-9a-fA-F]{0,3})$", "", sanitized_value)
            sanitized_value = re.sub(r"\\x([0-9a-fA-F]?)$", "", sanitized_value)
            sanitized_value = re.sub(r"\\$", "", sanitized_value)
            try:
                return codecs.decode(sanitized_value, "unicode_escape")
            except Exception:
                return sanitized_value

    def _extract_text_fragments_from_json_like_payload(
        self, payload: str
    ) -> List[str]:
        fragments: List[str] = []
        search_start = 0

        while True:
            text_match = re.search(r'"text"\s*:\s*"', payload[search_start:])
            if not text_match:
                break

            fragment_start = search_start + text_match.end()
            cursor = fragment_start
            escaped = False
            fragment_chars: List[str] = []
            closed = False

            while cursor < len(payload):
                char = payload[cursor]
                if escaped:
                    fragment_chars.append(char)
                    escaped = False
                    cursor += 1
                    continue

                if char == "\\":
                    fragment_chars.append(char)
                    escaped = True
                    cursor += 1
                    continue

                if char == '"':
                    closed = True
                    cursor += 1
                    break

                fragment_chars.append(char)
                cursor += 1

            fragment_text = "".join(fragment_chars)
            normalized_fragment = self._normalize_extracted_text(
                self._decode_json_like_string(fragment_text)
            )
            if normalized_fragment:
                fragments.append(normalized_fragment)

            if not closed:
                break
            search_start = cursor

        return fragments

    def _salvage_text_payload(self, payload: str) -> Optional[str]:
        normalized_payload = self._normalize_extracted_text(payload)
        if not normalized_payload:
            return None

        if re.search(r'"has_text"\s*:\s*false', normalized_payload, flags=re.IGNORECASE):
            return None

        fragments = self._extract_text_fragments_from_json_like_payload(
            normalized_payload
        )
        if fragments:
            return "\n\n".join(fragment for fragment in fragments if fragment).strip()

        return None

    def _parse_text_payload(self, raw_text: str) -> Optional[str]:
        normalized_payload = self._normalize_extracted_text(raw_text)
        if not normalized_payload:
            return None

        fenced_payload = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            normalized_payload,
            flags=re.IGNORECASE | re.DOTALL,
        ).strip()

        try:
            parsed_payload = json.loads(fenced_payload)
        except json.JSONDecodeError:
            if normalized_payload.upper() == "NO_TEXT_FOUND":
                return None
            if (
                fenced_payload.startswith("{")
                or fenced_payload.startswith("[")
                or '"has_text"' in fenced_payload
                or '"text"' in fenced_payload
            ):
                return self._salvage_text_payload(fenced_payload)
            return normalized_payload

        if isinstance(parsed_payload, dict):
            extracted_text = self._normalize_extracted_text(parsed_payload.get("text", ""))
            if parsed_payload.get("has_text") is False or not extracted_text:
                return None
            return extracted_text

        if isinstance(parsed_payload, list):
            extracted_fragments = [
                self._normalize_extracted_text(item.get("text", ""))
                for item in parsed_payload
                if isinstance(item, dict) and item.get("has_text") is not False
            ]
            extracted_fragments = [fragment for fragment in extracted_fragments if fragment]
            if extracted_fragments:
                return "\n\n".join(extracted_fragments)
            return None

        if isinstance(parsed_payload, str):
            return self._normalize_extracted_text(parsed_payload)

        return None

    def _extract_text_from_response(
        self, result: Dict[str, Any], page_num: int
    ) -> Optional[str]:
        candidates = result.get("candidates") or []
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts") or []
            finish_reason = candidate.get("finishReason")
            raw_response = "".join(
                part.get("text", "")
                for part in parts
                if isinstance(part, dict) and part.get("text")
            ).strip()

            extracted_text = self._parse_text_payload(raw_response)
            if extracted_text:
                if finish_reason == "MAX_TOKENS":
                    log.warning(
                        f"Gemini OCR hit MAX_TOKENS on page {page_num}; extracted text may be truncated"
                    )
                return extracted_text

            if finish_reason == "MAX_TOKENS":
                log.warning(
                    f"Gemini OCR hit MAX_TOKENS on page {page_num}; output may be truncated"
                )

        return None

    def _extract_text_from_image(
        self, image_base64: str, page_num: int
    ) -> Optional[str]:
        """
        Extract text from image using Gemini Vision API.

        Args:
            image_base64: Base64 encoded image data
            page_num: Page number for logging

        Returns:
            Extracted text or None if failed
        """
        headers = {"Content-Type": "application/json"}
        payload = self._build_ocr_request(image_base64)

        for attempt in range(self.max_retries):
            attempt_number = attempt + 1
            self._wait_for_request_slot(page_num, attempt_number)
            try:
                response = requests.post(
                    f"{self.api_url}?key={self.api_key}",
                    headers=headers,
                    json=payload,
                    timeout=self.request_timeout,
                )

                if response.status_code == 200:
                    try:
                        result = response.json()
                    except ValueError:
                        log.warning(
                            f"Gemini OCR returned non-JSON response on page {page_num}"
                        )
                        return None

                    extracted_text = self._extract_text_from_response(result, page_num)
                    if extracted_text:
                        log.info(f"Successfully extracted text from page {page_num}")
                        return extracted_text

                    log.warning(f"No text found on page {page_num}")
                    return None

                if response.status_code in TRANSIENT_STATUS_CODES:
                    wait_time = self._get_transient_wait_seconds(
                        attempt,
                        status_code=response.status_code,
                        response=response,
                    )
                    if response.status_code == 429:
                        self.had_rate_limit_errors = True
                        self.rate_limited_pages.add(page_num)
                    if attempt < self.max_retries - 1:
                        self._apply_global_cooldown(wait_time)
                        log.warning(
                            f"Gemini OCR transient error on page {page_num}: "
                            f"{response.status_code}. Waiting {wait_time:.1f}s before retry {attempt_number}"
                        )
                        continue
                    log.error(
                        f"Gemini OCR transient error on page {page_num}: "
                        f"{response.status_code}. Exhausted {self.max_retries} attempts"
                    )
                    return None

                log.error(
                    f"Gemini API error for page {page_num}: {response.status_code} - {response.text}"
                )
                return None

            except requests.exceptions.RequestException as exc:
                wait_time = self._get_transient_wait_seconds(attempt)
                if attempt < self.max_retries - 1:
                    self._apply_global_cooldown(wait_time)
                    log.warning(
                        f"Request error for page {page_num}, attempt {attempt_number}: "
                        f"{exc}. Waiting {wait_time:.1f}s before retry {attempt_number}"
                    )
                    continue
                log.error(
                    f"Request error for page {page_num}, attempt {attempt_number}: {exc}"
                )
                return None
            except Exception as exc:
                log.error(f"Unexpected error for page {page_num}: {exc}")
                return None

        log.error(
            f"Failed to extract text from page {page_num} after {self.max_retries} attempts"
        )
        return None

    def batch_extract_from_directory(
        self, pdf_dir: Path
    ) -> Dict[str, List[Tuple[int, str]]]:
        """
        Extract text from all PDFs in a directory.

        Args:
            pdf_dir: Directory containing PDF files

        Returns:
            Dictionary mapping filename to extracted pages
        """
        results: Dict[str, List[Tuple[int, str]]] = {}
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            log.warning(f"No PDF files found in {pdf_dir}")
            return results

        log.info(f"Processing {len(pdf_files)} PDF files from {pdf_dir}")
        for pdf_path in pdf_files:
            try:
                extracted_pages = self.extract_text_from_pdf(pdf_path)
                results[pdf_path.name] = extracted_pages
                time.sleep(1)
            except Exception as exc:
                log.error(f"Error processing {pdf_path.name}: {exc}")
                results[pdf_path.name] = []

        return results
