This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# Pull Request

## 📝 Description

Brief description of the changes made in this PR.

## 🔧 Changes Made

- [ ] Change 1
- [ ] Change 2
- [ ] Change 3

## Governance Checklist ✅

Please confirm before submitting:

- [ ] `test_import_isolation.py` passes
- [ ] `test_onboarding_integrity.py` passes
- [ ] I updated `ONBOARDING.md` if contributor experience changed
- [ ] Any new dependencies are justified and documented
- [ ] Docs are regenerated if `.regen_docs` is present
- [ ] I ran the test suite locally

> NOTE: CI will fail if governance is violated

## 🧪 Testing

- [ ] All existing tests pass
- [ ] New tests have been added for new functionality
- [ ] Import isolation test passes (no external dependencies in solo_heart/)
- [ ] Onboarding integrity test passes (documentation is consistent)
- [ ] SRD compliance is maintained

## 📚 Documentation

- [ ] Code is properly documented
- [ ] README.md has been updated if necessary
- [ ] API documentation has been updated if necessary
- [ ] SRD compliance is maintained

## 🔍 Review Checklist

- [ ] Code follows project style guidelines
- [ ] No external dependencies added to solo_heart/ (use api/ for API dependencies)
- [ ] All imports are properly isolated
- [ ] Documentation is consistent across files
- [ ] Governance constraints are respected
- [ ] SRD compliance is maintained

## 🚨 Breaking Changes

- [ ] This PR does not introduce breaking changes
- [ ] If breaking changes exist, they are documented below

## 📋 Additional Notes

Any additional information that reviewers should know. 