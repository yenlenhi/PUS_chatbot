"""
Test Background Tasks Implementation

Run this script to test the async upload and concurrent chat capabilities.
"""

import requests
import time
import threading
from pathlib import Path
import sys

# Configuration
BASE_URL = "http://localhost:8000"  # Change to Railway URL when testing production
API_BASE = f"{BASE_URL}/api/v1"


def test_upload_async():
    """Test async upload with immediate 202 response"""
    print("\n" + "=" * 60)
    print("TEST 1: Async Upload (202 Accepted)")
    print("=" * 60)

    # Use a test PDF (create a dummy one if needed)
    test_pdf = Path("test_upload.pdf")
    if not test_pdf.exists():
        print(f"⚠️  Test PDF not found: {test_pdf}")
        print("Creating dummy PDF...")
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(test_pdf))
        c.drawString(100, 750, "Test Document for Background Tasks")
        c.drawString(100, 730, "This document tests async upload processing.")
        c.save()

    # Upload file
    with open(test_pdf, "rb") as f:
        files = {"file": (test_pdf.name, f, "application/pdf")}
        data = {"category": "Test", "use_gemini": "false"}

        print(f"\n📤 Uploading {test_pdf.name}...")
        start = time.time()

        response = requests.post(f"{API_BASE}/admin/upload", files=files, data=data)

        upload_time = time.time() - start

        print(f"⏱️  Upload response time: {upload_time:.2f}s")

        if response.status_code == 202:
            print("✅ SUCCESS: Received 202 Accepted (async processing)")
            result = response.json()
            task_id = result.get("task_id")
            print(f"📋 Task ID: {task_id}")
            print(f"🔗 Status endpoint: {result.get('status_endpoint')}")

            if upload_time < 2.0:
                print(f"✅ PASS: Response time < 2s ({upload_time:.2f}s)")
            else:
                print(f"⚠️  SLOW: Response time > 2s ({upload_time:.2f}s)")

            return task_id
        else:
            print(f"❌ FAILED: Expected 202, got {response.status_code}")
            print(f"Response: {response.text}")
            return None


def test_upload_status(task_id):
    """Test status endpoint with progress tracking"""
    print("\n" + "=" * 60)
    print("TEST 2: Status Tracking")
    print("=" * 60)

    if not task_id:
        print("❌ No task_id, skipping status test")
        return False

    print(f"\n🔍 Monitoring task: {task_id}")

    for i in range(30):  # Poll for up to 5 minutes
        response = requests.get(f"{API_BASE}/admin/upload/status/{task_id}")

        if response.status_code != 200:
            print(f"❌ Status check failed: {response.status_code}")
            return False

        task = response.json()
        status = task.get("status")
        progress = task.get("progress", 0)

        print(f"  [{i+1}/30] Status: {status:12s} Progress: {progress:3d}%", end="\r")

        if status == "COMPLETED":
            print("\n✅ SUCCESS: Task completed")
            result = task.get("result", {})
            print(f"   Chunks created: {result.get('chunks_created', 0)}")
            print(f"   Embeddings: {result.get('embeddings_created', 0)}")
            return True
        elif status == "FAILED":
            print("\n❌ FAILED: Task failed")
            print(f"   Error: {task.get('result', {}).get('error', 'Unknown')}")
            return False

        time.sleep(10)  # Check every 10 seconds

    print("\n⚠️  TIMEOUT: Task still processing after 5 minutes")
    return False


def test_concurrent_chat(num_requests=10):
    """Test concurrent chat requests during upload processing"""
    print("\n" + "=" * 60)
    print(f"TEST 3: Concurrent Chat ({num_requests} requests)")
    print("=" * 60)

    results = []

    def send_chat(idx):
        """Send a chat request and record timing"""
        start = time.time()
        try:
            response = requests.post(
                f"{API_BASE}/chat",
                json={
                    "message": f"Test message {idx}: Học phí năm 2024?",
                    "conversation_id": f"test-{idx}",
                },
                timeout=30,
            )
            elapsed = time.time() - start

            if response.status_code == 200:
                results.append(
                    {
                        "idx": idx,
                        "success": True,
                        "time": elapsed,
                        "status": response.status_code,
                    }
                )
                print(f"  ✅ Request {idx:2d}: {elapsed:5.2f}s")
            else:
                results.append(
                    {
                        "idx": idx,
                        "success": False,
                        "time": elapsed,
                        "status": response.status_code,
                    }
                )
                print(f"  ❌ Request {idx:2d}: HTTP {response.status_code}")
        except Exception as e:
            elapsed = time.time() - start
            results.append(
                {"idx": idx, "success": False, "time": elapsed, "error": str(e)}
            )
            print(f"  ❌ Request {idx:2d}: {str(e)[:50]}")

    print(f"\n🚀 Sending {num_requests} concurrent chat requests...")
    start_time = time.time()

    # Send requests concurrently
    threads = []
    for i in range(num_requests):
        t = threading.Thread(target=send_chat, args=(i,))
        t.start()
        threads.append(t)
        time.sleep(0.1)  # Slight stagger to avoid overwhelming

    # Wait for all to complete
    for t in threads:
        t.join()

    total_time = time.time() - start_time

    # Analyze results
    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    print("\n📊 Results:")
    print(f"   Total requests: {num_requests}")
    print(f"   Successful: {len(successful)}")
    print(f"   Failed: {len(failed)}")
    print(f"   Success rate: {len(successful)/num_requests*100:.1f}%")
    print(f"   Total time: {total_time:.2f}s")

    if successful:
        avg_time = sum(r["time"] for r in successful) / len(successful)
        max_time = max(r["time"] for r in successful)
        min_time = min(r["time"] for r in successful)

        print("\n⏱️  Response times:")
        print(f"   Average: {avg_time:.2f}s")
        print(f"   Min: {min_time:.2f}s")
        print(f"   Max: {max_time:.2f}s")

        if len(successful) == num_requests:
            print(f"\n✅ PASS: All {num_requests} concurrent requests succeeded")
            return True
        else:
            print(f"\n⚠️  PARTIAL: {len(failed)}/{num_requests} requests failed")
            return False
    else:
        print("\n❌ FAIL: No successful requests")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BACKGROUND TASKS IMPLEMENTATION TEST SUITE")
    print("=" * 60)
    print(f"Testing against: {BASE_URL}")

    # Test 1: Async upload
    task_id = test_upload_async()

    # Test 2: Status tracking
    if task_id:
        status_success = test_upload_status(task_id)
    else:
        status_success = False

    # Test 3: Concurrent chat
    chat_success = test_concurrent_chat(num_requests=10)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"1. Async Upload:      {'✅ PASS' if task_id else '❌ FAIL'}")
    print(f"2. Status Tracking:   {'✅ PASS' if status_success else '❌ FAIL'}")
    print(f"3. Concurrent Chat:   {'✅ PASS' if chat_success else '❌ FAIL'}")

    all_passed = task_id and status_success and chat_success

    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Background tasks working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED. Check output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
