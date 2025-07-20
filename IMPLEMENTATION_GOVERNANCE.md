# SoloHeart Implementation Governance

## Overview

This document defines the governance constraints and implementation guidelines for the SoloHeart repository. SoloHeart is a D&D 5E solo gaming system that must maintain SRD compliance, legal safety, and architectural integrity.

## Core Governance Constraints

### 🎮 **Game Development Constraints**

#### **SRD 5.1 Compliance (CRITICAL)**
- **Content Boundaries**: Only use content from the Systems Reference Document 5.1
- **Legal Attribution**: Proper attribution to Wizards of the Coast LLC required
- **License Compliance**: Creative Commons Attribution 4.0 International License
- **No Proprietary Content**: Never use content from Player's Handbook, Monster Manual, etc.

#### **Character System Constraints**
- **SRD Schema**: All character data must follow SRD 5.1 specifications
- **Open Format**: Character data stored in open, documented JSON format
- **Validation**: Automated validation of character data compliance
- **Attribution Display**: Visible attribution in user interface

### 🏗️ **Architectural Constraints**

#### **Import Isolation (HIGH)**
- **Core Logic**: `solo_heart/` directory must isolate core game logic
- **Web Interface**: Flask and requests allowed in `solo_heart/` for web interface
- **API Dependencies**: Web framework dependencies permitted in web components
- **Testing Boundaries**: Separate tests for web and core components

#### **Dependency Management**
- **Allowed in `solo_heart/`**: Flask, requests, pydantic, fastapi, uvicorn, starlette
- **Core Isolation**: Core game logic must be isolated from web framework
- **API Layer**: External API dependencies isolated in appropriate layers
- **Validation**: Automated checking of import boundaries

### 📚 **Documentation Constraints**

#### **Required Documentation**
- **Onboarding**: `docs/dev_onboarding.md` for contributor experience
- **Governance**: This file for governance constraints
- **SRD Compliance**: Clear documentation of legal compliance
- **Attribution**: Proper attribution documentation

#### **Documentation Standards**
- **Cross-Reference Consistency**: All documentation uses consistent terminology
- **Legal Compliance**: Clear documentation of SRD compliance status
- **Contributor Experience**: Comprehensive onboarding and contribution guides
- **API Documentation**: Clear documentation of web interface and API

## Implementation Guidelines

### **File Structure Requirements**

```
SoloHeart/
├── .github/
│   ├── workflows/
│   │   └── test.yml                  # CI pipeline with governance tests
│   └── PULL_REQUEST_TEMPLATE.md      # Governance compliance checklist
├── scripts/
│   └── check_governance_status.py    # Governance status checker
├── tests/
│   ├── test_import_isolation.py      # Import boundary enforcement
│   └── test_onboarding_integrity.py  # Documentation validation
├── docs/
│   ├── GOVERNANCE.md                 # Governance summary
│   └── dev_onboarding.md             # Developer onboarding
├── solo_heart/                       # Core game logic (Flask allowed)
├── IMPLEMENTATION_GOVERNANCE.md      # This file
├── CONTRIBUTING.md                   # Contribution guidelines
└── README.md                         # Project overview with CI badge
```

### **Testing Requirements**

#### **Governance Tests**
- **Import Isolation**: `tests/test_import_isolation.py` - Enforces dependency boundaries
- **Onboarding Integrity**: `tests/test_onboarding_integrity.py` - Validates documentation
- **CI Integration**: Governance tests run first in CI pipeline
- **Custom Error Messages**: Clear feedback for governance violations

#### **Game-Specific Tests**
- **SRD Compliance**: Validation of character data and game mechanics
- **Legal Safety**: Automated checking for proper attribution
- **Integration Tests**: Full MVP integration testing
- **Compliance Validation**: Automated compliance checking

### **CI/CD Requirements**

