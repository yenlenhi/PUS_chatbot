#!/usr/bin/env python3
"""
Rate Limiting Test Script
Tests the rate limiting functionality for various endpoints
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TestResult:
    """Test result for rate limiting"""

    endpoint: str
    method: str
    status_code: int
    response_time: float
    success: bool
    message: str


class RateLimitTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def test_endpoint_rate_limit(
        self,
        endpoint: str,
        method: str = "POST",
        requests_per_minute: int = 10,
        test_duration: int = 60,
        payload: Dict[Any, Any] = None,
        headers: Dict[str, str] = None,
    ) -> List[TestResult]:
        """
        Test rate limiting for a specific endpoint

        Args:
            endpoint: API endpoint to test
            method: HTTP method (GET, POST, etc.)
            requests_per_minute: Expected rate limit
            test_duration: How long to run the test
            payload: Request payload for POST requests
            headers: Request headers
        """
        print(f"\n🧪 Testing rate limit for {method} {endpoint}")
        print(f"Expected limit: {requests_per_minute} requests/minute")

        url = f"{self.base_url}{endpoint}"
        results = []

        # Calculate request intervals to exceed the rate limit
        interval = 60 / (requests_per_minute * 2)  # Send twice as fast as allowed

        def make_request(request_num: int) -> TestResult:
            """Make a single request"""
            start_time = time.time()

            try:
                if method.upper() == "POST":
                    response = self.session.post(
                        url, json=payload, headers=headers, timeout=10
                    )
                elif method.upper() == "GET":
                    response = self.session.get(url, headers=headers, timeout=10)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response_time = time.time() - start_time

                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=response.status_code,
                    response_time=response_time,
                    success=response.status_code != 429,
                    message=response.text[:100] if response.text else "",
                )

            except Exception as e:
                return TestResult(
                    endpoint=endpoint,
                    method=method,
                    status_code=0,
                    response_time=time.time() - start_time,
                    success=False,
                    message=str(e)[:100],
                )

        # Send rapid requests to trigger rate limiting
        start_time = time.time()
        request_count = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []

            while time.time() - start_time < test_duration and request_count < 50:
                future = executor.submit(make_request, request_count)
                futures.append(future)
                request_count += 1
                time.sleep(interval)

                # Process completed requests
                if request_count % 5 == 0:
                    for future in as_completed(futures[:5], timeout=1):
                        try:
                            result = future.get()
                            results.append(result)

                            if result.status_code == 429:
                                print(
                                    f"   ⚡ Request {len(results)} - RATE LIMITED (429)"
                                )
                            elif result.success:
                                print(
                                    f"   ✅ Request {len(results)} - SUCCESS ({result.status_code})"
                                )
                            else:
                                print(
                                    f"   ❌ Request {len(results)} - ERROR ({result.status_code})"
                                )
                        except Exception as e:
                            print(f"   ⚠️  Request error: {e}")

                    futures = futures[5:]

            # Wait for remaining futures
            for future in as_completed(futures, timeout=10):
                try:
                    result = future.get()
                    results.append(result)
                except Exception:
                    pass

        return results

    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results"""
        if not results:
            return {"error": "No results to analyze"}

        total_requests = len(results)
        success_requests = sum(1 for r in results if r.success)
        rate_limited_requests = sum(1 for r in results if r.status_code == 429)
        error_requests = sum(
            1 for r in results if not r.success and r.status_code != 429
        )

        avg_response_time = sum(r.response_time for r in results) / total_requests

        return {
            "total_requests": total_requests,
            "successful_requests": success_requests,
            "rate_limited_requests": rate_limited_requests,
            "error_requests": error_requests,
            "success_rate": (success_requests / total_requests) * 100,
            "rate_limit_triggered": rate_limited_requests > 0,
            "avg_response_time": avg_response_time,
            "endpoint": results[0].endpoint,
            "method": results[0].method,
        }

    def test_login_rate_limit(self):
        """Test login endpoint rate limiting"""
        print("\n🔐 Testing Login Rate Limiting")

        payload = {"username": "invalid_user", "password": "invalid_password"}

        results = self.test_endpoint_rate_limit(
            endpoint="/auth/login",
            method="POST",
            requests_per_minute=5,
            test_duration=30,
            payload=payload,
        )

        return self.analyze_results(results)

    def test_chat_rate_limit(self):
        """Test chat endpoint rate limiting"""
        print("\n💬 Testing Chat Rate Limiting")

        payload = {"message": "Hello, this is a test message", "conversation_id": None}

        results = self.test_endpoint_rate_limit(
            endpoint="/chat",
            method="POST",
            requests_per_minute=60,
            test_duration=30,
            payload=payload,
        )

        return self.analyze_results(results)

    def test_admin_rate_limit(self):
        """Test admin endpoints rate limiting"""
        print("\n👑 Testing Admin Rate Limiting")

        # First, try to login as admin to get a token
        login_payload = {"username": "admin", "password": "Admin123"}

        try:
            login_response = self.session.post(
                f"{self.base_url}/auth/login", json=login_payload, timeout=10
            )

            if login_response.status_code == 200:
                token = login_response.json().get("access_token")
                headers = {"Authorization": f"Bearer {token}"}

                # Test admin user creation
                user_payload = {
                    "username": f"testuser_{int(time.time())}",
                    "password": "TestPassword123",
                    "roles": ["user"],
                }

                results = self.test_endpoint_rate_limit(
                    endpoint="/api/users/admin/users",
                    method="POST",
                    requests_per_minute=3,
                    test_duration=30,
                    payload=user_payload,
                    headers=headers,
                )

                return self.analyze_results(results)
            else:
                return {"error": "Could not authenticate as admin for testing"}

        except Exception as e:
            return {"error": f"Admin test failed: {e}"}

    def run_comprehensive_test(self):
        """Run all rate limiting tests"""
        print("🚀 Starting Comprehensive Rate Limiting Tests")
        print("=" * 60)

        # Test results storage
        test_results = {}

        # Test login rate limiting
        login_results = self.test_login_rate_limit()
        test_results["login"] = login_results

        # Test chat rate limiting
        chat_results = self.test_chat_rate_limit()
        test_results["chat"] = chat_results

        # Test admin rate limiting
        admin_results = self.test_admin_rate_limit()
        test_results["admin"] = admin_results

        # Print summary
        print("\n" + "=" * 60)
        print("📊 RATE LIMITING TEST SUMMARY")
        print("=" * 60)

        for test_name, results in test_results.items():
            if "error" in results:
                print(f"\n❌ {test_name.upper()} TEST - ERROR")
                print(f"   Error: {results['error']}")
                continue

            print(
                f"\n{'✅' if results['rate_limit_triggered'] else '❌'} {test_name.upper()} TEST"
            )
            print(f"   Endpoint: {results['method']} {results['endpoint']}")
            print(f"   Total Requests: {results['total_requests']}")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Rate Limited: {results['rate_limited_requests']}")
            print(
                f"   Rate Limit Working: {'YES' if results['rate_limit_triggered'] else 'NO'}"
            )
            print(f"   Avg Response Time: {results['avg_response_time']:.3f}s")

        return test_results


def main():
    """Main function to run rate limiting tests"""
    import argparse

    parser = argparse.ArgumentParser(description="Test rate limiting functionality")
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL for the API (default: http://localhost:8000)",
    )
    parser.add_argument(
        "--test",
        choices=["login", "chat", "admin", "all"],
        default="all",
        help="Which test to run",
    )

    args = parser.parse_args()

    tester = RateLimitTester(args.url)

    try:
        if args.test == "login":
            results = tester.test_login_rate_limit()
            print(json.dumps(results, indent=2))
        elif args.test == "chat":
            results = tester.test_chat_rate_limit()
            print(json.dumps(results, indent=2))
        elif args.test == "admin":
            results = tester.test_admin_rate_limit()
            print(json.dumps(results, indent=2))
        else:
            results = tester.run_comprehensive_test()

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()
