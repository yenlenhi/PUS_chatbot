#!/usr/bin/env python3
"""
Debug health check to see which component is unhealthy
"""
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, ".")

from src.services.rag_service import RAGService
import json

print("\n" + "=" * 60)
print("DEBUGGING HEALTH CHECK")
print("=" * 60)

try:
    # Initialize RAGService
    print("\n[1] Initializing RAGService...")
    rag = RAGService()
    print("   [OK] RAGService initialized")

    # Check system health
    print("\n[2] Checking system health...")
    health = rag.check_system_health()

    print("\n[HEALTH STATUS DETAILS]")
    print(json.dumps(health, indent=2, ensure_ascii=False))

    print("\n[3] Component Status Summary:")
    for component, details in health.get("components", {}).items():
        status = details.get("status", "unknown")
        emoji = (
            "[OK]"
            if status == "healthy"
            else "[FAIL]" if status == "unhealthy" else "[WARN]"
        )
        print(f"   {emoji} {component}: {status}")
        if status != "healthy" and "error" in details:
            print(f"      Error: {details['error']}")

    print(f"\n[4] Overall Status: {health.get('overall_status')}")

except Exception as e:
    print(f"[ERROR] {e}")
    import traceback

    traceback.print_exc()

print("\n" + "=" * 60 + "\n")
