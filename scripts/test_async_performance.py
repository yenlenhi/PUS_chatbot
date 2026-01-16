#!/usr/bin/env python3
"""
Async Database Performance Test Script
Tests the performance difference between sync and async database operations
"""

import asyncio
import time
import statistics
from typing import List
from src.services.postgres_database_service import PostgresDatabaseService
from src.services.async_postgres_database_service import AsyncPostgresDatabaseService
from src.utils.logger import log


class DatabasePerformanceTester:
    """Test performance of sync vs async database operations"""

    def __init__(self):
        self.sync_db = None
        self.async_db = None

    async def setup(self):
        """Setup database connections"""
        try:
            # Setup sync database
            self.sync_db = PostgresDatabaseService()
            log.info("✅ Sync database initialized")

            # Setup async database
            self.async_db = AsyncPostgresDatabaseService()
            await self.async_db.initialize()
            log.info("✅ Async database initialized")

        except Exception as e:
            log.error(f"❌ Setup failed: {e}")
            raise

    def test_sync_operations(self, num_operations: int = 10) -> List[float]:
        """Test sync database operations"""
        log.info(f"Testing {num_operations} sync operations...")
        times = []

        for i in range(num_operations):
            start_time = time.time()

            try:
                # Simulate typical sync database operation
                with self.sync_db.engine.connect() as conn:
                    result = conn.execute(
                        self.sync_db._text(
                            "SELECT COUNT(*) FROM chunks WHERE id > :id"
                        ),
                        {"id": i},
                    )
                    result.fetchone()

                end_time = time.time()
                operation_time = end_time - start_time
                times.append(operation_time)

            except Exception as e:
                log.error(f"Sync operation {i} failed: {e}")
                times.append(float("inf"))

        return times

    async def test_async_operations(self, num_operations: int = 10) -> List[float]:
        """Test async database operations"""
        log.info(f"Testing {num_operations} async operations...")
        times = []

        for i in range(num_operations):
            start_time = time.time()

            try:
                # Simulate typical async database operation
                async with self.async_db.get_session() as session:
                    from sqlalchemy import text

                    result = await session.execute(
                        text("SELECT COUNT(*) FROM chunks WHERE id > :id"), {"id": i}
                    )
                    result.fetchone()

                end_time = time.time()
                operation_time = end_time - start_time
                times.append(operation_time)

            except Exception as e:
                log.error(f"Async operation {i} failed: {e}")
                times.append(float("inf"))

        return times

    async def test_concurrent_async_operations(
        self, num_operations: int = 10
    ) -> List[float]:
        """Test concurrent async database operations"""
        log.info(f"Testing {num_operations} concurrent async operations...")

        async def single_async_operation(operation_id: int) -> float:
            """Single async operation"""
            start_time = time.time()

            try:
                async with self.async_db.get_session() as session:
                    from sqlalchemy import text

                    result = await session.execute(
                        text("SELECT COUNT(*) FROM chunks WHERE id > :id"),
                        {"operation_id": operation_id},
                    )
                    result.fetchone()

                end_time = time.time()
                return end_time - start_time

            except Exception as e:
                log.error(f"Concurrent async operation {operation_id} failed: {e}")
                return float("inf")

        # Run all operations concurrently
        start_time = time.time()
        tasks = [single_async_operation(i) for i in range(num_operations)]
        times = await asyncio.gather(*tasks)
        total_time = time.time() - start_time

        log.info(
            f"Total time for {num_operations} concurrent operations: {total_time:.3f}s"
        )
        return times

    def analyze_performance(
        self,
        sync_times: List[float],
        async_times: List[float],
        concurrent_times: List[float],
    ) -> dict:
        """Analyze performance results"""

        def calculate_stats(times: List[float]) -> dict:
            """Calculate statistics for operation times"""
            valid_times = [t for t in times if t != float("inf")]
            if not valid_times:
                return {"error": "No valid measurements"}

            return {
                "count": len(valid_times),
                "mean": statistics.mean(valid_times),
                "median": statistics.median(valid_times),
                "min": min(valid_times),
                "max": max(valid_times),
                "stdev": statistics.stdev(valid_times) if len(valid_times) > 1 else 0,
            }

        sync_stats = calculate_stats(sync_times)
        async_stats = calculate_stats(async_times)
        concurrent_stats = calculate_stats(concurrent_times)

        return {
            "sync_operations": sync_stats,
            "async_operations": async_stats,
            "concurrent_async_operations": concurrent_stats,
            "performance_improvement": {
                "async_vs_sync": {
                    "speedup": sync_stats.get("mean", 0) / async_stats.get("mean", 1),
                    "difference_ms": (
                        sync_stats.get("mean", 0) - async_stats.get("mean", 0)
                    )
                    * 1000,
                },
                "concurrent_vs_sequential": {
                    "speedup": (async_stats.get("mean", 0) * len(concurrent_times))
                    / sum(concurrent_times),
                    "total_time_reduction": (
                        async_stats.get("mean", 0) * len(concurrent_times)
                    )
                    - sum(concurrent_times),
                },
            },
        }

    async def run_full_test(self, num_operations: int = 20):
        """Run comprehensive async vs sync performance test"""
        log.info("🚀 Starting Database Performance Test")
        log.info("=" * 60)

        await self.setup()

        # Test sync operations
        log.info("\n📊 Testing Synchronous Operations")
        sync_times = self.test_sync_operations(num_operations)

        # Test async operations (sequential)
        log.info("\n📊 Testing Asynchronous Operations (Sequential)")
        async_times = await self.test_async_operations(num_operations)

        # Test async operations (concurrent)
        log.info("\n📊 Testing Asynchronous Operations (Concurrent)")
        concurrent_times = await self.test_concurrent_async_operations(num_operations)

        # Analyze results
        results = self.analyze_performance(sync_times, async_times, concurrent_times)

        # Print results
        self.print_results(results)

        return results

    def print_results(self, results: dict):
        """Print formatted test results"""
        print("\n" + "=" * 60)
        print("📈 DATABASE PERFORMANCE TEST RESULTS")
        print("=" * 60)

        # Sync results
        sync_stats = results["sync_operations"]
        print("\n🔄 SYNCHRONOUS OPERATIONS")
        if "error" not in sync_stats:
            print(f"   Operations: {sync_stats['count']}")
            print(f"   Mean time: {sync_stats['mean']*1000:.2f} ms")
            print(f"   Median time: {sync_stats['median']*1000:.2f} ms")
            print(
                f"   Range: {sync_stats['min']*1000:.2f} - {sync_stats['max']*1000:.2f} ms"
            )
            print(f"   Std Dev: {sync_stats['stdev']*1000:.2f} ms")
        else:
            print(f"   ❌ {sync_stats['error']}")

        # Async results
        async_stats = results["async_operations"]
        print("\n⚡ ASYNCHRONOUS OPERATIONS (Sequential)")
        if "error" not in async_stats:
            print(f"   Operations: {async_stats['count']}")
            print(f"   Mean time: {async_stats['mean']*1000:.2f} ms")
            print(f"   Median time: {async_stats['median']*1000:.2f} ms")
            print(
                f"   Range: {async_stats['min']*1000:.2f} - {async_stats['max']*1000:.2f} ms"
            )
            print(f"   Std Dev: {async_stats['stdev']*1000:.2f} ms")
        else:
            print(f"   ❌ {async_stats['error']}")

        # Concurrent async results
        concurrent_stats = results["concurrent_async_operations"]
        print("\n🚀 ASYNCHRONOUS OPERATIONS (Concurrent)")
        if "error" not in concurrent_stats:
            print(f"   Operations: {concurrent_stats['count']}")
            print(f"   Mean time: {concurrent_stats['mean']*1000:.2f} ms")
            print(f"   Median time: {concurrent_stats['median']*1000:.2f} ms")
            print(
                f"   Range: {concurrent_stats['min']*1000:.2f} - {concurrent_stats['max']*1000:.2f} ms"
            )
            print(f"   Std Dev: {concurrent_stats['stdev']*1000:.2f} ms")
        else:
            print(f"   ❌ {concurrent_stats['error']}")

        # Performance improvements
        improvements = results["performance_improvement"]
        print("\n🎯 PERFORMANCE COMPARISON")

        async_vs_sync = improvements["async_vs_sync"]
        print("   Async vs Sync:")
        print(f"     Speedup: {async_vs_sync['speedup']:.2f}x")
        print(f"     Time saved: {async_vs_sync['difference_ms']:.2f} ms per operation")

        concurrent_vs_sequential = improvements["concurrent_vs_sequential"]
        print("   Concurrent vs Sequential:")
        print(f"     Speedup: {concurrent_vs_sequential['speedup']:.2f}x")
        print(
            f"     Total time saved: {concurrent_vs_sequential['total_time_reduction']:.3f}s"
        )

        # Recommendations
        print("\n💡 RECOMMENDATIONS")
        if async_vs_sync["speedup"] > 1.1:
            print("   ✅ Async operations show significant improvement")
            print("   → Use async/await for database operations")
        else:
            print("   ⚠️  Async operations show minimal improvement")
            print("   → Consider other optimization strategies")

        if concurrent_vs_sequential["speedup"] > 2:
            print("   ✅ Concurrent operations provide excellent speedup")
            print("   → Use asyncio.gather() for independent operations")
        else:
            print("   ⚠️  Concurrent operations show limited improvement")
            print("   → Check for database connection bottlenecks")

    async def cleanup(self):
        """Cleanup database connections"""
        if self.async_db:
            await self.async_db.close()


async def main():
    """Main function to run performance tests"""
    tester = DatabasePerformanceTester()

    try:
        results = await tester.run_full_test(num_operations=20)

        print("\n🔍 For detailed analysis, check the logs above")
        print("💾 Results can be saved by redirecting output to a file")

    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        log.error(f"Performance test error: {e}")
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
