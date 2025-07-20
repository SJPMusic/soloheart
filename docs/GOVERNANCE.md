# Governance Expectations

## Overview

This document summarizes the governance expectations for the SoloHeart repository. For complete governance details, see [IMPLEMENTATION_GOVERNANCE.md](../IMPLEMENTATION_GOVERNANCE.md).

## Core Governance Principles

### 🎮 **Game Development Standards**
- **SRD 5.1 Compliance**: All game mechanics follow official D&D 5E rules
- **Legal Attribution**: Proper attribution to Wizards of the Coast for SRD content
- **Flask Integration**: Web interface dependencies allowed in `solo_heart/` directory
- **Game-Appropriate Isolation**: Flask and requests allowed for web interface components

### 📚 **Documentation Standards**
- **Onboarding**: Complete contributor onboarding documentation in `docs/dev_onboarding.md`
- **Governance**: Comprehensive governance documentation in `IMPLEMENTATION_GOVERNANCE.md`
- **SRD Compliance**: Clear documentation of legal compliance and attribution
- **Cross-Reference Consistency**: All documentation must use consistent terminology

### 🧪 **Testing Requirements**
- **Import Isolation Tests**: Automated testing of dependency boundaries (Flask allowed)
- **Onboarding Integrity Tests**: Validation of documentation consistency
- **Governance Enforcement**: CI integration of governance tests
- **SRD Compliance Tests**: Validation of legal compliance and attribution

### 🔄 **CI/CD Integration**
- **Governance Tests**: Automated governance enforcement in CI pipeline
- **Early Failure**: Governance tests run first with custom error messages
- **Visual Status**: CI badges display governance compliance status
- **Documentation Regeneration**: Optional documentation updates triggered by `.regen_docs`

## Repository Structure

```
SoloHeart/
├── .github/
│   ├── workflows/
│   │   └── test.yml                  # CI pipeline with governance tests
│   └── PULL_REQUEST_TEMPLATE.md      # Governance compliance checklist
├── scripts/
│   └── check_governance_status.py    # Governance status checker
├── tests/
│   ├── test_import_isolation.py      # Import boundary enforcement (Flask allowed)
│   └── test_onboarding_integrity.py  # Documentation validation
├── docs/
│   ├── GOVERNANCE.md                 # This file
│   └── dev_onboarding.md             # Developer onboarding guide
├── IMPLEMENTATION_GOVERNANCE.md      # Complete governance documentation
├── CONTRIBUTING.md                   # Contribution guidelines
└── README.md                         # Project overview with CI badge
```

## Enforcement Mechanisms

### **Pre-commit Checks**
- Manual governance compliance checklist in PR templates
- Required verification of governance test results
- Documentation review requirements
- SRD compliance validation

### **CI Automation**
- Automated governance test execution on every commit
- Custom error messages for governance violations
- Early failure to prevent governance drift
- SRD compliance checking

### **Visual Indicators**
- CI badges showing governance compliance status
- Clear status reporting in governance status checker
- Repository-specific achievement highlighting

## Key Achievements

### **✅ SoloHeart Governance Implementation**
- **Game-Appropriate Isolation**: Flask/requests allowed for web interface
- **SRD Compliance**: Legal and attribution requirements met
- **Comprehensive Testing**: All governance tests passing
- **CI Integration**: Automated enforcement active

## Compliance Verification

### **Manual Verification**
```bash
# Run governance tests locally
pytest tests/test_import_isolation.py -v
pytest tests/test_onboarding_integrity.py -v

# Check governance status
python scripts/check_governance_status.py
```

### **Automated Verification**
- CI pipeline automatically runs governance tests
- PR template enforces governance compliance checklist
- Governance status checker provides comprehensive reporting
- SRD compliance validation

## SRD Compliance Requirements

### **Legal Requirements**
- **Attribution**: Proper attribution to Wizards of the Coast
- **License Compliance**: Creative Commons Attribution 4.0 International License
- **Content Boundaries**: Only use SRD 5.1 content, no proprietary material
- **Documentation**: Clear documentation of compliance status

### **Technical Requirements**
- **Character Data**: SRD 5.1-compliant JSON schema
- **Game Mechanics**: Official D&D 5E rules only
- **Content Validation**: Automated checking for SRD compliance
- **Attribution Display**: Visible attribution in user interface

## Governance Drift Prevention

### **Regular Monitoring**
- Weekly governance status checks
- Monthly documentation consistency reviews
- Quarterly SRD compliance validation
- Regular legal compliance audits

### **Drift Indicators**
- Import isolation test failures
- Documentation inconsistency warnings
- CI badge status changes
- SRD compliance violations
- Governance status checker alerts

## Repository-Specific Adaptations

### **Flask Integration**
- **Web Interface**: Flask and requests allowed in `solo_heart/` directory
- **API Dependencies**: Web framework dependencies permitted
- **Isolation Boundaries**: Core game logic isolated from web interface
- **Testing Strategy**: Separate tests for web and core components

### **Game Development Patterns**
- **SRD Compliance**: All game mechanics follow official rules
- **Character System**: SRD 5.1-compliant character data structures
- **Legal Safety**: Comprehensive compliance checking
- **Attribution**: Proper attribution throughout the system

## Related Documentation

- [IMPLEMENTATION_GOVERNANCE.md](../IMPLEMENTATION_GOVERNANCE.md) - Complete governance documentation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [docs/dev_onboarding.md](dev_onboarding.md) - Developer onboarding guide
- [solo_heart/ATTRIBUTION.md](../solo_heart/ATTRIBUTION.md) - Legal compliance and attributions

---

**This governance system ensures SoloHeart maintains game development standards, SRD compliance, and contributor experience quality.** 