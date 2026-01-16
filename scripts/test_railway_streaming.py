"""
Simple example to test streaming chat after deployment
Replace YOUR_RAILWAY_URL with your actual Railway URL
"""

import requests
import json
import time


def test_streaming_on_railway():
    # TODO: Replace with your actual Railway URL
    RAILWAY_URL = "https://your-app.railway.app"

    # Or use localhost for local testing
    # RAILWAY_URL = "http://localhost:8000"

    url = f"{RAILWAY_URL}/api/v1/chat/stream"

    payload = {"message": "Điều kiện xét tuyển của trường là gì?", "language": "vi"}

    print("🚀 Testing streaming chat...")
    print(f"📍 URL: {url}\n")

    start_time = time.time()
    first_chunk_time = None

    try:
        response = requests.post(url, json=payload, stream=True, timeout=300)

        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return

        print("✅ Connected! Streaming response:\n")
        print("=" * 80)

        for line in response.iter_lines():
            if line:
                line_str = line.decode("utf-8")

                if line_str.startswith("data: "):
                    data = json.loads(line_str[6:])

                    if data["type"] == "answer_chunk":
                        if first_chunk_time is None:
                            first_chunk_time = time.time()
                            ttfc = first_chunk_time - start_time
                            print(f"\n⏱️ Time to First Chunk: {ttfc:.2f}s\n")

                        print(data["content"], end="", flush=True)

                    elif data["type"] == "done":
                        break

        total_time = time.time() - start_time
        print("\n\n=" * 40)
        print(f"✅ Completed in {total_time:.2f}s")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_streaming_on_railway()
