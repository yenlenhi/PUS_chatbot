"""
Quick test script for suggested questions endpoint
Run this after starting the server with: python main.py
"""

import requests


def test_suggested_questions():
    """Test the suggested questions endpoint"""
    base_url = "http://localhost:8000/api"

    print("=" * 60)
    print("TESTING SUGGESTED QUESTIONS ENDPOINT")
    print("=" * 60)

    # Test 1: Basic request
    print("\n1️⃣ Test: Basic request (limit=5)")
    try:
        response = requests.get(f"{base_url}/analytics/suggested-questions?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {data.get('count')} questions")
            print(f"📦 Cached: {data.get('cached', False)}")
            print(f"⏱️  Cache age: {data.get('cache_age_seconds', 0)}s")
            print("\nQuestions:")
            for i, q in enumerate(data.get("questions", []), 1):
                print(f"  {i}. {q.get('question')}")
                print(
                    f"     Count: {q.get('count')}, Last asked: {q.get('last_asked')}"
                )
        else:
            print(f"❌ Error: Status {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 2: Different limit
    print("\n2️⃣ Test: Different limit (limit=3)")
    try:
        response = requests.get(f"{base_url}/analytics/suggested-questions?limit=3")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {data.get('count')} questions")
            print(f"📦 Cached: {data.get('cached', False)}")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 3: Force refresh
    print("\n3️⃣ Test: Force refresh (force_refresh=true)")
    try:
        response = requests.get(
            f"{base_url}/analytics/suggested-questions?limit=5&force_refresh=true"
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {data.get('count')} questions")
            print(f"📦 Cached: {data.get('cached', False)} (should be False)")
            print(f"⏱️  Cache age: {data.get('cache_age_seconds', 0)}s (should be 0)")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Test 4: Second request (should be cached)
    print("\n4️⃣ Test: Second request (should use cache)")
    try:
        response = requests.get(f"{base_url}/analytics/suggested-questions?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Got {data.get('count')} questions")
            print(f"📦 Cached: {data.get('cached', False)} (should be True)")
            print(f"⏱️  Cache age: {data.get('cache_age_seconds', 0)}s")
        else:
            print(f"❌ Error: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

    print("\n" + "=" * 60)
    print("TESTING COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    print("\n⚠️  Make sure the server is running: python main.py")
    print("⚠️  Server should be at: http://localhost:8000")
    input("\nPress Enter to start testing...")

    test_suggested_questions()
