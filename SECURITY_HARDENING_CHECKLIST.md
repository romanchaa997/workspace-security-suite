# Security Hardening Checklist

## OWASP Top 10 Compliance

### 1. Broken Authentication & Session Management
- [ ] Implement strong password policy (12+ chars, uppercase, lowercase, numbers, special chars)
- [ ] Enable multi-factor authentication (MFA) for all admin accounts
- [ ] Implement session timeout (30 minutes inactivity)
- [ ] Use secure session tokens (JWT with HS256+ or RS256)
- [ ] Implement CSRF protection on all state-changing operations
- [ ] Validate all authentication tokens server-side
- [ ] Use HTTP-only and Secure flags on authentication cookies
- [ ] Implement account lockout after 5 failed login attempts
- [ ] Log all authentication events (success and failure)
- [ ] Rotate session tokens regularly (every 24 hours)

### 2. Sensitive Data Exposure
- [ ] Enable HTTPS/TLS 1.2+ for all connections
- [ ] Use strong cipher suites (AES-256-GCM preferred)
- [ ] Implement HSTS with minimum 1 year max-age
- [ ] Encrypt sensitive data at rest (AES-256)
- [ ] Mask sensitive data in logs (PII, API keys, passwords)
- [ ] Use environment variables for secrets (not hardcoded)
- [ ] Implement secret rotation (every 90 days)
- [ ] Disable weak protocols (SSLv2, SSLv3, TLS 1.0, 1.1)
- [ ] Use certificate pinning for critical APIs
- [ ] Validate SSL certificates in all external API calls

### 3. Injection Attacks
- [ ] Use parameterized queries for all database operations
- [ ] Validate and sanitize all user inputs
- [ ] Use allowlists for file uploads (whitelist extensions)
- [ ] Implement Web Application Firewall (WAF) rules
- [ ] Escape output based on context (HTML, URL, JavaScript)
- [ ] Use prepared statements in ORMs
- [ ] Implement rate limiting to prevent brute force
- [ ] Log and alert on suspicious input patterns
- [ ] Use content security headers (CSP, X-Content-Type-Options)
- [ ] Implement SQL injection detection and blocking

### 4. Broken Access Control
- [ ] Implement role-based access control (RBAC)
- [ ] Validate authorization on every API endpoint
- [ ] Use principle of least privilege for all accounts
- [ ] Implement attribute-based access control (ABAC) where needed
- [ ] Audit role assignments monthly
- [ ] Implement service accounts with minimal permissions
- [ ] Restrict admin console access by IP address
- [ ] Log all authorization decisions
- [ ] Implement privileged access management (PAM)
- [ ] Regular review of user permissions

### 5. Security Misconfiguration
- [ ] Disable unnecessary services and features
- [ ] Remove default accounts and credentials
- [ ] Configure security headers (X-Frame-Options, etc.)
- [ ] Implement Content Security Policy (CSP)
- [ ] Use security scanner to verify configuration
- [ ] Keep all dependencies updated
- [ ] Configure firewall rules (allow minimum necessary traffic)
- [ ] Implement AWS IAM or equivalent role-based access
- [ ] Use AWS Security Groups with least privilege
- [ ] Enable AWS CloudTrail and VPC Flow Logs

### 6. Cryptography & Key Management
- [ ] Use industry-standard encryption algorithms
- [ ] Store encryption keys separately from data
- [ ] Implement key rotation (annually minimum)
- [ ] Use Hardware Security Module (HSM) for key storage
- [ ] Implement key versioning
- [ ] Never hardcode encryption keys
- [ ] Use random initialization vectors (IVs)
- [ ] Implement secure key exchange mechanism
- [ ] Monitor key usage and access
- [ ] Have key recovery procedures documented

---

## TLS/SSL Configuration

### Certificate Management
- [ ] Use valid CA-signed certificates
- [ ] Certificate covers all domains (or use wildcard)
- [ ] Certificate validity: 1 year or less
- [ ] Auto-renewal implemented (at 30 days before expiry)
- [ ] Certificate monitoring and alerting
- [ ] Support for certificate pinning
- [ ] Backup certificates and keys in secure location
- [ ] Document certificate renewal process
- [ ] Test certificate renewal in staging first

### Cipher Suite Configuration
- [ ] Disable SSLv2, SSLv3, TLS 1.0, 1.1
- [ ] Support TLS 1.2 and 1.3 minimum
- [ ] Prefer TLS 1.3 (AEAD ciphers)
- [ ] Use strong cipher suites only:
  - [ ] TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - [ ] TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
  - [ ] TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
  - [ ] TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
- [ ] Disable cipher suites with MD5, DES
- [ ] Configure forward secrecy (ECDHE, DHE)
- [ ] Test with SSL Labs (target: A+ grade)
- [ ] Monitor for weak cipher usage