#### **Governance Enforcement**
```yaml
- name: Run governance enforcement tests
  run: |
    echo "🔍 Running governance enforcement tests..."
    pytest tests/test_import_isolation.py -v -s || (echo "❌ Import isolation test failed!"; exit 1)
    pytest tests/test_onboarding_integrity.py -v -s || (echo "❌ Onboarding integrity test failed!"; exit 1)
```

#### **Documentation Regeneration**
```yaml
- name: Regenerate documentation if requested
  if: hashFiles('.regen_docs') != ''
  run: |
    echo "📚 Regenerating documentation..."
    python scripts/generate_docs.py
```

### **PR Template Requirements**

#### **Governance Compliance Checklist**
- [ ] Import isolation test passes (Flask allowed in solo_heart/)
- [ ] Onboarding integrity test passes (documentation is consistent)
- [ ] SRD compliance maintained (no proprietary content)
- [ ] Legal attribution properly documented
- [ ] Governance constraints respected

## Repository-Specific Adaptations

### **Flask Integration (SoloHeart-Specific)**

#### **Allowed Dependencies in `solo_heart/`**
```python
# ✅ Allowed for web interface
import flask
import requests
from flask import Flask, request, jsonify
import pydantic
from fastapi import FastAPI
import uvicorn
from starlette import applications
```

#### **Core Logic Isolation**
```python
# ✅ Core game logic should be isolated
from solo_heart.game_logic import CharacterSystem
from solo_heart.srd_compliance import SRDValidator
from solo_heart.attribution import AttributionManager
```

### **SRD Compliance Patterns**

#### **Character Data Structure**
```python
# ✅ SRD 5.1 compliant character data
character_data = {
    "name": "Character Name",
    "race": "Human",  # SRD races only
    "class": "Fighter",  # SRD classes only
    "level": 1,
    "ability_scores": {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8
    }
}
```

#### **Attribution Requirements**
```python
# ✅ Required attribution
attribution_text = """
This project uses content from the Systems Reference Document 5.1 (SRD 5.1) 
by Wizards of the Coast LLC, available under the Creative Commons Attribution 
4.0 International License (CC BY 4.0).
"""
```

## Compliance Verification

### **Automated Checks**
- **Import Isolation**: Automated scanning of import boundaries
- **Documentation Consistency**: Validation of cross-references
- **SRD Compliance**: Automated checking of content compliance
- **Attribution Validation**: Verification of proper attribution

### **Manual Verification**
```bash
# Run governance tests
pytest tests/test_import_isolation.py -v
pytest tests/test_onboarding_integrity.py -v

# Check governance status
python scripts/check_governance_status.py

# Verify SRD compliance
python security_check.py
```

## Governance Drift Prevention

### **Regular Monitoring**
- **Weekly**: Governance status checks
- **Monthly**: Documentation consistency reviews
- **Quarterly**: SRD compliance validation
- **Annually**: Legal compliance audits

### **Drift Indicators**
- Import isolation test failures
- Documentation inconsistency warnings
- SRD compliance violations
- Missing attribution
- CI badge status changes

## Success Criteria

### **Architectural Integrity**
- **Import Boundaries**: Clear separation between core logic and web interface
- **Dependency Management**: Appropriate use of Flask and web dependencies
- **Testing Coverage**: Comprehensive governance and game-specific tests
- **Documentation Quality**: Complete and consistent documentation

### **Legal Compliance**
- **SRD Compliance**: All content from SRD 5.1 only
- **Attribution**: Proper attribution to Wizards of the Coast
- **License Compliance**: Creative Commons Attribution 4.0
- **Content Validation**: Automated checking for compliance

### **Contributor Experience**
- **Onboarding**: Clear contributor onboarding documentation
- **Governance**: Comprehensive governance documentation
- **PR Templates**: Enforced governance compliance checklists
- **CI Integration**: Automated governance enforcement

---

**This governance system ensures SoloHeart maintains game development standards, SRD compliance, and architectural integrity while providing a clear contributor experience.** 