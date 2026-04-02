"""
Helpers for GenAI credential fallback and temporary cooldowns.
"""

from __future__ import annotations

from dataclasses import dataclass
import threading
import time
from typing import Iterable, List

from config.settings import (
    GEMINI_DEVELOPER_API_VERSION,
    GEMINI_API_KEY,
    GEMINI_API_KEYS,
    GEMINI_KEY_COOLDOWN_SECONDS,
    GENAI_PROVIDER_PRIORITY,
    VERTEX_AI_API_KEYS,
    VERTEX_AI_API_KEY,
    VERTEX_AI_API_VERSION,
    VERTEX_AI_LOCATION,
    VERTEX_AI_PROJECT,
    VERTEX_AI_USE_ADC,
)
from src.utils.logger import log

_key_state_lock = threading.Lock()
_key_cooldowns: dict[str, float] = {}


@dataclass(frozen=True)
class GenAIAuthConfig:
    provider: str
    api_key: str | None = None
    project: str = ""
    location: str = ""
    use_adc: bool = False
    api_version: str = "v1beta"

    @property
    def cooldown_key(self) -> str:
        if self.provider == "vertex" and self.api_key:
            return f"vertex:{self.api_key}"
        if self.provider == "vertex":
            return f"vertex-adc:{self.project}:{self.location}"
        return f"gemini:{self.api_key or ''}"

    @property
    def display_name(self) -> str:
        if self.provider == "vertex":
            if self.api_key:
                return f"vertex:{_mask_secret(self.api_key)}"
            return f"vertex-adc:{self.project or '<project>'}/{self.location or 'global'}"
        return f"gemini:{_mask_secret(self.api_key or '')}"


def _mask_secret(secret: str) -> str:
    if not secret:
        return "<missing>"
    if len(secret) <= 8:
        return f"{secret[:2]}***"
    return f"{secret[:4]}...{secret[-4:]}"


def get_configured_gemini_keys() -> List[str]:
    seen: set[str] = set()
    keys: List[str] = []

    for api_key in GEMINI_API_KEYS or []:
        if api_key and api_key not in seen:
            keys.append(api_key)
            seen.add(api_key)

    if GEMINI_API_KEY and GEMINI_API_KEY not in seen:
        keys.append(GEMINI_API_KEY)

    return keys


def get_configured_vertex_keys() -> List[str]:
    seen: set[str] = set()
    keys: List[str] = []

    for api_key in VERTEX_AI_API_KEYS or []:
        if api_key and api_key not in seen:
            keys.append(api_key)
            seen.add(api_key)

    if VERTEX_AI_API_KEY and VERTEX_AI_API_KEY not in seen:
        keys.append(VERTEX_AI_API_KEY)

    return keys


def get_candidate_gemini_keys() -> List[str]:
    keys = get_configured_gemini_keys()
    if not keys:
        return []

    now = time.time()
    available: List[str] = []
    cooling: List[str] = []

    with _key_state_lock:
        for api_key in keys:
            cooldown_until = _key_cooldowns.get(api_key, 0)
            if cooldown_until > now:
                cooling.append(api_key)
            else:
                available.append(api_key)

    if available:
        return available + cooling

    return keys


def get_candidate_genai_auth_configs() -> List[GenAIAuthConfig]:
    provider_buckets: dict[str, List[GenAIAuthConfig]] = {
        "vertex": [],
        "gemini": [],
    }

    for api_key in get_configured_vertex_keys():
        provider_buckets["vertex"].append(
            GenAIAuthConfig(
                provider="vertex",
                api_key=api_key,
                project=VERTEX_AI_PROJECT,
                location=VERTEX_AI_LOCATION,
                api_version=VERTEX_AI_API_VERSION,
            )
        )

    if VERTEX_AI_USE_ADC:
        provider_buckets["vertex"].append(
            GenAIAuthConfig(
                provider="vertex",
                project=VERTEX_AI_PROJECT,
                location=VERTEX_AI_LOCATION,
                use_adc=True,
                api_version=VERTEX_AI_API_VERSION,
            )
        )

    for api_key in get_configured_gemini_keys():
        provider_buckets["gemini"].append(
            GenAIAuthConfig(
                provider="gemini",
                api_key=api_key,
                api_version=GEMINI_DEVELOPER_API_VERSION,
            )
        )

    ordered_configs: List[GenAIAuthConfig] = []
    seen: set[str] = set()
    provider_order = GENAI_PROVIDER_PRIORITY or ["vertex", "gemini"]

    for provider in provider_order + ["vertex", "gemini"]:
        for config in provider_buckets.get(provider, []):
            if config.cooldown_key not in seen:
                ordered_configs.append(config)
                seen.add(config.cooldown_key)

    if not ordered_configs:
        return []

    now = time.time()
    available: List[GenAIAuthConfig] = []
    cooling: List[GenAIAuthConfig] = []

    with _key_state_lock:
        for config in ordered_configs:
            cooldown_until = _key_cooldowns.get(config.cooldown_key, 0)
            if cooldown_until > now:
                cooling.append(config)
            else:
                available.append(config)

    return available + cooling if available else ordered_configs


def _cooldown_key(resource: str | GenAIAuthConfig) -> str:
    if isinstance(resource, GenAIAuthConfig):
        return resource.cooldown_key
    return resource


def _display_name(resource: str | GenAIAuthConfig) -> str:
    if isinstance(resource, GenAIAuthConfig):
        return resource.display_name
    return _mask_secret(resource)


def mark_key_success(resource: str | GenAIAuthConfig) -> None:
    cooldown_key = _cooldown_key(resource)
    if not cooldown_key:
        return

    with _key_state_lock:
        _key_cooldowns.pop(cooldown_key, None)


def mark_key_failure(
    resource: str | GenAIAuthConfig,
    reason: str,
    cooldown_seconds: int | None = None,
) -> None:
    cooldown_key = _cooldown_key(resource)
    if not cooldown_key:
        return

    cooldown = max(1, cooldown_seconds or GEMINI_KEY_COOLDOWN_SECONDS)
    until = time.time() + cooldown

    with _key_state_lock:
        _key_cooldowns[cooldown_key] = until

    log.warning(
        f"GenAI credential {_display_name(resource)} marked unhealthy for {cooldown}s ({reason})"
    )


def is_retryable_status(status_code: int) -> bool:
    return status_code in (401, 403, 408, 429) or 500 <= status_code <= 599


def build_sync_error_message(
    failures: Iterable[str], fallback_used: bool, context: str
) -> str:
    failure_summary = "; ".join(failures) if failures else "unknown Gemini failure"
    fallback_note = "fallback attempted" if fallback_used else "single key only"
    return f"{context}: {failure_summary} ({fallback_note})"
