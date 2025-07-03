#!/usr/bin/env python3
"""
Automated SoloHeart Branding Compliance Check

This script scans files for branding compliance and logs violations.
Can be run manually or integrated into file system watchers.
"""

import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Set, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SoloHeartComplianceChecker:
    """Automated compliance checker for SoloHeart branding."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.compliance_log_path = self.project_root / "branding_status" / "compliance_log.md"
        self.compliance_ignore_path = self.project_root / ".complianceignore"
        
        # Required branding terms
        self.required_terms = {
            "SoloHeart": "Primary game branding",
            "SoloHeart Guide": "Replaces Dungeon Master/DM"
        }
        
        # Restricted terms (should not appear in active code)
        self.restricted_terms = {
            "D&D": "Use SoloHeart instead",
            "5E": "Use SoloHeart instead", 
            "Dungeon Master": "Use SoloHeart Guide instead",
            "DM": "Use SoloHeart Guide instead",
            "Solo Adventure": "Use SoloHeart instead"
        }
        
        # Preserved terms (must not be changed)
        self.preserved_terms = {
            "The Narrative Engine": "Must be preserved exactly"
        }
        
        # File extensions to check
        self.checkable_extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx', '.html', '.css', 
            '.json', '.md', '.txt', '.yml', '.yaml', '.toml'
        }
        
        # Load ignore patterns
        self.ignore_patterns = self._load_ignore_patterns()
    
    def _load_ignore_patterns(self) -> Set[str]:
        """Load patterns from .complianceignore file."""
        ignore_patterns = set()
        
        if self.compliance_ignore_path.exists():
            with open(self.compliance_ignore_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        ignore_patterns.add(line)
        
        return ignore_patterns
    
    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored based on patterns."""
        relative_path = file_path.relative_to(self.project_root)
        
        for pattern in self.ignore_patterns:
            if pattern.endswith('/'):
                # Directory pattern
                if str(relative_path).startswith(pattern[:-1]):
                    return True
            else:
                # File pattern
                if str(relative_path) == pattern or str(relative_path).endswith(pattern):
                    return True
        
        return False
    
    def _is_checkable_file(self, file_path: Path) -> bool:
        """Check if file should be scanned for compliance."""
        if not file_path.is_file():
            return False
        
        if file_path.suffix not in self.checkable_extensions:
            return False
        
        if self._should_ignore_file(file_path):
            return False
        
        return True
    
    def scan_file(self, file_path: Path) -> Dict[str, any]:
        """Scan a single file for compliance issues."""
        if not self._is_checkable_file(file_path):
            return {"skipped": True, "reason": "Not a checkable file"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return {"error": True, "message": f"Could not read file: {e}"}
        
        issues = []
        warnings = []
        
        # Check for restricted terms
        for term, description in self.restricted_terms.items():
            if term in content:
                # Count occurrences
                count = content.count(term)
                issues.append({
                    "type": "restricted_term",
                    "term": term,
                    "description": description,
                    "count": count,
                    "severity": "high"
                })
        
        # Check for required terms (warning if missing in certain file types)
        if file_path.suffix in ['.py', '.js', '.ts', '.tsx', '.jsx']:
            # Check if this is a main application file
            if any(keyword in file_path.name.lower() for keyword in ['main', 'app', 'interface', 'game']):
                for term, description in self.required_terms.items():
                    if term not in content:
                        warnings.append({
                            "type": "missing_required_term",
                            "term": term,
                            "description": description,
                            "severity": "medium"
                        })
        
        # Check for preserved terms
        for term, description in self.preserved_terms.items():
            if term in content:
                # This is good - preserved terms should be present
                pass
        
        return {
            "file_path": str(file_path.relative_to(self.project_root)),
            "issues": issues,
            "warnings": warnings,
            "has_issues": len(issues) > 0,
            "has_warnings": len(warnings) > 0
        }
    
    def scan_directory(self, directory: Path = None) -> Dict[str, any]:
        """Scan entire directory for compliance issues."""
        if directory is None:
            directory = self.project_root
        
        results = {
            "scan_time": datetime.now().isoformat(),
            "directory": str(directory),
            "files_scanned": 0,
            "files_with_issues": 0,
            "files_with_warnings": 0,
            "total_issues": 0,
            "total_warnings": 0,
            "results": []
        }
        
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                result = self.scan_file(file_path)
                if not result.get("skipped") and not result.get("error"):
                    results["files_scanned"] += 1
                    results["results"].append(result)
                    
                    if result["has_issues"]:
                        results["files_with_issues"] += 1
                        results["total_issues"] += len(result["issues"])
                    
                    if result["has_warnings"]:
                        results["files_with_warnings"] += 1
                        results["total_warnings"] += len(result["warnings"])
        
        return results
    
    def log_compliance_results(self, results: Dict[str, any]) -> None:
        """Log compliance results to the compliance log."""
        if not self.compliance_log_path.parent.exists():
            self.compliance_log_path.parent.mkdir(parents=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        log_entry = f"""
### {timestamp}
- **Files Scanned:** {results['files_scanned']}
- **Files with Issues:** {results['files_with_issues']}
- **Files with Warnings:** {results['files_with_warnings']}
- **Total Issues:** {results['total_issues']}
- **Total Warnings:** {results['total_warnings']}

"""
        
        if results['files_with_issues'] > 0:
            log_entry += "#### Issues Found:\n"
            for result in results['results']:
                if result['has_issues']:
                    log_entry += f"- **{result['file_path']}:**\n"
                    for issue in result['issues']:
                        log_entry += f"  - {issue['term']}: {issue['description']} (Count: {issue['count']})\n"
        
        if results['files_with_warnings'] > 0:
            log_entry += "#### Warnings:\n"
            for result in results['results']:
                if result['has_warnings']:
                    log_entry += f"- **{result['file_path']}:**\n"
                    for warning in result['warnings']:
                        log_entry += f"  - Missing: {warning['term']}: {warning['description']}\n"
        
        # Append to log file
        with open(self.compliance_log_path, 'a') as f:
            f.write(log_entry)
    
    def check_single_file(self, file_path: str) -> Dict[str, any]:
        """Check a single file and log results."""
        path = Path(file_path)
        if not path.is_absolute():
            path = self.project_root / path
        
        result = self.scan_file(path)
        if not result.get("skipped") and not result.get("error"):
            self.log_compliance_results({
                "scan_time": datetime.now().isoformat(),
                "directory": str(path.parent),
                "files_scanned": 1,
                "files_with_issues": 1 if result["has_issues"] else 0,
                "files_with_warnings": 1 if result["has_warnings"] else 0,
                "total_issues": len(result["issues"]),
                "total_warnings": len(result["warnings"]),
                "results": [result]
            })
        
        return result

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="SoloHeart Branding Compliance Checker")
    parser.add_argument("--file", help="Check a single file")
    parser.add_argument("--directory", help="Check a specific directory")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    checker = SoloHeartComplianceChecker()
    
    if args.file:
        result = checker.check_single_file(args.file)
        if args.verbose:
            print(json.dumps(result, indent=2))
        else:
            if result.get("has_issues"):
                print(f"❌ Issues found in {args.file}")
                for issue in result["issues"]:
                    print(f"  - {issue['term']}: {issue['description']}")
            elif result.get("has_warnings"):
                print(f"⚠️  Warnings in {args.file}")
                for warning in result["warnings"]:
                    print(f"  - Missing: {warning['term']}")
            else:
                print(f"✅ {args.file} passes compliance check")
    
    else:
        # Scan entire project
        results = checker.scan_directory()
        checker.log_compliance_results(results)
        
        if args.verbose:
            print(json.dumps(results, indent=2))
        else:
            print(f"📊 Compliance Scan Results:")
            print(f"  Files scanned: {results['files_scanned']}")
            print(f"  Files with issues: {results['files_with_issues']}")
            print(f"  Files with warnings: {results['files_with_warnings']}")
            print(f"  Total issues: {results['total_issues']}")
            print(f"  Total warnings: {results['total_warnings']}")
            
            if results['files_with_issues'] == 0 and results['files_with_warnings'] == 0:
                print("✅ All files pass SoloHeart branding compliance!")
            else:
                print("❌ Compliance issues found. Check branding_status/compliance_log.md for details.")

if __name__ == "__main__":
    main() 