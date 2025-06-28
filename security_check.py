#!/usr/bin/env python3
"""
Security Check Script for DnD 5E AI-Powered Campaign Manager
===========================================================

This script performs security checks on the codebase to ensure:
- No hardcoded secrets
- No API keys in code
- Proper environment variable usage
- Security best practices
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class SecurityChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.issues = []
        self.warnings = []
        
        # Patterns to check for
        self.secret_patterns = [
            r'sk-[a-zA-Z0-9]{20,}',  # OpenAI API keys
            r'pk_[a-zA-Z0-9]{20,}',  # OpenAI public keys
            r'[a-zA-Z0-9]{32,}',     # Generic long tokens
            r'password\s*=\s*["\'][^"\']+["\']',  # Hardcoded passwords
            r'secret\s*=\s*["\'][^"\']+["\']',    # Hardcoded secrets
            r'token\s*=\s*["\'][^"\']+["\']',     # Hardcoded tokens
        ]
        
        # Files to exclude from checks
        self.exclude_patterns = [
            r'__pycache__',
            r'\.git',
            r'\.env',
            r'venv',
            r'node_modules',
            r'\.pyc$',
            r'\.log$',
            r'\.db$',
            r'\.sqlite$',
        ]
        
        # Files to include
        self.include_extensions = ['.py', '.js', '.html', '.md', '.txt', '.json']

    def should_check_file(self, file_path: Path) -> bool:
        """Determine if a file should be checked for security issues."""
        # Check if file should be excluded
        for pattern in self.exclude_patterns:
            if re.search(pattern, str(file_path)):
                return False
        
        # Check if file has an included extension
        return any(str(file_path).endswith(ext) for ext in self.include_extensions)

    def check_file_for_secrets(self, file_path: Path) -> List[Dict]:
        """Check a single file for security issues."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern in self.secret_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            issues.append({
                                'file': str(file_path),
                                'line': line_num,
                                'pattern': pattern,
                                'content': line.strip()[:100] + '...' if len(line) > 100 else line.strip()
                            })
        except Exception as e:
            self.warnings.append(f"Could not read {file_path}: {e}")
        
        return issues

    def check_environment_usage(self, file_path: Path) -> List[Dict]:
        """Check if environment variables are properly used."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for hardcoded Flask secret keys
                flask_secret_patterns = [
                    r'app\.secret_key\s*=\s*["\'][^"\']+["\']',
                    r'secret_key\s*=\s*["\'][^"\']+["\']',
                ]
                
                for pattern in flask_secret_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        issues.append({
                            'file': str(file_path),
                            'line': line_num,
                            'type': 'hardcoded_secret_key',
                            'content': match.group(0)[:100] + '...' if len(match.group(0)) > 100 else match.group(0)
                        })
        except Exception as e:
            self.warnings.append(f"Could not read {file_path}: {e}")
        
        return issues

    def check_gitignore(self) -> List[str]:
        """Check if .gitignore properly excludes sensitive files."""
        issues = []
        gitignore_path = self.project_root / '.gitignore'
        
        if not gitignore_path.exists():
            issues.append("No .gitignore file found")
            return issues
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        required_patterns = [
            r'\.env',
            r'__pycache__',
            r'\.pyc',
            r'\.db',
            r'\.log',
            r'venv',
        ]
        
        for pattern in required_patterns:
            if not re.search(pattern, content):
                issues.append(f"Missing pattern in .gitignore: {pattern}")
        
        return issues

    def run_checks(self) -> Dict:
        """Run all security checks."""
        print("🔍 Running security checks...")
        
        # Check .gitignore
        gitignore_issues = self.check_gitignore()
        if gitignore_issues:
            self.issues.extend([{'type': 'gitignore', 'message': issue} for issue in gitignore_issues])
        
        # Check all files
        for file_path in self.project_root.rglob('*'):
            if file_path.is_file() and self.should_check_file(file_path):
                # Check for secrets
                secret_issues = self.check_file_for_secrets(file_path)
                self.issues.extend(secret_issues)
                
                # Check for hardcoded secrets
                env_issues = self.check_environment_usage(file_path)
                self.issues.extend(env_issues)
        
        return {
            'issues': self.issues,
            'warnings': self.warnings,
            'total_files_checked': len(list(self.project_root.rglob('*'))),
            'total_issues': len(self.issues)
        }

    def print_report(self, results: Dict):
        """Print a formatted security report."""
        print("\n" + "="*60)
        print("🔐 SECURITY CHECK REPORT")
        print("="*60)
        
        if results['issues']:
            print(f"\n❌ Found {len(results['issues'])} security issues:")
            print("-" * 40)
            
            for issue in results['issues']:
                if 'file' in issue:
                    print(f"File: {issue['file']}")
                    print(f"Line: {issue['line']}")
                    print(f"Pattern: {issue['pattern']}")
                    print(f"Content: {issue['content']}")
                    print()
                else:
                    print(f"⚠️  {issue['message']}")
        else:
            print("\n✅ No security issues found!")
        
        if results['warnings']:
            print(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for warning in results['warnings']:
                print(f"  - {warning}")
        
        print(f"\n📊 Summary:")
        print(f"  - Files checked: {results['total_files_checked']}")
        print(f"  - Issues found: {results['total_issues']}")
        print(f"  - Warnings: {len(results['warnings'])}")
        
        if results['total_issues'] == 0:
            print("\n🎉 All security checks passed!")
        else:
            print("\n🚨 Security issues detected. Please review and fix before committing.")
        
        print("="*60)

def main():
    """Main function to run security checks."""
    checker = SecurityChecker()
    results = checker.run_checks()
    checker.print_report(results)
    
    # Exit with error code if issues found
    if results['total_issues'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main() 