#!/usr/bin/env python3
"""
Test Runner for Pipecat ECS Deployment

Runs all tests in sequence and provides a summary report.
"""

import subprocess
import sys
import time
from pathlib import Path


def run_test(test_file: str) -> tuple[bool, str, float]:
    """Run a single test file and return results."""
    print(f"\n{'='*60}")
    print(f"Running: {test_file}")
    print("=" * 60)

    start_time = time.time()

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
        )

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ PASSED: {test_file} ({duration:.1f}s)")
            return True, result.stdout, duration
        else:
            print(f"❌ FAILED: {test_file} ({duration:.1f}s)")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False, result.stderr, duration

    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ TIMEOUT: {test_file} ({duration:.1f}s)")
        return False, "Test timed out after 5 minutes", duration
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 ERROR: {test_file} ({duration:.1f}s) - {str(e)}")
        return False, str(e), duration


def main():
    """Run all tests and provide summary."""
    tests_dir = Path(__file__).parent

    # Define test order (most basic to most comprehensive)
    test_files = [
        "test-bedrock-access.py",
        "test-secrets-integration.py",
        "test-specific-functionality.py",
        "test-complete-user-journey.py",
        "test-end-to-end.py",
    ]

    print("🚀 Starting Pipecat ECS Deployment Test Suite")
    print(f"Tests directory: {tests_dir}")

    results = []
    total_start = time.time()

    for test_file in test_files:
        test_path = tests_dir / test_file
        if test_path.exists():
            success, output, duration = run_test(str(test_path))
            results.append(
                {
                    "test": test_file,
                    "success": success,
                    "duration": duration,
                    "output": output,
                }
            )
        else:
            print(f"⚠️  SKIPPED: {test_file} (file not found)")
            results.append(
                {
                    "test": test_file,
                    "success": False,
                    "duration": 0,
                    "output": "File not found",
                }
            )

    total_duration = time.time() - total_start

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for r in results if r["success"])
    total = len(results)

    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {result['test']} ({result['duration']:.1f}s)")

    print(f"\nResults: {passed}/{total} tests passed")
    print(f"Total time: {total_duration:.1f} seconds")
    print(f"Success rate: {(passed/total)*100:.1f}%")

    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {total-passed} tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
