"""
Shared Google Gen AI client helpers for Gemini Developer API and Vertex AI.
"""

from __future__ import annotations

import base64
from typing import Any, AsyncGenerator, Iterable, Sequence

from google import genai
from google.genai import types

from config.settings import GENAI_MODEL, GENAI_VISION_MODEL
from src.services.gemini_key_fallback import (
    GenAIAuthConfig,
    get_candidate_genai_auth_configs,
    mark_key_failure,
    mark_key_success,
)
from src.utils.logger import log


def get_candidate_auth_configs() -> list[GenAIAuthConfig]:
    return get_candidate_genai_auth_configs()


def build_client(auth: GenAIAuthConfig) -> genai.Client:
    http_options = types.HttpOptions(api_version=auth.api_version)
    client_kwargs: dict[str, Any] = {"http_options": http_options}

    if auth.provider == "vertex":
        client_kwargs["vertexai"] = True
        if auth.api_key:
            client_kwargs["api_key"] = auth.api_key
        if auth.project:
            client_kwargs["project"] = auth.project
        if auth.location:
            client_kwargs["location"] = auth.location
    else:
        client_kwargs["api_key"] = auth.api_key

    return genai.Client(**client_kwargs)


def build_text_config(
    *,
    temperature: float,
    max_output_tokens: int,
    top_p: float = 0.95,
    top_k: int = 40,
    enable_google_search: bool = False,
    response_mime_type: str | None = None,
    response_schema: Any | None = None,
) -> types.GenerateContentConfig:
    config_kwargs: dict[str, Any] = {
        "temperature": temperature,
        "max_output_tokens": max_output_tokens,
        "top_p": top_p,
        "top_k": top_k,
    }
    if enable_google_search:
        config_kwargs["tools"] = [types.Tool(google_search=types.GoogleSearch())]
    if response_mime_type:
        config_kwargs["response_mime_type"] = response_mime_type
    if response_schema is not None:
        config_kwargs["response_schema"] = response_schema
    return types.GenerateContentConfig(**config_kwargs)


def build_multimodal_contents(
    prompt: str,
    images: Sequence[dict[str, str]],
    *,
    prompt_last: bool = True,
) -> list[Any]:
    contents: list[Any] = []
    for image in images:
        image_data = image.get("data", "")
        if not image_data:
            continue
        contents.append(
            types.Part.from_bytes(
                data=base64.b64decode(image_data),
                mime_type=image.get("mime_type", "image/jpeg"),
            )
        )

    if prompt_last:
        contents.append(prompt)
    else:
        contents.insert(0, prompt)

    return contents


def extract_text_from_response(response: Any) -> str:
    text = getattr(response, "text", None)
    if isinstance(text, str):
        return text.strip()

    candidates = getattr(response, "candidates", None) or []
    text_fragments: list[str] = []

    for candidate in candidates:
        content = getattr(candidate, "content", None)
        parts = getattr(content, "parts", None) or []
        for part in parts:
            part_text = getattr(part, "text", None)
            if part_text:
                text_fragments.append(str(part_text))

    return "".join(text_fragments).strip()


def extract_finish_reason(response: Any) -> str:
    candidates = getattr(response, "candidates", None) or []
    if not candidates:
        return ""
    finish_reason = getattr(candidates[0], "finish_reason", "")
    return str(finish_reason or "")


def is_max_tokens_finish_reason(finish_reason: str) -> bool:
    return "MAX_TOKENS" in (finish_reason or "").upper()


def generate_content_once(
    *,
    auth: GenAIAuthConfig,
    model: str,
    contents: Any,
    config: types.GenerateContentConfig,
) -> Any:
    with build_client(auth) as client:
        return client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )


async def generate_content_once_async(
    *,
    auth: GenAIAuthConfig,
    model: str,
    contents: Any,
    config: types.GenerateContentConfig,
) -> Any:
    async with build_client(auth).aio as client:
        return await client.models.generate_content(
            model=model,
            contents=contents,
            config=config,
        )


def generate_content_stream_once(
    *,
    auth: GenAIAuthConfig,
    model: str,
    contents: Any,
    config: types.GenerateContentConfig,
) -> Iterable[Any]:
    with build_client(auth) as client:
        for chunk in client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        ):
            yield chunk


async def generate_content_stream_once_async(
    *,
    auth: GenAIAuthConfig,
    model: str,
    contents: Any,
    config: types.GenerateContentConfig,
) -> AsyncGenerator[Any, None]:
    async with build_client(auth).aio as client:
        stream = await client.models.generate_content_stream(
            model=model,
            contents=contents,
            config=config,
        )
        async for chunk in stream:
            yield chunk


def log_auth_attempt(auth: GenAIAuthConfig, index: int, total: int, operation: str) -> None:
    log.info(f"{operation} using {auth.display_name} ({index}/{total})")


def mark_auth_failure(auth: GenAIAuthConfig, exc: Exception | str) -> None:
    reason = exc if isinstance(exc, str) else type(exc).__name__
    mark_key_failure(auth, str(reason))


def mark_auth_success(auth: GenAIAuthConfig) -> None:
    mark_key_success(auth)


def default_text_model() -> str:
    return GENAI_MODEL


def default_vision_model() -> str:
    return GENAI_VISION_MODEL
