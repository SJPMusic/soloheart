This work includes material from the System Reference Document 5.1 and is licensed under the Creative Commons Attribution 4.0 International License.

# 🔐 GitHub Repo Hardening for SoloHeart

To protect production integrity and ensure secure deployment:

## ✅ Branch Protection Rules

### Protect Critical Branches
- **`main`**: Primary production branch
- **`release/mvp_ready`**: MVP release branch

### Required Settings
- ✅ **Require pull request reviews** before merging
- ✅ **Require status checks** to pass before merging
- ✅ **Require branches to be up to date** before merging
- ✅ **Restrict pushes** that create files that match specified patterns
- ✅ **Require linear history** (no merge commits)

### Status Check Requirements
- **SoloHeart CI**: Must pass all integration tests
- **Compliance Check**: Must pass restricted term validation
- **Test Coverage**: Must maintain minimum coverage threshold

## 🔑 Tag and Commit Signing

### GPG Key Setup
```bash
# Generate GPG key for signing
gpg --full-generate-key

# Configure Git to use GPG signing
git config --global user.signingkey YOUR_GPG_KEY_ID
git config --global commit.gpgsign true
git config --global tag.gpgsign true
```

### Enforce Signed Commits
- ✅ **Require signed commits** on protected branches
- ✅ **Require signed tags** for releases
- ✅ **Verify GPG signatures** in CI pipeline

## 🛡️ Compliance Hooks

### Pre-commit Hook Configuration
```bash
# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Configure .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: compliance-check
        name: Compliance Validation
        entry: python -c "import tests.full_mvp_integration_test as test; test.run_compliance_check()"
        language: system
        pass_filenames: false
```

### CI Compliance Enforcement
```yaml
# In .github/workflows/test.yml
- name: Run compliance check
  run: |
    python -c "import tests.full_mvp_integration_test as test; test.run_compliance_check()"
```

## 🔒 Secrets Management

### Environment Variables
- ✅ **Never commit API keys** to repository
- ✅ **Use GitHub Secrets** for sensitive data
- ✅ **Rotate keys regularly**
- ✅ **Limit access** to production secrets

### Required Secrets
```yaml
# For Render deployment
OPENROUTER_API_KEY: "{{ secrets.OPENROUTER_API_KEY }}"
TNE_BASE_URL: "{{ secrets.TNE_BASE_URL }}"

# For CI/CD
TEST_API_KEY: "{{ secrets.TEST_API_KEY }}"
```

### Secret Validation
```bash
# Check for hardcoded secrets
grep -r "sk-" . --exclude-dir=node_modules --exclude-dir=venv
grep -r "api_key" . --exclude-dir=node_modules --exclude-dir=venv
```

## 🚫 Security Restrictions

### File Access Controls
- ✅ **Restrict access** to sensitive configuration files
- ✅ **Use .gitignore** for local environment files
- ✅ **Validate file permissions** in CI

### Code Review Requirements
- ✅ **Minimum 1 reviewer** for all PRs
- ✅ **Code owner review** for critical files
- ✅ **Security review** for new dependencies

## 🔍 Monitoring and Alerts

### Security Scanning
```yaml
# Add to .github/workflows/security.yml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security scan
        uses: github/codeql-action/init@v2
        with:
          languages: python, javascript
```

### Dependency Monitoring
- ✅ **Automated dependency updates** with Dependabot
- ✅ **Vulnerability scanning** for known CVEs
- ✅ **License compliance** checking

## 📋 Security Checklist

### Repository Setup
- [ ] Branch protection rules configured
- [ ] GPG signing enabled for commits and tags
- [ ] Pre-commit hooks installed
- [ ] Secrets properly configured
- [ ] Security scanning enabled

### CI/CD Security
- [ ] All tests pass before merge
- [ ] Compliance validation enforced
- [ ] Secrets not exposed in logs
- [ ] Dependency scanning active
- [ ] Code signing verified

### Access Control
- [ ] Minimal admin access granted
- [ ] Two-factor authentication required
- [ ] Regular access reviews scheduled
- [ ] Audit logs monitored

## 🚨 Incident Response

### Security Breach Protocol
1. **Immediate Response**
   - Revoke compromised credentials
   - Assess scope of exposure
   - Notify stakeholders

2. **Investigation**
   - Review access logs
   - Identify root cause
   - Document findings

3. **Recovery**
   - Rotate all secrets
   - Update security measures
   - Implement additional safeguards

### Contact Information
- **Security Team**: security@project-domain.com
- **Emergency Contact**: emergency@project-domain.com
- **GitHub Security**: Report via GitHub Security tab

## 📚 Additional Resources

- **GitHub Security Best Practices**: https://docs.github.com/en/security
- **OWASP Security Guidelines**: https://owasp.org/
- **Python Security**: https://python-security.readthedocs.io/
- **Node.js Security**: https://nodejs.org/en/docs/guides/security/

---

**Remember: Security is everyone's responsibility. Stay vigilant and report any concerns immediately.** 