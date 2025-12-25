# Contributing to Workspace Security Suite

Thank you for your interest in contributing! We welcome community contributions to help improve enterprise Google Workspace security.

## Code of Conduct

- Be respectful and inclusive
- Focus on the code, not the person
- Help others learn and grow
- Report security issues privately

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/workspace-security-suite.git
   ```
3. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Cloud Project with Workspace APIs enabled

### Install Dependencies

**Backend/Scripts:**
```bash
cd scripts
pip install -r requirements.txt
```

**Frontend Dashboard:**
```bash
cd src/workspace-sentinel
npm install
```

## Making Changes

1. **Create comprehensive commit messages:**
   ```
   feat: Add MFA enforcement controls
   
   - Implement MFA status checking
   - Add enforcement UI components
   - Include validation logic
   ```

2. **Test your changes thoroughly**
3. **Update documentation** if applicable
4. **Follow code style guidelines:**
   - Python: PEP 8
   - JavaScript: Prettier + ESLint

## Submitting a Pull Request

1. **Push to your fork**
2. **Create a Pull Request** with:
   - Clear title and description
   - Reference to related issues (if any)
   - Screenshots for UI changes
   - Test coverage

3. **Address review feedback** promptly

## Areas for Contribution

- 🔒 Security enhancements
- 🧪 Test coverage improvements
- 📚 Documentation improvements
- 🐛 Bug fixes
- ✨ New features (discuss first in Issues)
- 🎨 UI/UX improvements
- 🌐 Translations

## Reporting Issues

- **Security issues**: Email security@workspace-security-suite.dev (do NOT open public issues)
- **Bugs**: Use GitHub Issues with detailed reproduction steps
- **Feature requests**: Use GitHub Discussions

## Questions?

Open a GitHub Discussion or check our documentation in `/docs`.

Thank you for contributing! 🚀
