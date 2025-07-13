# Security Guidelines for DnD 5E AI-Powered Campaign Manager

## Overview
This document outlines security measures, best practices, and guidelines for the DnD 5E AI-Powered Campaign Manager project.

## 🔐 Security Measures Implemented

### 1. Environment Variables ✅
- **API Keys**: All OpenAI API keys are stored in environment variables
- **Secret Keys**: Flask secret keys use environment variables with fallbacks
- **Database Credentials**: Database connections use environment variables
- **Redis Configuration**: Redis connection details use environment variables

### 2. File Protection ✅
- **`.gitignore`**: Comprehensive patterns to prevent sensitive files from being committed
- **Database Files**: SQLite databases are excluded from version control
- **Log Files**: Application logs are excluded
- **Backup Files**: Automatic backup files are excluded
- **Cache Files**: Python cache and temporary files are excluded

### 3. Code Security ✅
- **No Hardcoded Secrets**: All sensitive values use environment variables
- **Input Validation**: User inputs are validated and sanitized
- **SQL Injection Protection**: Using parameterized queries with SQLAlchemy
- **XSS Protection**: Output is properly escaped in templates

## 🚨 Security Checklist

### Before Committing Code ✅
- [x] No API keys in code
- [x] No hardcoded passwords
- [x] No database files included
- [x] No log files included
- [x] No backup files included
- [x] No cache files included
- [x] No environment files included

### Before Deployment ✅
- [x] Environment variables configured
- [x] Production secret keys set
- [x] Database credentials secured
- [x] API keys rotated if needed
- [x] HTTPS enabled
- [x] CORS properly configured

### Enhanced Security Measures ✅
- [x] **Input Sanitization**: All user inputs are validated and sanitized
- [x] **Error Message Sanitization**: No sensitive information in error messages
- [x] **Session Security**: Secure session management with environment variables
- [x] **Log Security**: No sensitive data logged to files
- [x] **API Key Rotation**: Support for API key rotation
- [x] **Environment Validation**: Startup checks for required environment variables
- [x] **Secure Headers**: Proper security headers in responses
- [x] **Rate Limiting**: Basic rate limiting implemented
- [x] **CORS Configuration**: Proper CORS settings for production
- [x] **HTTPS Enforcement**: HTTPS required in production
- [x] **Content Security Policy**: CSP headers implemented
- [x] **XSS Protection**: XSS protection headers enabled
- [x] **SQL Injection Prevention**: Parameterized queries used throughout

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

## 🛡️ Enhanced Security Features

### 1. Input Validation & Sanitization
```python
import re
from html import escape

def sanitize_input(user_input: str) -> str:
    """Sanitize user input to prevent XSS and injection attacks."""
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', user_input)
    # HTML escape remaining content
    return escape(sanitized)

def validate_api_key(api_key: str) -> bool:
    """Validate API key format without exposing the key."""
    if not api_key or len(api_key) < 20:
        return False
    return True
```

### 2. Secure Logging
```python
import logging
import re

class SecureLogger:
    """Logger that redacts sensitive information."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.sensitive_patterns = [
            r'sk-[a-zA-Z0-9]{20,}',  # OpenAI API keys
            r'pk_[a-zA-Z0-9]{20,}',  # OpenAI public keys
            r'Bearer [a-zA-Z0-9]{20,}',  # Bearer tokens
        ]
    
    def _redact_sensitive_data(self, message: str) -> str:
        """Redact sensitive data from log messages."""
        for pattern in self.sensitive_patterns:
            message = re.sub(pattern, '[REDACTED]', message)
        return message
    
    def info(self, message: str):
        """Log info message with sensitive data redacted."""
        safe_message = self._redact_sensitive_data(message)
        self.logger.info(safe_message)
    
    def error(self, message: str):
        """Log error message with sensitive data redacted."""
        safe_message = self._redact_sensitive_data(message)
        self.logger.error(safe_message)
```

### 3. Environment Variable Validation
```python
import os
from typing import List, Optional

def validate_environment() -> List[str]:
    """Validate that all required environment variables are set."""
    required_vars = [
        'FLASK_SECRET_KEY',
        'OPENAI_API_KEY',
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    return missing_vars

def check_security_configuration():
    """Check security configuration on startup."""
    missing_vars = validate_environment()
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # Validate API key format
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and not validate_api_key(api_key):
        raise ValueError("Invalid API key format")
```

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

**Last Updated**: July 12, 2025  
**Version**: 2.0  
**Maintainer**: Stephen Miller 