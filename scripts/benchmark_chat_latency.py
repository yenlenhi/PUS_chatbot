#!/usr/bin/env python3
"""
Benchmark non-stream chat latency and print stage-by-stage timing summaries.

Examples:
    python scripts/benchmark_chat_latency.py --url http://localhost:8000 --runs 3
    python scripts/benchmark_chat_latency.py --direct --query-file scripts/admission_benchmark_queries.json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List

import requests


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


DEFAULT_QUERY_FILE = Path(__file__).with_name("admission_benchmark_queries.json")
DEFAULT_QUERIES = [
    "Điều kiện tuyển sinh của trường là gì?",
    "Hồ sơ sơ tuyển cần chuẩn bị những gì?",
    "Mốc thời gian nộp hồ sơ và nhập học diễn ra khi nào?",
]


def _print_query_result(index: int, query: str, data: dict, wall_time_ms: float) -> None:
    performance = data.get("performance") or {}
    stages = performance.get("stages") or {}
    print(f"\n[{index}] {query}")
    print(f"  Wall time: {wall_time_ms:.2f} ms")
    print(f"  API processing_time: {(data.get('processing_time') or 0) * 1000:.2f} ms")
    if performance:
        print(f"  Service total_ms: {performance.get('total_ms', 0):.2f} ms")
        print(f"  Response path: {performance.get('response_path', 'unknown')}")
        print(f"  Retrieval cache hit: {performance.get('retrieval_cache_hit', False)}")
        print(
            f"  Attachment skipped: {performance.get('attachment_lookup_skipped', False)}"
        )
        if performance.get("time_to_first_token_ms") is not None:
            print(
                f"  Time to first token: {performance['time_to_first_token_ms']:.2f} ms"
            )
        if stages:
            print("  Stage timings:")
            for stage, duration in stages.items():
                print(f"    - {stage}: {duration:.2f} ms")


def _print_summary(results: Iterable[dict]) -> None:
    results = list(results)
    if not results:
        return

    wall_times = [item["wall_time_ms"] for item in results]
    api_times = [
        item["api_processing_ms"] for item in results if item["api_processing_ms"]
    ]
    service_times = [
        item["service_total_ms"]
        for item in results
        if item["service_total_ms"] is not None
    ]
    per_stage: Dict[str, List[float]] = defaultdict(list)

    for item in results:
        for stage, duration in item["stages"].items():
            per_stage[stage].append(duration)

    print("\n=== Summary ===")
    print(f"Samples: {len(results)}")
    print(f"Wall time avg: {statistics.mean(wall_times):.2f} ms")
    if api_times:
        print(f"API processing avg: {statistics.mean(api_times):.2f} ms")
    if service_times:
        print(f"Service total avg: {statistics.mean(service_times):.2f} ms")

    cache_hits = sum(1 for item in results if item["retrieval_cache_hit"])
    print(f"Retrieval cache hit rate: {cache_hits}/{len(results)}")

    if per_stage:
        print("Average stage timings:")
        for stage in sorted(per_stage):
            values = per_stage[stage]
            print(
                f"  - {stage}: avg={statistics.mean(values):.2f} ms, "
                f"p95={max(values):.2f} ms, n={len(values)}"
            )


def _collect_sample(data: dict, wall_time_ms: float) -> dict:
    performance = data.get("performance") or {}
    return {
        "wall_time_ms": wall_time_ms,
        "api_processing_ms": (data.get("processing_time") or 0) * 1000,
        "service_total_ms": performance.get("total_ms"),
        "stages": performance.get("stages") or {},
        "retrieval_cache_hit": performance.get("retrieval_cache_hit", False),
    }


def run_benchmark_via_api(
    base_url: str, queries: List[str], runs: int, language: str
) -> int:
    endpoint = f"{base_url.rstrip('/')}/api/v1/chat"
    collected: List[dict] = []

    for run in range(runs):
        for index, query in enumerate(queries, start=1):
            payload = {
                "message": query,
                "language": language,
                "conversation_id": f"benchmark-run-{run + 1}-{index}",
                "conversation_history": [],
            }
            started_at = time.perf_counter()
            response = requests.post(endpoint, json=payload, timeout=300)
            wall_time_ms = (time.perf_counter() - started_at) * 1000

            if response.status_code != 200:
                print(f"\n[{index}] {query}")
                print(f"  Request failed with status {response.status_code}")
                print(response.text)
                return 1

            data = response.json()
            _print_query_result(index, query, data, wall_time_ms)
            collected.append(_collect_sample(data, wall_time_ms))

    _print_summary(collected)
    return 0


async def run_benchmark_direct(queries: List[str], runs: int, language: str) -> int:
    try:
        from src.services.async_rag_service import AsyncRAGService
    except ModuleNotFoundError as exc:
        print(
            "Direct benchmark mode requires the project runtime dependencies to be installed."
        )
        print(f"Missing module: {exc.name}")
        return 2

    rag = AsyncRAGService()
    collected: List[dict] = []

    for run in range(runs):
        for index, query in enumerate(queries, start=1):
            started_at = time.perf_counter()
            data = await rag.generate_answer_async(
                query=query,
                conversation_id=f"benchmark-direct-{run + 1}-{index}",
                conversation_history=[],
                language=language,
            )
            wall_time_ms = (time.perf_counter() - started_at) * 1000
            _print_query_result(index, query, data, wall_time_ms)
            collected.append(_collect_sample(data, wall_time_ms))

    _print_summary(collected)
    return 0


def _load_queries(explicit_queries: List[str], query_file: str | None) -> List[str]:
    queries = list(explicit_queries)

    file_to_use = query_file
    if not queries and not file_to_use and DEFAULT_QUERY_FILE.exists():
        file_to_use = str(DEFAULT_QUERY_FILE)

    if file_to_use:
        with open(file_to_use, "r", encoding="utf-8") as handle:
            if file_to_use.endswith(".json"):
                queries.extend(json.load(handle))
            else:
                queries.extend(
                    line.strip() for line in handle.readlines() if line.strip()
                )

    if not queries:
        queries = DEFAULT_QUERIES.copy()

    return queries


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Benchmark chat latency and print stage timings"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--query",
        action="append",
        help="Benchmark a specific query. Can be passed multiple times.",
    )
    parser.add_argument(
        "--query-file",
        help="Path to a JSON or text file containing benchmark queries",
    )
    parser.add_argument("--runs", type=int, default=1, help="Number of benchmark rounds")
    parser.add_argument("--language", default="vi", help="Request language")
    parser.add_argument(
        "--direct",
        action="store_true",
        help="Call AsyncRAGService directly instead of going through HTTP",
    )
    args = parser.parse_args()

    queries = _load_queries(args.query or [], args.query_file)

    if args.direct:
        return asyncio.run(
            run_benchmark_direct(queries, max(args.runs, 1), args.language)
        )

    return run_benchmark_via_api(args.url, queries, max(args.runs, 1), args.language)


if __name__ == "__main__":
    raise SystemExit(main())
