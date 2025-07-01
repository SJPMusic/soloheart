# SRD 5.1 Compliance Summary

This document summarizes the compliance measures implemented to ensure adherence to the System Reference Document 5.1 license and content restrictions.

## Overview

The project is designed to be 5E-compatible while strictly adhering to the Creative Commons Attribution 4.0 International License for SRD content. All proprietary SRD publisher intellectual property is excluded.

## Compliance Measures Implemented

### 1. Content Separation
- **SRD Data**: All SRD-derived content is stored in the `srd_data/` directory
- **Code Separation**: Game logic and mechanics are separated from SRD content
- **Attribution**: All SRD-derived files include required attribution text

### 2. Attribution Requirements
**Required Text**: "This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License."

**Files Requiring Attribution**:
- All files in `srd_data/` directory
- All `.json` files containing SRD content
- All `.md` files containing SRD content

### 3. Restricted Content
The following proprietary SRD publisher content is **NOT PERMITTED**:
- **Settings**: classic fantasy setting, mystic realm, dark domain, established campaign setting
- **Monsters**: psionic horror, eye tyrant
- **Characters**: famous wizard, undying sorcerer
- **Branding**: system-neutral roleplaying framework, system-neutral roleplaying framework, SRD publisher, SRD publisher

### 4. Automated Compliance Enforcement

#### Git Pre-commit Hook
- **Location**: `.hooks/pre-commit-template`
- **Activation**: `ln -s ../../.hooks/pre-commit-template .git/hooks/pre-commit`
- **Functionality**:
  - Scans all staged files for compliance violations
  - Checks for required SRD attribution in `.json` and `.md` files
  - Blocks commits containing restricted keywords
  - Provides detailed violation reports with file and line numbers

#### CLI Compliance Audit Tool
- **Location**: `cli/compliance_check.py`
- **Usage**:
  ```bash
  python cli/compliance_check.py                    # Basic compliance check
  python cli/compliance_check.py --verbose         # Detailed output
  python cli/compliance_check.py --fix-attribution # Auto-fix attribution issues
  ```
- **Features**:
  - Recursive project scanning
  - Attribution validation
  - Restricted keyword detection
  - Auto-fix for missing attribution
  - CI/CD ready (non-zero exit code for violations)
  - Support for `.complianceignore` file

#### Compliance Configuration
- **`.complianceignore`**: Exclude patterns from compliance checks
- **Patterns**: Similar to `.gitignore` syntax
- **Examples**: `*.pyc`, `__pycache__/`, `.env`, `docs/api/`

### 5. Documentation Updates
- **README.md**: Added "5E-Compatible: SRD Compliant" badge and comprehensive compliance tools section
- **License Files**: Full Creative Commons Attribution 4.0 International License included
- **Attribution Files**: Required attribution text in all SRD-derived content

## Compliance Status

### ✅ Implemented
- [x] Content separation and organization
- [x] Required attribution in all SRD files
- [x] Removal of SRD publisher branding
- [x] Git pre-commit hook for automated checking
- [x] CLI compliance audit tool
- [x] Auto-fix functionality for attribution issues
- [x] Comprehensive documentation
- [x] License and attribution files

### ⚠️ Known Issues
- Some documentation files contain restricted keywords in examples and explanations
- These are acceptable as they demonstrate what NOT to include
- The compliance tools correctly identify these for awareness

## Usage Guidelines

### For Developers
1. **Activate the pre-commit hook** before making changes
2. **Run compliance checks** regularly: `python cli/compliance_check.py`
3. **Use auto-fix** for attribution issues: `python cli/compliance_check.py --fix-attribution`
4. **Review violations** and fix restricted content before committing

### For CI/CD
- Include compliance check in build pipeline
- Use exit code to fail builds with violations
- Example: `python cli/compliance_check.py || exit 1`

### For Content Creation
- Only use SRD 5.1 content from the `srd_data/` directory
- Always include required attribution text
- Avoid any proprietary SRD publisher IP
- Use 5E-compatible terminology instead of system-neutral roleplaying framework branding

## Legal Compliance

This project complies with:
- **Creative Commons Attribution 4.0 International License** for SRD content
- **SRD publisher IP restrictions** by excluding proprietary content
- **Copyright law** through proper attribution and content separation

The project is 5E-compatible but is not affiliated with or endorsed by SRD publisher.

## Maintenance

### Regular Tasks
- Run compliance audit monthly: `python cli/compliance_check.py --verbose`
- Update restricted keywords list as needed
- Review and update `.complianceignore` patterns
- Test pre-commit hook functionality

### Updates
- Monitor SRD license changes
- Update attribution text if required
- Review new SRD publisher content for restrictions
- Maintain compliance tools and documentation

---

**Last Updated**: June 28, 2025  
**Compliance Tools Version**: 1.0  
**SRD Version**: 5.1  
**License**: Creative Commons Attribution 4.0 International
