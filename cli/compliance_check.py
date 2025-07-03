#!/usr/bin/env python3
"""
SRD 5.1 Compliance Audit Tool

This script performs a comprehensive audit of the project to ensure
compliance with the System Reference Document 5.1 license and content restrictions.

Usage:
    python cli/compliance_check.py [--verbose] [--fix-attribution]

Options:
    --verbose          Show detailed output for each file
    --fix-attribution  Automatically add missing attribution to files
"""

import os
import sys
import argparse
import fnmatch
from pathlib import Path
from typing import List, Dict, Tuple, Set
import re

# Required SRD attribution text
REQUIRED_ATTRIBUTION = "This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License."

# Restricted keywords that indicate non-SRD content
RESTRICTED_KEYWORDS = [
    "classic fantasy setting",
    "mystic realm",
    "dark domain",
    "psionic horror",
    "eye tyrant",
    "famous wizard",
    "undying sorcerer",
    "established campaign setting",
    "tabletop fantasy RPG",
    "tabletop fantasy RPG",
    "Faerûn",
    "Eberron"
]

# File patterns that require SRD attribution
SRD_ATTRIBUTION_PATTERNS = [
    "srd_data/**/*",
    "**/*.json",
    "**/*.md"
]

# Files and directories to exclude from scanning
EXCLUDE_PATTERNS = [
    ".git/**/*",
    "node_modules/**/*",
    "__pycache__/**/*",
    "**/*.pyc",
    "**/*.pyo",
    "**/*.pyd",
    "**/.DS_Store",
    "venv/**/*",
    ".venv/**/*",
    "**/LICENSE.txt",
    "**/COMPLIANCE_SUMMARY.md",
    ".hooks/**/*",
    "**/.complianceignore",
    ".pytest_cache/**/*",
    "**/.pytest_cache/**/*"
]

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color

