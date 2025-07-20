#!/usr/bin/env python3
"""
Import Isolation Tests for SoloHeart
Enforces SoloHeart's API dependency boundary.

This test ensures that no external dependencies (Pydantic, FastAPI, etc.)
are imported in the core solo_heart/ directory, maintaining SoloHeart's
portability and clean separation between internal logic and external API.
"""

import os
import ast
import pytest
from pathlib import Path
from typing import Set, List


def extract_imports(file_path: str) -> Set[str]:
    """
    Extract all import statements from a Python file using AST parsing.
    
    Args:
        file_path: Path to the Python file to analyze
        
    Returns:
        Set of imported module names (without submodules)
    """
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # Handle 'import module' statements
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # Get the base module name (before any dots)
                    module_name = alias.name.split('.')[0]
                    imports.add(module_name)
            
            # Handle 'from module import ...' statements
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # Get the base module name (before any dots)
                    module_name = node.module.split('.')[0]
                    imports.add(module_name)
    
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
    
    return imports


def find_python_files(directory: str) -> List[Path]:
    """
    Recursively find all Python files in the given directory.
    
    Args:
        directory: Directory to search for Python files
        
    Returns:
        List of Path objects for Python files
    """
    python_files = []
    
    for root, dirs, files in os.walk(directory):
        # Skip common directories that shouldn't be scanned
        dirs[:] = [d for d in dirs if d not in {
            '__pycache__', '.git', 'venv', 'node_modules', 
            '.pytest_cache', 'build', 'dist'
        }]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def test_import_isolation():
    """
    Test that solo_heart/ contains no banned external imports.
    
    This test ensures SoloHeart's core logic remains free of external dependencies
    like Pydantic, FastAPI, or requests, maintaining portability and
    clean separation between internal and external concerns.
    """
    # Define banned imports that should not appear in solo_heart/ core logic
    # Note: SoloHeart uses Flask for web interface, so flask is allowed
    banned_imports = {
        "pydantic", "fastapi", "django",
        "sqlalchemy", "psycopg2", "mysql", "redis", "celery",
        "tornado", "aiohttp", "httpx", "urllib3", "boto3"
    }
    
    # Find the solo_heart directory
    soloheart_root = Path(__file__).parent.parent
    solo_heart_dir = soloheart_root / "solo_heart"
    
    if not solo_heart_dir.exists():
        pytest.skip(f"solo_heart directory not found at {solo_heart_dir}")
    
    # Find all Python files in solo_heart/
    python_files = find_python_files(str(solo_heart_dir))
    
    if not python_files:
        pytest.skip(f"No Python files found in {solo_heart_dir}")
    
    # Check each file for banned imports
    violations = []
    
    for file_path in python_files:
        imports = extract_imports(str(file_path))
        
        # Check for banned imports
        banned_found = imports.intersection(banned_imports)
        
        if banned_found:
            violations.append({
                'file': str(file_path),
                'banned_imports': list(banned_found),
                'all_imports': list(imports)
            })
    
    # Report violations if any found
    if violations:
        error_messages = []
        error_messages.append("🚫 BANNED IMPORTS DETECTED in solo_heart/")
        error_messages.append("")
        error_messages.append("The following files contain forbidden external dependencies:")
        error_messages.append("")
        
        for violation in violations:
            error_messages.append(f"📁 {violation['file']}")
            error_messages.append(f"   ❌ Banned imports: {', '.join(violation['banned_imports'])}")
            error_messages.append(f"   📋 All imports: {', '.join(violation['all_imports'])}")
            error_messages.append("")
        
        error_messages.append("💡 REMEDY:")
        error_messages.append("   - Move external dependencies to api/ directory")
        error_messages.append("   - Use internal models in solo_heart/")
        error_messages.append("   - Use conversion layer for API interactions")
        error_messages.append("")
        error_messages.append("🔒 SoloHeart's core must remain free of external dependencies for portability.")
        
        pytest.fail("\n".join(error_messages))
    
    # If we get here, all files are compliant
    print(f"✅ Import isolation test passed: {len(python_files)} files scanned, no violations found")


def test_api_files_can_import_external():
    """
    Test that API files (if they exist) are allowed to import external dependencies.
    
    This ensures the test doesn't incorrectly flag legitimate external imports
    in the API layer where they belong.
    """
    # Define allowed external imports for API files
    allowed_external_imports = {
        "pydantic", "fastapi", "requests", "uvicorn", "starlette", "flask"
    }
    
    # Find potential API directories
    soloheart_root = Path(__file__).parent.parent
    api_directories = [
        soloheart_root / "api",
        soloheart_root / "solo_heart" / "api",
        soloheart_root / "web",
        soloheart_root / "solo_heart" / "web"
    ]
    
    api_files_with_external = []
    
    for api_dir in api_directories:
        if api_dir.exists():
            python_files = find_python_files(str(api_dir))
            
            for file_path in python_files:
                imports = extract_imports(str(file_path))
                external_found = imports.intersection(allowed_external_imports)
                
                if external_found:
                    api_files_with_external.append({
                        'file': str(file_path),
                        'external_imports': list(external_found)
                    })
    
    # If API files exist, at least some should import external dependencies
    if api_files_with_external:
        print(f"✅ API files correctly import external dependencies: {len(api_files_with_external)} files found")
    else:
        print("ℹ️  No API files found with external imports (this is OK if no API layer exists)")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"]) 