### HSTS Configuration
- [ ] Enable HSTS header: Strict-Transport-Security
- [ ] Set max-age to 31536000 (1 year) minimum
- [ ] Include subdomains: includeSubDomains
- [ ] Enable preloading if applicable: preload
- [ ] Test HSTS with online validators
- [ ] Document HSTS policy

---

## RBAC Audit Checklist

### Role Definition
- [ ] Clearly document all roles
- [ ] Define permissions for each role
- [ ] Use principle of least privilege
- [ ] Implement minimum 3-4 core roles:
  - [ ] Viewer (read-only access)
  - [ ] Editor (read-write for own resources)
  - [ ] Admin (full access to module)
  - [ ] Super Admin (full system access)
- [ ] Implement custom roles if needed
- [ ] Document role creation/modification process

### User Assignment
- [ ] Monthly audit of role assignments
- [ ] Verify each user has appropriate role
- [ ] Remove access immediately upon departure
- [ ] Implement role expiration (annual)
- [ ] Document role change history
- [ ] Approve all role changes
- [ ] Test permission enforcement

### API Authorization
- [ ] Check role on EVERY API endpoint
- [ ] Implement consistent authorization checks
- [ ] Return 403 (Forbidden) for unauthorized access
- [ ] Log all authorization failures
- [ ] Alert on repeated authorization failures
- [ ] Test with multiple user roles

### Admin Access
- [ ] Admin accounts require MFA
- [ ] Limit admin account creation (max 3)
- [ ] Monthly review of admin accounts
- [ ] Separate admin and user accounts
- [ ] Implement admin action logging
- [ ] Use dedicated admin IP ranges
- [ ] Require admin approval for sensitive actions

---

## Vulnerability Management

### Dependency Scanning
- [ ] Scan dependencies weekly with OWASP Dependency-Check
- [ ] Use GitHub Dependabot for continuous monitoring
- [ ] Track all third-party libraries and versions
- [ ] Document all dependencies
- [ ] Update critical vulnerabilities within 7 days
- [ ] Maintain Bill of Materials (BOM)
- [ ] Test updates in staging before production

### Code Security
- [ ] Use static application security testing (SAST) tool
- [ ] Run security linters on all code changes
- [ ] Implement code review process
- [ ] Security training for developers
- [ ] Enforce secure coding standards
- [ ] Document security-critical code
- [ ] Regular penetration testing (quarterly)

### Infrastructure Security
- [ ] Regular vulnerability scanning (weekly)
- [ ] Patch management process documented
- [ ] Critical patches applied within 48 hours
- [ ] Security group audits (monthly)
- [ ] Network segmentation verified
- [ ] DDoS protection enabled
- [ ] WAF rules reviewed quarterly

---

## Monitoring & Logging

### Log Collection
- [ ] Centralize all security logs
- [ ] Retain logs for minimum 90 days
- [ ] Enable audit logging for all critical operations
- [ ] Log authentication attempts (success & failure)
- [ ] Log authorization decisions
- [ ] Log data access and modifications
- [ ] Log configuration changes
- [ ] Implement tamper protection for logs
- [ ] Regular log review (daily for critical events)

### Alerting
- [ ] Alert on multiple failed login attempts (5+)
- [ ] Alert on privilege escalation attempts
- [ ] Alert on unexpected data access
- [ ] Alert on configuration changes
- [ ] Alert on certificate expiry (30 days before)
- [ ] Alert on vulnerability discoveries
- [ ] Test alert mechanisms monthly
- [ ] Document alert response procedures

---

## Incident Response

- [ ] Incident response plan documented
- [ ] Incident response team identified
- [ ] Contact list maintained and tested
- [ ] Response procedures documented for:
  - [ ] Data breach
  - [ ] Malware infection
  - [ ] DDoS attack
  - [ ] Unauthorized access
  - [ ] Service unavailability
- [ ] Regular incident response drills (quarterly)
- [ ] Post-incident reviews documented
- [ ] Forensic capability available

---

## Compliance & Standards

- [ ] SOC 2 Type 2 compliance verified
- [ ] ISO 27001 controls implemented
- [ ] GDPR compliance (if applicable)
- [ ] HIPAA compliance (if healthcare)
- [ ] PCI DSS compliance (if payment card data)
- [ ] Annual security audit conducted
- [ ] Penetration test completed annually
- [ ] Compliance documentation maintained
- [ ] Third-party security assessment completed

---

## Sign-Off

**Security Officer:** _________________ **Date:** _______
**IT Manager:** _________________ **Date:** _______
**Project Lead:** _________________ **Date:** _______

---

**Last Updated:** January 15, 2025  
**Next Review:** April 15, 2025

For security inquiries: security@workspace-security.dev