class ComplianceChecker:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.attribution_violations: List[str] = []
        self.keyword_violations: List[Tuple[str, str, int]] = []
        self.passed_files: List[str] = []
        self.excluded_files: List[str] = []
        
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns."""
        relative_path = file_path.relative_to(self.project_root)
        # Always ignore the ignore file and the compliance checker itself
        if str(relative_path) in ['.complianceignore', 'cli/compliance_check.py']:
            return True
        for pattern in EXCLUDE_PATTERNS:
            if pattern.endswith('/'):
                # Directory pattern
                if str(relative_path).startswith(pattern[:-1]):
                    return True
            else:
                # File pattern
                if str(relative_path) == pattern or str(relative_path).endswith(pattern):
                    return True
        return False
    
    def should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        relative_path = file_path.relative_to(self.project_root)
        relative_str = str(relative_path)
        
        # Check hardcoded exclude patterns
        for pattern in EXCLUDE_PATTERNS:
            if fnmatch.fnmatch(relative_str, pattern):
                return True
        
        # Additional manual checks for common patterns
        if "node_modules" in relative_str:
            return True
        if "__pycache__" in relative_str:
            return True
        if relative_str.endswith(".pyc") or relative_str.endswith(".pyo") or relative_str.endswith(".pyd"):
            return True
        if relative_str.endswith(".DS_Store"):
            return True
        if "venv" in relative_str or ".venv" in relative_str:
            return True
                
        # Check .complianceignore file
        compliance_ignore = self.project_root / ".complianceignore"
        if compliance_ignore.exists():
            with open(compliance_ignore, 'r') as f:
                ignore_patterns = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(relative_str, pattern):
                    return True
                    
        return False
    
    def requires_attribution(self, file_path: Path) -> bool:
        """Check if file requires SRD attribution."""
        relative_path = file_path.relative_to(self.project_root)
        
        for pattern in SRD_ATTRIBUTION_PATTERNS:
            if fnmatch.fnmatch(str(relative_path), pattern):
                return True
                
        return False
    
    def check_file_attribution(self, file_path: Path) -> bool:
        """Check if file contains required SRD attribution."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return REQUIRED_ATTRIBUTION in content
        except (UnicodeDecodeError, IOError):
            # Skip binary files or files that can't be read
            return True
    
    def check_file_keywords(self, file_path: Path) -> List[Tuple[str, int]]:
        """Check file for restricted keywords and return violations with line numbers."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip keyword checking if the file contains the required attribution
            # This prevents false positives on the legally required attribution text
            if REQUIRED_ATTRIBUTION in content:
                return violations
                
            for line_num, line in enumerate(content.split('\n'), 1):
                for keyword in RESTRICTED_KEYWORDS:
                    if re.search(rf'\b{re.escape(keyword)}\b', line, re.IGNORECASE):
                        violations.append((keyword, line_num))
        except (UnicodeDecodeError, IOError):
            # Skip binary files or files that can't be read
            pass
            
        return violations
    
    def add_attribution_to_file(self, file_path: Path) -> bool:
        """Add missing attribution to file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Add attribution at the beginning of the file
            new_content = f"{REQUIRED_ATTRIBUTION}\n\n{content}"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return True
        except (UnicodeDecodeError, IOError):
            return False
    
    def scan_project(self, verbose: bool = False) -> None:
        """Scan the entire project for compliance violations."""
        print(f"{Colors.BLUE}🔍 Scanning project for SRD 5.1 compliance...{Colors.NC}")
        print(f"Project root: {self.project_root}")
        print()
        
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue
                
            relative_path = file_path.relative_to(self.project_root)
            
            if self._should_ignore_file(file_path):
                self.excluded_files.append(str(relative_path))
                if verbose:
                    print(f"{Colors.YELLOW}⏭️  Excluded: {relative_path}{Colors.NC}")
                continue
            
            if verbose:
                print(f"Checking: {relative_path}")
            
            file_violations = False
            
            # Check attribution requirement
            if self.requires_attribution(file_path):
                if not self.check_file_attribution(file_path):
                    self.attribution_violations.append(str(relative_path))
                    file_violations = True
                    if verbose:
                        print(f"  {Colors.RED}❌ Missing SRD attribution{Colors.NC}")
                elif verbose:
                    print(f"  {Colors.GREEN}✅ SRD attribution found{Colors.NC}")
            
            # Check for restricted keywords
            keyword_violations = self.check_file_keywords(file_path)
            for keyword, line_num in keyword_violations:
                self.keyword_violations.append((str(relative_path), keyword, line_num))
                file_violations = True
                if verbose:
                    print(f"  {Colors.RED}❌ Restricted keyword '{keyword}' at line {line_num}{Colors.NC}")
            
            if not file_violations:
                self.passed_files.append(str(relative_path))
    
    def generate_report(self) -> bool:
        """Generate and display compliance report."""
        print(f"\n{Colors.BLUE}📊 COMPLIANCE AUDIT REPORT{Colors.NC}")
        print("=" * 50)
        
        # Summary
        total_files = len(self.passed_files) + len(self.attribution_violations) + len(set(v[0] for v in self.keyword_violations))
        excluded_count = len(self.excluded_files)
        
        print(f"\n📈 Summary:")
        print(f"  Total files scanned: {total_files}")
        print(f"  Files excluded: {excluded_count}")
        print(f"  Files passed: {len(self.passed_files)}")
        print(f"  Attribution violations: {len(self.attribution_violations)}")
        print(f"  Keyword violations: {len(self.keyword_violations)}")
        
        # Attribution violations
        if self.attribution_violations:
            print(f"\n{Colors.RED}🚨 Missing SRD Attribution:{Colors.NC}")
            for file_path in self.attribution_violations:
                print(f"  - {file_path}")
            print(f"\nRequired attribution text:")
            print(f"  \"{REQUIRED_ATTRIBUTION}\"")
        
        # Keyword violations
        if self.keyword_violations:
            print(f"\n{Colors.RED}🚨 Restricted Keywords Found:{Colors.NC}")
            for file_path, keyword, line_num in self.keyword_violations:
                print(f"  - {file_path}:{line_num} - '{keyword}'")
            print(f"\nRestricted keywords include:")
            for keyword in RESTRICTED_KEYWORDS:
                print(f"  - {keyword}")
        
        # Passed files (if verbose)
        if self.passed_files:
            print(f"\n{Colors.GREEN}✅ Files that passed compliance:{Colors.NC}")
            for file_path in sorted(self.passed_files):
                print(f"  - {file_path}")
        
        # Overall result
        if self.attribution_violations or self.keyword_violations:
            print(f"\n{Colors.RED}❌ COMPLIANCE VIOLATIONS FOUND{Colors.NC}")
            print("The project does not meet SRD 5.1 compliance requirements.")
            return False
        else:
            print(f"\n{Colors.GREEN}✅ ALL FILES PASS SRD 5.1 COMPLIANCE CHECK!{Colors.NC}")
            return True
    
    def fix_attribution_violations(self) -> None:
        """Automatically fix attribution violations."""
        if not self.attribution_violations:
            print(f"{Colors.GREEN}No attribution violations to fix.{Colors.NC}")
            return
        
        print(f"\n{Colors.YELLOW}🔧 Fixing attribution violations...{Colors.NC}")
        
        for file_path in self.attribution_violations:
            full_path = self.project_root / file_path
            if self.add_attribution_to_file(full_path):
                print(f"  ✅ Fixed: {file_path}")
            else:
                print(f"  ❌ Failed to fix: {file_path}")
        
        print(f"{Colors.GREEN}Attribution fixes completed.{Colors.NC}")

def main():
    parser = argparse.ArgumentParser(
        description="SRD 5.1 Compliance Audit Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/compliance_check.py                    # Basic compliance check
  python cli/compliance_check.py --verbose         # Detailed output
  python cli/compliance_check.py --fix-attribution # Auto-fix attribution issues
        """
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for each file'
    )
    
    parser.add_argument(
        '--fix-attribution',
        action='store_true',
        help='Automatically add missing attribution to files'
    )
    
    parser.add_argument(
        '--project-root',
        default='.',
        help='Project root directory (default: current directory)'
    )
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = ComplianceChecker(args.project_root)
    
    # Scan project
    checker.scan_project(verbose=args.verbose)
    
    # Fix attribution if requested
    if args.fix_attribution:
        checker.fix_attribution_violations()
        # Re-scan after fixes
        checker.attribution_violations.clear()
        checker.keyword_violations.clear()
        checker.passed_files.clear()
        checker.scan_project(verbose=False)
    
    # Generate report
    is_compliant = checker.generate_report()
    
    # Exit with appropriate status code
    sys.exit(0 if is_compliant else 1)

if __name__ == "__main__":
    main()
