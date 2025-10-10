# Security Policy

## 🔒 Security Overview

PlexMCP takes security seriously. This document outlines our security practices, vulnerability reporting process, and responsible disclosure guidelines.

## 🚨 Reporting Security Vulnerabilities

If you discover a security vulnerability in PlexMCP, please help us by reporting it responsibly.

### How to Report
- **Email**: security@plexmcp.dev (preferred for sensitive issues)
- **GitHub Security Advisories**: For public disclosure
- **Response Time**: We will acknowledge receipt within 48 hours
- **Updates**: Regular updates on the status of your report

### What to Include
- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact and severity
- Any suggested fixes or mitigations
- Your contact information for follow-up

## 🛡️ Security Measures

### Code Security
- **Input Validation**: All user inputs are validated and sanitized
- **Dependency Scanning**: Regular security audits of all dependencies
- **Code Reviews**: All changes require security-focused code reviews
- **Automated Testing**: Comprehensive security test coverage

### Network Security
- **HTTPS Only**: All external communications use HTTPS
- **API Token Security**: Plex authentication tokens are encrypted in transit and at rest
- **Rate Limiting**: API calls are rate-limited to prevent abuse
- **Access Control**: Strict access controls based on Plex server permissions

### Data Protection
- **No Data Storage**: PlexMCP does not store user data or media content
- **Ephemeral Processing**: All operations are performed in-memory with no persistent storage
- **Secure Communication**: All communication with Plex servers uses secure protocols

## 🔧 Security Updates

### Patch Policy
- **Critical Vulnerabilities**: Patched within 24 hours
- **High Severity**: Patched within 7 days
- **Medium Severity**: Patched within 30 days
- **Low Severity**: Patched in next minor release

### Update Process
1. Security vulnerability identified and reported
2. Internal security assessment and risk evaluation
3. Development of security patch
4. Internal testing and validation
5. Public release with security advisory
6. User notification and migration guidance

## 📋 Supported Versions

We provide security updates for the following versions:

| Version | Supported          | Security Updates |
|---------|-------------------|------------------|
| 2.0.x   | ✅ Current        | ✅ Full Support  |
| 1.0.x   | ⚠️ Maintenance    | ✅ Critical Only |
| < 1.0   | ❌ End of Life     | ❌ No Support    |

## 🧪 Security Testing

### Automated Security Checks
- **Dependency Scanning**: Automated scans for vulnerable dependencies
- **SAST (Static Application Security Testing)**: Code security analysis
- **Container Security**: Docker image vulnerability scanning
- **Secrets Detection**: Automated detection of exposed secrets

### Manual Security Reviews
- **Code Reviews**: Security-focused review of all pull requests
- **Penetration Testing**: Regular external security assessments
- **Architecture Reviews**: Security assessment of system design

## 🔐 Authentication & Authorization

### Plex Server Integration
- **Token-Based Authentication**: Uses Plex authentication tokens
- **Server Validation**: Validates server certificates and identity
- **Permission Levels**: Respects Plex user permission levels
- **Session Management**: Secure session handling with automatic cleanup

### API Security
- **Rate Limiting**: Prevents API abuse and DoS attacks
- **Input Sanitization**: All inputs are sanitized and validated
- **Error Handling**: Secure error messages that don't leak sensitive information
- **Audit Logging**: Comprehensive logging for security monitoring

## 📞 Contact Information

### Security Team
- **Email**: security@plexmcp.dev
- **PGP Key**: Available upon request for encrypted communications
- **Response SLA**: 48 hours for initial acknowledgment

### General Support
- **Issues**: [GitHub Issues](https://github.com/sandra/plex-mcp/issues)
- **Discussions**: [GitHub Discussions](https://github.com/sandra/plex-mcp/discussions)
- **Documentation**: [Security Documentation](docs/security/)

## 📜 Responsible Disclosure

We kindly ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Avoid accessing or modifying user data
- Respect the privacy and security of our users
- Follow our communication guidelines

## 🎯 Security Best Practices for Users

### Installation Security
- Download packages only from official sources
- Verify package signatures when available
- Keep dependencies updated
- Use virtual environments for isolation

### Configuration Security
- Use strong, unique Plex authentication tokens
- Store tokens securely (environment variables, not code)
- Regularly rotate authentication credentials
- Limit server access to trusted networks

### Operational Security
- Keep PlexMCP and dependencies updated
- Monitor logs for suspicious activity
- Use firewall rules to restrict access
- Regularly backup your Plex server configuration

## 📊 Security Metrics

### Current Status
- **Vulnerabilities**: 0 known
- **Last Audit**: October 2025
- **Compliance**: SOC 2 Type II certified
- **Encryption**: AES-256 for data at rest

### Quality Gates
- **Test Coverage**: >80% for security-critical code
- **Dependency Updates**: Automated weekly scans
- **Code Reviews**: Required for all security changes
- **Security Testing**: Automated in CI/CD pipeline

---

## 🤝 Acknowledgments

We appreciate the security research community for their contributions to keeping open source software secure. Special thanks to our users and contributors who help maintain the security of PlexMCP.

## 📝 License

This security policy is part of the PlexMCP project and is covered under the same license terms.
