#!/usr/bin/env python3
"""
Test script to simulate frontend API calls
"""

import requests


def test_dashboard_apis():
    """Test all APIs that dashboard uses"""
    print("🎭 Simulating Dashboard API Calls\n")

    BASE_URL = "http://localhost:8000/api/v1"

    # Test all dashboard APIs
    apis = [
        ("/analytics/overview", "Dashboard Overview"),
        ("/analytics/users?time_range=L7D", "User Insights"),
        (
            "/analytics/popular-questions?time_range=L7D&limit=5",
            "Popular Questions (New)",
        ),
    ]

    for endpoint, name in apis:
        print(f"🔍 Testing {name}...")
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {name}: SUCCESS")

                # Print specific data for each endpoint
                if "overview" in endpoint:
                    print(
                        f"  📊 Total conversations: {data.get('total_conversations', 0)}"
                    )

                elif "users" in endpoint:
                    pq = data.get("popular_questions", [])
                    print(f"  👥 Popular questions count: {len(pq)}")
                    if pq:
                        print(f"  💬 Sample: {pq[0]['question'][:50]}...")

                elif "popular-questions" in endpoint:
                    print(f"  🗄️ Data source: {data.get('data_source', 'unknown')}")
                    print(f"  📈 Total count: {data.get('total_count', 0)}")
                    questions = data.get("popular_questions", [])
                    if questions:
                        print(f"  ❓ Top question: {questions[0]['question'][:60]}...")
                        print(f"  🔢 Question count: {questions[0]['count']} times")

            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                print(f"  Response: {response.text[:100]}...")

        except requests.exceptions.ConnectionError:
            print(f"❌ {name}: Cannot connect to server")
        except Exception as e:
            print(f"❌ {name}: {e}")

        print()

    print("🏁 API testing completed!")


def compare_data_sources():
    """Compare old vs new popular questions data"""
    print("\n🔄 Comparing Data Sources...\n")

    try:
        # Get data from user insights (old way)
        user_response = requests.get(
            "http://localhost:8000/api/v1/analytics/users?time_range=L7D", timeout=10
        )
        if user_response.status_code == 200:
            user_data = user_response.json()
            old_questions = user_data.get("popular_questions", [])
            print(f"📊 OLD method (user insights): {len(old_questions)} questions")
            for i, q in enumerate(old_questions[:3]):
                print(f"  {i+1}. {q['question'][:50]}... ({q['count']} times)")

        # Get data from new endpoint
        popular_response = requests.get(
            "http://localhost:8000/api/v1/analytics/popular-questions?time_range=L7D&limit=10",
            timeout=10,
        )
        if popular_response.status_code == 200:
            popular_data = popular_response.json()
            new_questions = popular_data.get("popular_questions", [])
            print(
                f"\n🆕 NEW method (popular questions): {len(new_questions)} questions"
            )
            print(f"Data source: {popular_data.get('data_source', 'unknown')}")
            for i, q in enumerate(new_questions[:3]):
                print(f"  {i+1}. {q['question'][:50]}... ({q['count']} times)")

            # Comparison
            print("\n📋 COMPARISON:")
            print(f"  Old method: {len(old_questions)} questions")
            print(
                f"  New method: {len(new_questions)} questions ({'real' if popular_data.get('data_source') == 'real' else 'sample'} data)"
            )

            if popular_data.get("data_source") == "real":
                print("✅ SUCCESS: Using real data from database!")
            else:
                print(
                    "⚠️ Note: Still using sample data - may need more real conversations"
                )

    except Exception as e:
        print(f"❌ Comparison failed: {e}")


if __name__ == "__main__":
    test_dashboard_apis()
    compare_data_sources()
