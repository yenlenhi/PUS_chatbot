"""
Test script for streaming chat endpoint
"""

import requests
import json
import time
import sys


def test_streaming_chat(message: str, base_url: str = "http://localhost:8000"):
    """
    Test the streaming chat endpoint

    Args:
        message: The message to send
        base_url: Base URL of the API
    """
    print(f"🚀 Testing streaming chat with message: '{message}'\n")
    print("=" * 80)

    url = f"{base_url}/api/v1/chat/stream"

    payload = {"message": message, "language": "vi"}

    start_time = time.time()
    first_chunk_time = None
    full_answer = ""
    sources = []
    attachments = []
    confidence = 0.0
    performance = None

    try:
        response = requests.post(url, json=payload, stream=True, timeout=300)

        if response.status_code != 200:
            print(f"❌ Error: Status code {response.status_code}")
            print(response.text)
            return

        print("✅ Connected to streaming endpoint\n")

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")

                # Parse SSE format
                if line_str.startswith("data: "):
                    json_str = line_str[6:]  # Remove "data: " prefix

                    try:
                        data = json.loads(json_str)
                        event_type = data.get("type")

                        if event_type == "metadata":
                            print(
                                f"📋 Metadata: conversation_id={data.get('conversation_id')}"
                            )
                            print()

                        elif event_type == "status":
                            print(f"ℹ️  Status: {data.get('message')}")

                        elif event_type == "sources":
                            sources = data.get("sources", [])
                            confidence = data.get("confidence", 0.0)
                            print(f"\n📚 Sources ({len(sources)}):")
                            for source in sources:
                                print(f"   - {source}")
                            print(f"📊 Confidence: {confidence:.2%}\n")
                            print("💬 Answer:")
                            print("-" * 80)

                        elif event_type == "answer_chunk":
                            chunk = data.get("content", "")
                            full_answer += chunk

                            # Record time to first chunk
                            if first_chunk_time is None:
                                first_chunk_time = time.time()
                                ttfc = first_chunk_time - start_time
                                print(
                                    f"\n⏱️  Time to First Chunk: {ttfc:.2f}s\n",
                                    file=sys.stderr,
                                )

                            # Print chunk
                            print(chunk, end="", flush=True)

                        elif event_type == "complete":
                            attachments = data.get("attachments", [])
                            chart_data = data.get("chart_data", [])
                            performance = data.get("performance")

                            print("\n" + "-" * 80)
                            print()

                            if attachments:
                                print(f"📎 Attachments ({len(attachments)}):")
                                for att in attachments:
                                    print(
                                        f"   - {att.get('file_name')} ({att.get('file_type')})"
                                    )
                                print()

                            if chart_data:
                                print(f"📊 Charts ({len(chart_data)}):")
                                for chart in chart_data:
                                    print(f"   - {chart.get('title')}")
                                print()

                        elif event_type == "done":
                            print("✅ Streaming completed\n")
                            break

                        elif event_type == "error":
                            print(f"\n❌ Error: {data.get('message')}\n")
                            break

                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse JSON: {e}")
                        continue

        # Calculate total time
        end_time = time.time()
        total_time = end_time - start_time
        ttfc = first_chunk_time - start_time if first_chunk_time else total_time

        print("=" * 80)
        print("\n📊 Performance Metrics:")
        print(f"   ⏱️  Time to First Chunk (TTFC): {ttfc:.2f}s")
        print(f"   ⌛ Total Time: {total_time:.2f}s")
        print(f"   📝 Answer Length: {len(full_answer)} characters")
        print(f"   📚 Sources: {len(sources)}")
        print(f"   📎 Attachments: {len(attachments)}")
        print(f"   📊 Confidence: {confidence:.2%}")
        if performance:
            print(f"   🧭 Response Path: {performance.get('response_path')}")
            print(
                f"   ⚡ Retrieval Cache Hit: {performance.get('retrieval_cache_hit', False)}"
            )
            if performance.get("time_to_first_token_ms") is not None:
                print(
                    f"   🚀 Time to First Token (server): {performance['time_to_first_token_ms']:.2f} ms"
                )
            print("   🧩 Stage Timings:")
            for stage, duration in performance.get("stages", {}).items():
                print(f"      - {stage}: {duration:.2f} ms")

        # Calculate streaming speed
        if ttfc > 0 and total_time > ttfc:
            streaming_duration = total_time - ttfc
            chars_per_second = (
                len(full_answer) / streaming_duration if streaming_duration > 0 else 0
            )
            print(f"   ⚡ Streaming Speed: {chars_per_second:.0f} chars/s")

        print()

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Request error: {e}\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")


def test_multiple_queries():
    """Test with multiple queries to compare performance"""
    queries = [
        "Điều kiện xét tuyển của trường là gì?",
        "Học phí đại học là bao nhiêu?",
        "Các ngành đào tạo của trường?",
    ]

    print("🧪 Testing Multiple Queries\n")
    print("=" * 80)

    for i, query in enumerate(queries, 1):
        print(f"\n\n🔹 Test {i}/{len(queries)}")
        print("=" * 80)
        test_streaming_chat(query)
        print("\n")
        time.sleep(2)  # Wait between tests


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test streaming chat endpoint")
    parser.add_argument(
        "--message",
        type=str,
        default="Điều kiện xét tuyển của trường là gì?",
        help="Message to send to the chatbot",
    )
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000",
        help="Base URL of the API",
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Test with multiple queries",
    )

    args = parser.parse_args()

    if args.multiple:
        test_multiple_queries()
    else:
        test_streaming_chat(args.message, args.url)
