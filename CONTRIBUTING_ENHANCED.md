# Contributing to Workspace Security Suite

## Welcome!

Thank you for your interest in contributing to the Workspace Security Suite. This document provides guidelines and instructions for contributing to our project.

## Getting Started

### Prerequisites
- Python 3.8+
- Git and GitHub account
- Docker and Docker Compose (optional, for testing)
- Virtual environment tool (venv or conda)

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/romanchaa997/workspace-security-suite.git
cd workspace-security-suite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install

# Run tests
make test
```

## Development Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Follow PEP 8 style guidelines
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Testing
```bash
make test          # Run all tests
make lint          # Run linting checks
make format        # Auto-format code
```

### 4. Commit and Push
```bash
git add .
git commit -m "Descriptive commit message"
git push origin feature/your-feature-name
```

### 5. Submit Pull Request
- Create a PR with clear description of changes
- Link to related issues
- Ensure CI/CD pipeline passes
- Request review from maintainers

## Contribution Types

### Bug Reports
- Use GitHub Issues with clear reproduction steps
- Include environment details and error messages
- Attach relevant logs or screenshots

### Feature Requests
- Describe the use case and expected behavior
- Provide implementation suggestions if possible
- Link to related issues

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update API documentation

### Code
- Follow existing code patterns
- Add comprehensive tests
- Maintain backward compatibility when possible

## Code Style

### Python
- Follow PEP 8 guidelines
- Use type hints for better code clarity
- Maximum line length: 100 characters
- Use docstrings for all functions and classes

### Commit Messages
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore
Scope: component or module affected
Subject: concise description (50 chars max)

## Testing Requirements

- Unit test coverage: minimum 80%
- Integration tests for critical workflows
- End-to-end tests for user scenarios
- Security tests for sensitive operations

## Pull Request Process

1. Update documentation and README
2. Add tests for new features
3. Ensure CI pipeline passes
4. Request review from 2+ maintainers
5. Squash commits before merge

## Review Process

Maintainers will review your PR within 3-5 business days. We may request changes or improvements. Please:
- Respond to feedback promptly
- Be open to suggestions
- Ask for clarification if needed
- Maintain professional tone

## Community

- Read our Code of Conduct
- Follow the community standards
- Report issues responsibly
- Respect all contributors

## Resources

- [Architecture Documentation](./ARCHITECTURE.md)
- [API Documentation](./docs/API.md)
- [Security Guidelines](./docs/SECURITY.md)
- [Deployment Guide](./DEPLOYMENT.md)

## Questions?

- Open a discussion in GitHub Discussions
- Email: contribute@workspace-security.dev
- Check existing issues and documentation

Thank you for contributing!
