# Security Guidelines for DnD 5E AI-Powered Campaign Manager

## Overview
This document outlines security measures, best practices, and guidelines for the DnD 5E AI-Powered Campaign Manager project.

## 🔐 Security Measures Implemented

### 1. Environment Variables
- **API Keys**: All OpenAI API keys are stored in environment variables
- **Secret Keys**: Flask secret keys use environment variables with fallbacks
- **Database Credentials**: Database connections use environment variables
- **Redis Configuration**: Redis connection details use environment variables

### 2. File Protection
- **`.gitignore`**: Comprehensive patterns to prevent sensitive files from being committed
- **Database Files**: SQLite databases are excluded from version control
- **Log Files**: Application logs are excluded
- **Backup Files**: Automatic backup files are excluded
- **Cache Files**: Python cache and temporary files are excluded

### 3. Code Security
- **No Hardcoded Secrets**: All sensitive values use environment variables
- **Input Validation**: User inputs are validated and sanitized
- **SQL Injection Protection**: Using parameterized queries with SQLAlchemy
- **XSS Protection**: Output is properly escaped in templates

## 🚨 Security Checklist

### Before Committing Code
- [ ] No API keys in code
- [ ] No hardcoded passwords
- [ ] No database files included
- [ ] No log files included
- [ ] No backup files included
- [ ] No cache files included
- [ ] No environment files included

### Before Deployment
- [ ] Environment variables configured
- [ ] Production secret keys set
- [ ] Database credentials secured
- [ ] API keys rotated if needed
- [ ] HTTPS enabled
- [ ] CORS properly configured

## 🔧 Environment Setup

### Required Environment Variables
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Flask Security
FLASK_SECRET_KEY=your_secure_random_secret_key

# Database (if using external database)
DATABASE_URL=your_database_connection_string

# Redis (if using Redis)
REDIS_URL=your_redis_connection_string

# Optional: Development settings
FLASK_ENV=development
DEBUG=False
```

### Generating Secure Secret Keys
```python
import secrets
print(secrets.token_hex(32))  # Generate a secure random key
```

## 🛡️ Best Practices

### 1. API Key Management
- Never commit API keys to version control
- Use environment variables for all API keys
- Rotate API keys regularly
- Use different keys for development and production

### 2. Database Security
- Use parameterized queries
- Validate all user inputs
- Implement proper access controls
- Regular backups with encryption

### 3. Web Application Security
- Use HTTPS in production
- Implement proper CORS policies
- Validate and sanitize all inputs
- Use secure session management

### 4. Code Security
- Regular dependency updates
- Security audits of third-party packages
- Code reviews for security issues
- Automated security testing

## 🚨 Incident Response

### If API Key is Compromised
1. Immediately rotate the API key
2. Check for unauthorized usage
3. Review access logs
4. Update environment variables
5. Notify team members

### If Database is Compromised
1. Isolate the affected system
2. Assess the scope of the breach
3. Restore from secure backup
4. Update credentials
5. Implement additional security measures

## 📋 Security Tools

### Recommended Tools
- **Bandit**: Python security linter
- **Safety**: Check for known security vulnerabilities
- **TruffleHog**: Detect secrets in code
- **GitGuardian**: Monitor for secrets in repositories

### Installation
```bash
pip install bandit safety
```

### Usage
```bash
# Run security checks
bandit -r .
safety check
```

## 🔍 Security Monitoring

### Log Monitoring
- Monitor application logs for suspicious activity
- Set up alerts for failed authentication attempts
- Track API usage patterns
- Monitor database access

### Regular Audits
- Monthly security reviews
- Quarterly dependency updates
- Annual penetration testing
- Continuous vulnerability scanning

## 📞 Security Contacts

### Reporting Security Issues
- **Email**: [Your Email]
- **GitHub Issues**: Use private issues for security reports
- **Response Time**: Within 24 hours for critical issues

### Security Team
- **Lead**: Stephen Miller
- **Backup**: [Backup Contact]

## 📚 Additional Resources

### Documentation
- [OpenAI API Security](https://platform.openai.com/docs/guides/safety-best-practices)
- [Flask Security](https://flask-security.readthedocs.io/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

### Tools
- [GitHub Security](https://github.com/features/security)
- [Snyk Security](https://snyk.io/)
- [SonarQube](https://www.sonarqube.org/)

---

**Last Updated**: June 27, 2025  
**Version**: 1.0  
**Maintainer**: Stephen Miller 