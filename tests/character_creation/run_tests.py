#!/usr/bin/env python3
"""
Test Runner for Enhanced Step-by-Step Character Creator Tests

Run this script to execute all tests for the enhanced character creation system.
"""

import sys
import os
import unittest

# Add the game_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'game_app'))

def run_tests():
    """Run all enhanced step-by-step creator tests."""
    print("🧪 Running Enhanced Step-by-Step Character Creator Tests")
    print("=" * 60)
    
    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = os.path.dirname(__file__)
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n🚨 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code) 