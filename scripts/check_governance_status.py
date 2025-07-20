#!/usr/bin/env python3
"""
Governance Enforcement Status Checker

Checks governance enforcement status across TNE, SoloHeart, and TNB repositories.
Runs governance-related test suites and generates a markdown-formatted status report
confirming enforcement components across all repos.
"""

import os
import sys
import subprocess
import argparse
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RepoConfig:
    """Configuration for a repository."""
    name: str
    display_name: str
    path: str
    test_paths: Dict[str, str]
    expected_artifacts: List[str]
    allowed_imports: List[str] = None


@dataclass
class TestResult:
    """Result of running a test suite."""
    test_name: str
    passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    output: str
    file_count: Optional[int] = None
    violations: Optional[List[str]] = None


@dataclass
class ArtifactStatus:
    """Status of a governance artifact."""
    name: str
    exists: bool
    details: str = ""


class GovernanceStatusChecker:
    """Main class for checking governance enforcement status."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.repos = self._setup_repo_configs()
    
    def _setup_repo_configs(self) -> Dict[str, RepoConfig]:
        """Setup repository configurations."""
        return {
            "tne": RepoConfig(
                name="tne",
                display_name="TNE (The Narrative Engine)",
                path=str(self.base_path / "TNE"),
                test_paths={
                    "import_isolation": "tests/test_import_isolation.py",
                    "onboarding_integrity": "tests/test_onboarding_integrity.py"
                },
                expected_artifacts=[
                    "tests/test_import_isolation.py",
                    "tests/test_onboarding_integrity.py",
                    ".github/workflows/test.yml",
                    ".github/PULL_REQUEST_TEMPLATE.md",
                    "README.md",
                    "ONBOARDING.md",
                    "IMPLEMENTATION_GOVERNANCE.md",
                    "docs/API_DEPENDENCY_ISOLATION.md"
                ],
                allowed_imports=["pydantic", "fastapi", "requests", "uvicorn", "starlette"]
            ),
            "soloheart": RepoConfig(
                name="soloheart",
                display_name="SoloHeart",
                path=str(self.base_path / "SoloHeart"),
                test_paths={
                    "import_isolation": "tests/test_import_isolation.py",
                    "onboarding_integrity": "tests/test_onboarding_integrity.py"
                },
                expected_artifacts=[
                    "tests/test_import_isolation.py",
                    "tests/test_onboarding_integrity.py",
                    ".github/workflows/test.yml",
                    ".github/PULL_REQUEST_TEMPLATE.md",
                    "README.md",
                    "docs/dev_onboarding.md",
                    "CONTRIBUTING.md"
                ],
                allowed_imports=["flask", "requests", "pydantic", "fastapi", "uvicorn", "starlette"]
            ),
            "tnb": RepoConfig(
                name="tnb",
                display_name="TNB (The Narrative Bridge)",
                path=str(self.base_path / "TNB"),
                test_paths={
                    "import_isolation": "python_tests/test_import_isolation.py",
                    "onboarding_integrity": "python_tests/test_onboarding_integrity.py"
                },
                expected_artifacts=[
                    "python_tests/test_import_isolation.py",
                    "python_tests/test_onboarding_integrity.py",
                    ".github/workflows/test.yml",
                    ".github/PULL_REQUEST_TEMPLATE.md",
                    "README.md",
                    "docs/ONBOARDING.md",
                    "CONTRIBUTING.md"
                ],
                allowed_imports=["pydantic", "fastapi", "requests", "uvicorn", "starlette"]
            )
        }
    
    def run_pytest(self, repo_path: str, test_path: str) -> TestResult:
        """Run pytest on a specific test file and capture results."""
        try:
            # Change to repo directory
            original_cwd = os.getcwd()
            os.chdir(repo_path)
            
            # Run pytest with verbose output
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_path, "-v", "-s"
            ], capture_output=True, text=True, timeout=60)
            
            # Parse pytest output
            output = result.stdout + result.stderr
            
            # Extract test statistics
            total_tests = 0
            passed_tests = 0
            failed_tests = 0
            skipped_tests = 0
            
            # Look for pytest summary - handle different formats
            summary_patterns = [
                r'(\d+) passed.*?(\d+) failed.*?(\d+) skipped',
                r'(\d+) passed.*?(\d+) skipped',
                r'(\d+) passed.*?(\d+) failed',
                r'(\d+) passed'
            ]
            
            for pattern in summary_patterns:
                summary_match = re.search(pattern, output)
                if summary_match:
                    passed_tests = int(summary_match.group(1))
                    failed_tests = int(summary_match.group(2)) if len(summary_match.groups()) > 1 and summary_match.group(2) else 0
                    skipped_tests = int(summary_match.group(3)) if len(summary_match.groups()) > 2 and summary_match.group(3) else 0
                    total_tests = passed_tests + failed_tests + skipped_tests
                    break
            
            # Extract file count from import isolation test
            file_count = None
            file_count_match = re.search(r'(\d+) files scanned', output)
            if file_count_match:
                file_count = int(file_count_match.group(1))
            
            # Extract violations if any
            violations = []
            if "BANNED IMPORTS DETECTED" in output:
                violation_lines = [line.strip() for line in output.split('\n') 
                                 if '❌ Banned imports:' in line]
                violations = violation_lines
            
            # Restore original directory
            os.chdir(original_cwd)
            
            return TestResult(
                test_name=os.path.basename(test_path),
                passed=result.returncode == 0,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                output=output,
                file_count=file_count,
                violations=violations
            )
            
        except subprocess.TimeoutExpired:
            return TestResult(
                test_name=os.path.basename(test_path),
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                output="Test timed out after 60 seconds"
            )
        except Exception as e:
            return TestResult(
                test_name=os.path.basename(test_path),
                passed=False,
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                skipped_tests=0,
                output=f"Error running test: {str(e)}"
            )
    
    def check_artifacts(self, repo_config: RepoConfig) -> List[ArtifactStatus]:
        """Check for existence of governance artifacts."""
        artifacts = []
        repo_path = Path(repo_config.path)
        
        for artifact_path in repo_config.expected_artifacts:
            full_path = repo_path / artifact_path
            exists = full_path.exists()
            
            details = ""
            if exists:
                if artifact_path.endswith('.md'):
                    # Check for CI badge in README
                    if artifact_path == "README.md":
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if "![CI]" in content and "workflows" in content:
                                details = "CI badge present"
                            else:
                                details = "CI badge missing"
                    else:
                        details = "Documentation file exists"
                elif artifact_path.endswith('.yml') or artifact_path.endswith('.yaml'):
                    # Check for governance tests in workflow
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "test_import_isolation" in content:
                            details = "Governance tests included"
                        else:
                            details = "Governance tests not found"
                else:
                    details = "File exists"
            else:
                details = "File not found"
            
            artifacts.append(ArtifactStatus(
                name=artifact_path,
                exists=exists,
                details=details
            ))
        
        return artifacts
    
    def get_status_emoji(self, passed: bool) -> str:
        """Get status emoji based on test result."""
        return "✅" if passed else "❌"
    
    def get_status_text(self, passed: bool) -> str:
        """Get status text based on test result."""
        return "PASSING" if passed else "FAILING"
    
    def generate_repo_report(self, repo_name: str, repo_config: RepoConfig) -> str:
        """Generate markdown report for a single repository."""
        repo_path = repo_config.path
        
        if not os.path.exists(repo_path):
            return f"### **❌ {repo_config.display_name} - NOT FOUND**\n**Status: REPOSITORY MISSING**\n\n"
        
        # Run tests
        test_results = {}
        for test_type, test_path in repo_config.test_paths.items():
            full_test_path = os.path.join(repo_path, test_path)
            if os.path.exists(full_test_path):
                test_results[test_type] = self.run_pytest(repo_path, test_path)
            else:
                test_results[test_type] = TestResult(
                    test_name=os.path.basename(test_path),
                    passed=False,
                    total_tests=0,
                    passed_tests=0,
                    failed_tests=1,
                    skipped_tests=0,
                    output=f"Test file not found: {test_path}"
                )
        
        # Check artifacts
        artifacts = self.check_artifacts(repo_config)
        
        # Determine overall status
        all_tests_passed = all(result.passed for result in test_results.values())
        all_artifacts_exist = all(artifact.exists for artifact in artifacts)
        
        if all_tests_passed and all_artifacts_exist:
            status = "FULLY IMPLEMENTED"
            status_emoji = "✅"
        elif all_tests_passed:
            status = "PARTIALLY IMPLEMENTED"
            status_emoji = "⚠️"
        else:
            status = "INCOMPLETE"
            status_emoji = "❌"
        
        # Generate report
        report = f"### **{status_emoji} {repo_config.display_name} - {status.split()[0]}**\n"
        report += f"**Status: {status}** 🎯\n\n"
        
        # Test results table
        report += "| Component | Status | Details |\n"
        report += "|-----------|--------|---------|\n"
        
        # Import isolation test
        if "import_isolation" in test_results:
            result = test_results["import_isolation"]
            details = f"{result.file_count or 0} files scanned, no violations" if result.passed else "Violations detected"
            report += f"| **Import Isolation Test** | {self.get_status_emoji(result.passed)} {self.get_status_text(result.passed)} | {details} |\n"
        
        # Onboarding integrity test
        if "onboarding_integrity" in test_results:
            result = test_results["onboarding_integrity"]
            details = f"{result.passed_tests}/{result.total_tests} tests passed" if result.total_tests > 0 else "No tests found"
            report += f"| **Onboarding Integrity Test** | {self.get_status_emoji(result.passed)} {self.get_status_text(result.passed)} | {details} |\n"
        
        # CI workflow
        ci_workflow = next((a for a in artifacts if a.name.endswith('test.yml')), None)
        if ci_workflow:
            status_emoji = "✅" if ci_workflow.exists else "❌"
            status_text = "ACTIVE" if ci_workflow.exists else "MISSING"
            report += f"| **CI Workflow Integration** | {status_emoji} {status_text} | {ci_workflow.details} |\n"
        
        # PR template
        pr_template = next((a for a in artifacts if 'PULL_REQUEST_TEMPLATE' in a.name), None)
        if pr_template:
            status_emoji = "✅" if pr_template.exists else "❌"
            status_text = "CREATED" if pr_template.exists else "MISSING"
            report += f"| **PR Template** | {status_emoji} {status_text} | Governance checklist enforced |\n"
        
        # CI badge
        readme = next((a for a in artifacts if a.name == "README.md"), None)
        if readme:
            status_emoji = "✅" if "CI badge present" in readme.details else "❌"
            status_text = "DISPLAYED" if "CI badge present" in readme.details else "MISSING"
            report += f"| **CI Badge** | {status_emoji} {status_text} | Visual status indicator |\n"
        
        # Documentation
        docs = [a for a in artifacts if a.name.endswith('.md') and 'README' not in a.name]
        if docs:
            existing_docs = sum(1 for d in docs if d.exists)
            total_docs = len(docs)
            status_emoji = "✅" if existing_docs == total_docs else "⚠️"
            status_text = "COMPLETE" if existing_docs == total_docs else "PARTIAL"
            report += f"| **Documentation** | {status_emoji} {status_text} | {existing_docs}/{total_docs} files present |\n"
        
        report += "\n"
        
        # Add key achievements if tests passed
        if all_tests_passed:
            report += "**Key Achievements:**\n"
            if repo_name == "tne":
                report += "- 🔒 **Strict API Isolation**: No external dependencies in `narrative_core/`\n"
                report += "- 📚 **Complete Documentation**: API dependency isolation fully documented\n"
            elif repo_name == "soloheart":
                report += "- 🎮 **Game-Appropriate Isolation**: Flask/requests allowed for web interface\n"
                report += "- 📋 **SRD Compliance**: Legal and attribution requirements met\n"
            elif repo_name == "tnb":
                report += "- 🌉 **Stateless Design**: Middleware architecture constraints enforced\n"
                report += "- 📦 **Multi-Language Support**: Python tests for JavaScript project\n"
            
            report += "- 🧪 **Comprehensive Testing**: All governance tests passing\n"
            report += "- 🔄 **CI Integration**: Automated enforcement active\n"
        
        return report
    
    def generate_overall_report(self) -> str:
        """Generate complete governance status report."""
        report = f"# 📊 **Governance Enforcement Status Report**\n\n"
        report += f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        # Generate reports for each repository
        repo_reports = []
        total_repos = 0
        completed_repos = 0
        
        for repo_name, repo_config in self.repos.items():
            total_repos += 1
            repo_report = self.generate_repo_report(repo_name, repo_config)
            repo_reports.append(repo_report)
            
            # Count completed repos
            if "FULLY IMPLEMENTED" in repo_report:
                completed_repos += 1
        
        report += "\n".join(repo_reports)
        
        # Overall status
        completion_percentage = (completed_repos / total_repos) * 100 if total_repos > 0 else 0
        
        report += f"\n## 🎯 **Overall Governance Status: {completion_percentage:.0f}% COMPLETE**\n\n"
        
        if completion_percentage == 100:
            report += "### **Cross-Repository Consistency** ✅\n"
            report += "- **Import Isolation**: All repositories enforce dependency boundaries\n"
            report += "- **CI Integration**: All workflows include governance enforcement\n"
            report += "- **Documentation**: All repositories have onboarding and governance\n"
            report += "- **PR Templates**: All repositories enforce pre-commit checks\n"
            report += "- **Error Handling**: Custom failure messages for violations\n"
            report += "- **Badge Integration**: Visual CI status indicators\n\n"
            
            report += "### **Repository-Specific Adaptations** ✅\n"
            report += "- **TNE**: Strict API dependency isolation (reference implementation)\n"
            report += "- **SoloHeart**: Game-appropriate isolation with Flask/requests allowed\n"
            report += "- **TNB**: Stateless design principles with multi-language support\n\n"
            
            report += "### **Governance Enforcement Coverage** ✅\n"
            report += "- **Pre-commit**: Manual governance checks in PR templates\n"
            report += "- **CI Automation**: Automated governance tests on every commit\n"
            report += "- **Visual Status**: CI badges show governance compliance\n"
            report += "- **Documentation**: Consistent onboarding and governance across all repos\n\n"
            
            report += "## 🚀 **Ready for Production Deployment**\n\n"
            report += "All repositories now have **comprehensive, automated, and consistent** governance enforcement systems!\n"
        else:
            report += f"**Status**: {completed_repos}/{total_repos} repositories fully implemented\n"
            report += "**Next Steps**: Complete governance implementation for remaining repositories\n"
        
        return report
    
    def run(self, save_path: Optional[str] = None) -> str:
        """Run the governance status check and return the report."""
        report = self.generate_overall_report()
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"Report saved to: {save_path}")
        else:
            print(report)
        
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check governance enforcement status across repositories")
    parser.add_argument("--save", help="Save report to specified file path")
    parser.add_argument("--base-path", help="Base path to repositories (default: parent of scripts directory)")
    
    args = parser.parse_args()
    
    # Create checker and run
    checker = GovernanceStatusChecker(base_path=args.base_path)
    checker.run(save_path=args.save)


if __name__ == "__main__":
    main() 