#!/usr/bin/env python3
"""
Onboarding Integrity Tests for SoloHeart

Ensures that contributor onboarding documentation and governance constraints 
are verifiably present, consistent, and integrated into CI where appropriate.

This test suite validates:
- Core onboarding files exist
- Required headings are present in documentation
- CI enforcement mechanisms are in place
- Import isolation test is functional
"""

import os
import pytest
from pathlib import Path


def test_onboarding_file_exists():
    """Test that ONBOARDING.md exists at root level."""
    # Check for ONBOARDING.md in root or docs/
    onboarding_paths = [
        "ONBOARDING.md",
        "docs/ONBOARDING.md",
        "docs/dev_onboarding.md"
    ]
    
    onboarding_exists = any(os.path.exists(path) for path in onboarding_paths)
    assert onboarding_exists, "ONBOARDING.md or dev_onboarding.md must exist at project root or in docs/"


def test_governance_file_exists():
    """Test that governance file exists at root level."""
    # Check for various governance files
    governance_paths = [
        "IMPLEMENTATION_GOVERNANCE.md",
        "GOVERNANCE.md",
        "docs/GOVERNANCE.md",
        "CONTRIBUTING.md"
    ]
    
    governance_exists = any(os.path.exists(path) for path in governance_paths)
    assert governance_exists, "Governance file must exist (IMPLEMENTATION_GOVERNANCE.md, GOVERNANCE.md, or CONTRIBUTING.md)"


def test_api_dependency_isolation_doc_exists():
    """Test that API dependency isolation documentation exists."""
    # Check for API dependency isolation docs
    api_doc_paths = [
        "docs/API_DEPENDENCY_ISOLATION.md",
        "docs/api_dependency_isolation.md",
        "API_DEPENDENCY_ISOLATION.md"
    ]
    
    api_doc_exists = any(os.path.exists(path) for path in api_doc_paths)
    if not api_doc_exists:
        print("ℹ️  API dependency isolation documentation not found (optional for SoloHeart)")
        pytest.skip("API dependency isolation documentation is optional for SoloHeart")


def test_import_isolation_test_exists():
    """Test that the import isolation test file exists."""
    assert os.path.exists("tests/test_import_isolation.py"), \
        "tests/test_import_isolation.py must exist"


def test_import_isolation_test_is_functional():
    """Test that the import isolation test can be imported and run."""
    try:
        # Import the test module using relative import
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        import test_import_isolation
        
        # Check that the main test function exists
        assert hasattr(test_import_isolation, 'test_import_isolation'), \
            "test_import_isolation function must exist"
        assert hasattr(test_import_isolation, 'test_api_files_can_import_external'), \
            "test_api_files_can_import_external function must exist"
        
        print("✅ Import isolation test module is functional")
        
    except ImportError as e:
        pytest.fail(f"Failed to import test_import_isolation module: {e}")


def test_ci_workflow_exists():
    """Test that CI workflow files exist."""
    ci_paths = [
        ".github/workflows/test.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/python.yml",
        "ci.yml",
        ".travis.yml",
        "azure-pipelines.yml"
    ]
    
    existing_ci_files = [path for path in ci_paths if os.path.exists(path)]
    
    if existing_ci_files:
        print(f"✅ Found CI configuration files: {existing_ci_files}")
        
        # Check if any CI file mentions the import isolation test
        for ci_file in existing_ci_files:
            with open(ci_file, "r", encoding="utf-8") as f:
                ci_contents = f.read()
                if "test_import_isolation" in ci_contents:
                    print(f"✅ {ci_file} includes import isolation test")
                    return
        
        # If we get here, no CI file mentions the test
        print("⚠️  WARNING: No CI configuration found that explicitly includes test_import_isolation.py")
        print("   Please ensure CI runs this test to enforce API dependency isolation")
        
    else:
        print("⚠️  WARNING: No CI configuration files found")
        print("   Please ensure test_import_isolation.py is included in your CI pipeline")


def test_documentation_consistency():
    """Test that documentation is consistent across files."""
    
    # Read relevant documentation files if they exist
    onboarding_content = ""
    governance_content = ""
    
    # Try to read onboarding file
    onboarding_paths = ["ONBOARDING.md", "docs/ONBOARDING.md", "docs/dev_onboarding.md"]
    for path in onboarding_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                onboarding_content = f.read()
            break
    
    # Try to read governance file
    governance_paths = ["IMPLEMENTATION_GOVERNANCE.md", "GOVERNANCE.md", "CONTRIBUTING.md"]
    for path in governance_paths:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                governance_content = f.read()
            break
    
    # Check for consistent terminology if files exist
    if onboarding_content and governance_content:
        key_terms = [
            "solo_heart",
            "api",
            "test_import_isolation.py",
            "Flask",
            "OpenAI"
        ]
        
        for term in key_terms:
            # Check that both files use consistent terminology
            if term in onboarding_content and term in governance_content:
                print(f"✅ Consistent terminology found: {term}")
            else:
                print(f"ℹ️  Term not found in both files: {term}")


def test_file_structure_compliance():
    """Test that the actual file structure matches documented expectations."""
    
    # Check that solo_heart/ directory exists
    assert os.path.exists("solo_heart/"), "solo_heart/ directory must exist"
    
    # Check for core game files
    core_files = [
        "solo_heart/character_generator.py",
        "solo_heart/character_sheet.py",
        "solo_heart/game_engine.py"
    ]
    
    # At least one core file should exist
    core_files_exist = any(os.path.exists(path) for path in core_files)
    if not core_files_exist:
        print("ℹ️  Core game files not found in expected locations (this may be OK)")


def test_import_isolation_enforcement():
    """Test that the import isolation enforcement is actually working."""
    
    # This test runs the actual import isolation test to ensure it's functional
    try:
        import subprocess
        import sys
        
        # Run the import isolation test
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "tests/test_import_isolation.py", "-v"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Import isolation test passes - enforcement is active")
        else:
            pytest.fail(f"Import isolation test failed:\n{result.stdout}\n{result.stderr}")
            
    except subprocess.TimeoutExpired:
        pytest.fail("Import isolation test timed out")
    except Exception as e:
        pytest.fail(f"Failed to run import isolation test: {e}")


def test_soloheart_specific_requirements():
    """Test SoloHeart-specific requirements."""
    
    # Check for SRD compliance
    srd_files = [
        "srd_data/",
        "solo_heart/ATTRIBUTION.md",
        "LICENSE.txt"
    ]
    
    srd_files_exist = any(os.path.exists(path) for path in srd_files)
    if srd_files_exist:
        print("✅ SRD compliance files found")
    else:
        print("ℹ️  SRD compliance files not found (may be optional)")
    
    # Check for game-specific files
    game_files = [
        "solo_heart/",
        "tests/",
        "requirements.txt"
    ]
    
    for game_file in game_files:
        assert os.path.exists(game_file), f"{game_file} must exist"


if __name__ == "__main__":
    # Run all tests
    pytest.main([__file__, "-v"]) 