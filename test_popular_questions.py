#!/usr/bin/env python3
"""
Test script for the new popular questions endpoint
"""

import requests
from src.services.analytics_service import AnalyticsService
from src.models.analytics import TimeRange


def test_analytics_service():
    """Test the AnalyticsService directly"""
    print("🧪 Testing AnalyticsService...")

    try:
        analytics_svc = AnalyticsService()

        # Test get_real_popular_questions
        print("📊 Testing get_real_popular_questions...")
        questions = analytics_svc.get_real_popular_questions(
            TimeRange.LAST_7_DAYS, limit=5
        )

        print(f"✅ Found {len(questions)} popular questions")
        for i, q in enumerate(questions[:3]):
            print(f"  {i+1}. {q.question[:50]}... (count: {q.count})")

        if not questions:
            print("⚠️ No real questions found, testing fallback...")
            fallback = analytics_svc._generate_sample_popular_questions()
            print(f"📝 Fallback generated {len(fallback)} sample questions")

    except Exception as e:
        print(f"❌ Error testing AnalyticsService: {e}")


def test_api_endpoint():
    """Test the API endpoint"""
    print("\n🌐 Testing API endpoint...")

    try:
        # Test new popular questions endpoint
        url = "http://localhost:8000/api/v1/analytics/popular-questions"
        params = {"time_range": "L7D", "limit": 5}

        print(f"📡 Making request to {url}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            print("✅ API response successful")
            print(f"📊 Data source: {data.get('data_source', 'unknown')}")
            print(f"📊 Total count: {data.get('total_count', 0)}")

            questions = data.get("popular_questions", [])
            for i, q in enumerate(questions[:3]):
                print(
                    f"  {i+1}. {q.get('question', '')[:50]}... (count: {q.get('count', 0)})"
                )

        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Cannot connect to API. Make sure the server is running on localhost:8000"
        )
    except Exception as e:
        print(f"❌ Error testing API endpoint: {e}")


def check_database_data():
    """Check if there's actual data in conversations table"""
    print("\n🗃️ Checking database data...")

    try:
        analytics_svc = AnalyticsService()

        with analytics_svc.db_service.engine.connect() as conn:
            from sqlalchemy import text

            # Check if conversations table exists and has data
            result = conn.execute(text("SELECT COUNT(*) FROM conversations"))
            count = result.fetchone()[0]
            print(f"📊 Total conversations in database: {count}")

            if count > 0:
                # Get some sample data
                result = conn.execute(
                    text(
                        """
                    SELECT user_message, COUNT(*) as freq 
                    FROM conversations 
                    WHERE LENGTH(TRIM(user_message)) > 5
                    GROUP BY user_message 
                    ORDER BY freq DESC 
                    LIMIT 5
                """
                    )
                )

                print("📝 Sample frequent questions:")
                for row in result.fetchall():
                    msg = row[0][:60] + "..." if len(row[0]) > 60 else row[0]
                    print(f"  - {msg} ({row[1]} times)")
            else:
                print("⚠️ No conversation data found in database")

    except Exception as e:
        print(f"❌ Error checking database: {e}")


if __name__ == "__main__":
    print("🚀 Testing Popular Questions Implementation\n")

    # Test in order
    check_database_data()
    test_analytics_service()
    test_api_endpoint()

    print("\n✅ Testing completed!")
