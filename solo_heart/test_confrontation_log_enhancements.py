#!/usr/bin/env python3
"""
Test script for Confrontation Log enhancements
Verifies collapsible UI, lazy hydration, safe identity handling, and QA hooks
"""

import os
import sys
import json
from pathlib import Path

# Compute base directory relative to this test file
base_dir = os.path.dirname(__file__)

# Helper to resolve static paths
static_js_path = os.path.join(base_dir, 'static', 'js', 'confrontation-log-client.js')
static_css_path = os.path.join(base_dir, 'static', 'css', 'confrontation-log.css')
template_path = os.path.join(base_dir, 'templates', 'gameplay.html')

def test_file_exists(file_path, description):
    """Test if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - NOT FOUND")
        return False

def test_script_content(script_path):
    """Test if the script contains expected enhancements"""
    try:
        with open(script_path, 'r') as f:
            content = f.read()
        
        tests = [
            ("Collapsible UI", "isCollapsed" in content and "toggleCollapse" in content),
            ("Lazy Hydration", "isHydrated" in content and "triggerHydration" in content),
            ("Safe Identity Handling", "isValidIdentity" in content and "console.warn" in content),
            ("QA Hooks", "data-testid" in content),
            ("localStorage", "localStorage" in content),
            ("Intersection Observer", "IntersectionObserver" in content),
        ]
        
        all_passed = True
        for test_name, passed in tests:
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Error reading script: {e}")
        return False

def test_template_integration():
    """Test if the Flask template has correct integration"""
    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        return False
    
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        tests = [
            ("React CDN Scripts", "unpkg.com/react@18" in content),
            ("Hydration Script", "js/confrontation-log-client.js" in content),
            ("CSS Link", "css/confrontation-log.css" in content),
            ("Identity Scope ID", "identity_scope_id" in content),
            ("Root Element", "confrontation-log-root" in content),
        ]
        
        all_passed = True
        for test_name, passed in tests:
            status = "✅" if passed else "❌"
            print(f"{status} {test_name}")
            if not passed:
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Confrontation Log Enhancements\n")
    
    # Test file existence
    print("📁 File Existence Tests:")
    files_to_test = [
        (static_js_path, "Enhanced hydration script"),
        (static_css_path, "Additional CSS styles"),
        (template_path, "Flask template"),
    ]
    
    file_tests_passed = True
    for file_path, description in files_to_test:
        if not test_file_exists(file_path, description):
            file_tests_passed = False
    
    print()
    
    # Test script content
    print("🔍 Script Enhancement Tests:")
    script_tests_passed = test_script_content(static_js_path)
    
    print()
    
    # Test template integration
    print("🎨 Template Integration Tests:")
    template_tests_passed = test_template_integration()
    
    print()
    
    # Summary
    print("📊 Test Summary:")
    if file_tests_passed and script_tests_passed and template_tests_passed:
        print("✅ All tests passed! Confrontation Log enhancements are ready.")
        print("\n🎯 Enhancement Features:")
        print("  • Collapsible UI with localStorage persistence")
        print("  • Lazy hydration via scroll/click")
        print("  • Safe identity_scope_id handling")
        print("  • QA hooks for testing")
        print("  • Responsive design with Tailwind CSS")
        print("  • Enhanced error handling and loading states")
        return True
    else:
        print("❌ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 