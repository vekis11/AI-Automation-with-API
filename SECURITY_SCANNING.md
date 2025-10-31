# Security Scanning Guide

This repository uses automated security scanning for Infrastructure as Code (IaC) misconfigurations and secret detection in CI/CD pipelines.

## 🔒 Tools Overview

### 1. **Trivy** (All-in-One Scanner)
- **Purpose**: Comprehensive security scanner for vulnerabilities, misconfigurations, and secrets
- **Features**:
  - Container image scanning
  - File system scanning
  - IaC configuration scanning
  - Secret detection
- **Why Trivy**: Fast, accurate, and covers multiple security domains
- **Official Docs**: https://github.com/aquasecurity/trivy

### 2. **Checkov** (IaC Security Scanner)
- **Purpose**: Static analysis for IaC files to detect security misconfigurations
- **Supports**:
  - Dockerfiles
  - Docker Compose files
  - Terraform
  - Kubernetes
  - CloudFormation
  - And more
- **Why Checkov**: Industry-leading IaC security policies with 1000+ checks
- **Official Docs**: https://github.com/bridgecrewio/checkov

### 3. **Gitleaks** (Secret Scanner)
- **Purpose**: Fast secret scanning using regex patterns
- **Features**:
  - Scans git history
  - Real-time scanning
  - Customizable patterns
- **Why Gitleaks**: Lightweight, fast, and highly accurate for secret detection
- **Official Docs**: https://github.com/gitleaks/gitleaks

## 🚀 GitHub Actions Workflow

The security scanning runs automatically on:
- **Pull Requests** to `main` or `develop` branches
- **Pushes** to `main` or `develop` branches
- **Manual triggers** via workflow_dispatch

### Workflow Behavior

#### On Pull Requests:
- **Trivy**: Fails on CRITICAL/HIGH severity issues
- **Checkov**: Fails if critical security issues are found
- **Gitleaks**: Fails if secrets are detected
- **Result**: Blocks merge if security issues are found

#### On Push:
- **All scanners**: Report issues but don't fail (informational)
- **Result**: Provides visibility without blocking deployments

## 📋 Scan Coverage

### Files Scanned:
- ✅ Dockerfile
- ✅ docker-compose.yml / docker-compose.prod.yml
- ✅ All source code files
- ✅ Configuration files
- ✅ Entire git history (for secrets)

### Security Checks:
- Container vulnerabilities
- Misconfigured permissions
- Exposed secrets/credentials
- Insecure network configurations
- Missing security headers
- Hardcoded passwords/tokens
- Exposed ports and services

## 🔧 Configuration

### Customizing Checks

#### Trivy Configuration
Edit `.github/workflows/security-scan.yml`:
```yaml
severity: 'CRITICAL,HIGH,MEDIUM'  # Adjust severity levels
scan-type: 'fs'  # Options: fs, image, config
```

#### Checkov Configuration
To skip specific checks:
```yaml
--skip-check CKV_DOCKER_3  # Skip specific check ID
--soft-fail  # Don't fail on findings
```

#### Gitleaks Configuration
Create/update `.gitleaksignore` to exclude patterns:
```
# Patterns to ignore
**/test_*.py
**/*.md
```

## 📊 Viewing Results

### GitHub Security Tab
- Trivy results are uploaded to GitHub Security → Code scanning
- View detailed findings with remediation steps

### GitHub Actions Logs
- Each scan job shows detailed output
- Check individual job logs for specific issues

### Artifacts
- Gitleaks reports are saved as artifacts
- Download and review JSON/TXT reports

## 🛠️ Running Scans Locally

### Install Tools

```bash
# Install Trivy
# macOS
brew install trivy

# Linux
wget https://github.com/aquasecurity/trivy/releases/download/v0.50.0/trivy_0.50.0_Linux-64bit.tar.gz
tar -xzf trivy_0.50.0_Linux-64bit.tar.gz
sudo mv trivy /usr/local/bin/

# Install Checkov
pip install checkov

# Install Gitleaks
# macOS
brew install gitleaks

# Linux
wget https://github.com/gitleaks/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
tar -xzf gitleaks_8.18.0_linux_x64.tar.gz
sudo mv gitleaks /usr/local/bin/
```

### Run Scans

```bash
# Trivy - Scan filesystem
trivy fs .

# Trivy - Scan Dockerfile
trivy config Dockerfile

# Checkov - Scan Dockerfile
checkov -f Dockerfile --framework docker

# Checkov - Scan directory
checkov -d . --framework docker

# Gitleaks - Scan repository
gitleaks detect --source . --verbose
```

## 🚨 Handling Security Findings

### Critical/High Severity Issues

1. **Review the finding** in GitHub Security tab or logs
2. **Assess the risk**:
   - Is it a false positive?
   - Is it in production code or tests?
   - What's the impact?
3. **Fix the issue**:
   - Update configurations
   - Remove hardcoded secrets
   - Apply security best practices
4. **Re-run scans** to verify fixes

### False Positives

If you have a false positive:

1. **Trivy**: Add to `.trivyignore` or adjust severity
2. **Checkov**: Use `--skip-check` flag or add to config
3. **Gitleaks**: Add pattern to `.gitleaksignore`

### Bypassing (Not Recommended)

Only bypass if absolutely necessary:
- Add `[skip security]` in PR description (not recommended)
- Use `continue-on-error: true` in workflow (already configured for pushes)

## 📈 Best Practices

1. **Fix Before Merge**: Always fix critical/high issues before merging PRs
2. **Review Regularly**: Check security tab weekly
3. **Keep Updated**: Update tools regularly for latest checks
4. **Document Exceptions**: If bypassing, document why in PR comments
5. **Monitor Trends**: Watch for recurring patterns in findings

## 🔗 Resources

- [Trivy Documentation](https://aquasecurity.github.io/trivy/)
- [Checkov Documentation](https://www.checkov.io/)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)
- [GitHub Security Features](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## ❓ FAQ

**Q: Why do scans fail on PRs but not on pushes?**
A: PRs block merges to prevent insecure code from reaching main. Push scans are informational to avoid blocking deployments.

**Q: Can I skip scans for documentation-only changes?**
A: No, but documentation changes rarely trigger security findings. If needed, use `[skip security]` (not recommended).

**Q: How do I fix a "secret detected" finding?**
A: 
1. Rotate the exposed secret immediately
2. Remove it from git history (use BFG Repo-Cleaner or git-filter-repo)
3. Add it to `.gitleaksignore` if it's a test/example token

**Q: Scan is too slow, can I optimize it?**
A: 
- Use `--compact` mode for Checkov
- Limit Gitleaks to recent commits (`--log-opts "--since=30.days"`)
- Cache dependencies in GitHub Actions

---

**Last Updated**: 2024
**Maintained by**: Development Team

