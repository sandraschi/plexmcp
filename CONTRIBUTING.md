# Contributing to PlexMCP

Thank you for your interest in contributing to PlexMCP! We welcome contributions from the community and are grateful for your help in making this project better.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Development Guidelines](#development-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

## 🤝 Code of Conduct

This project adheres to a code of conduct to ensure a welcoming environment for all contributors. By participating, you agree to:

- Be respectful and inclusive
- Focus on constructive feedback
- Accept responsibility for mistakes
- Show empathy towards other contributors
- Help create a positive community

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- A Plex Media Server instance (for testing)
- Basic knowledge of MCP (Model Context Protocol)

### Quick Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/plex-mcp.git
cd plex-mcp

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest
```

## 🛠️ Development Setup

### Environment Configuration
Create a `.env` file for local development:
```bash
PLEX_URL=http://localhost:32400
PLEX_TOKEN=your_plex_token_here
PYTHONPATH=src
```

### Development Tools
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks for quality checks

### IDE Setup
We recommend using VS Code or Cursor with the following extensions:
- Python
- Pylance
- GitLens
- GitHub Pull Requests

## 💡 How to Contribute

### Types of Contributions
- **Bug fixes**: Fix issues in the codebase
- **Features**: Add new functionality
- **Documentation**: Improve docs and guides
- **Tests**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Security**: Address security concerns

### Finding Issues
- Check [GitHub Issues](https://github.com/sandra/plex-mcp/issues) for open tasks
- Look for issues labeled `good first issue` or `help wanted`
- Comment on issues you'd like to work on to avoid duplicate work

## 📝 Development Guidelines

### Code Style
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write descriptive variable and function names
- Keep functions small and focused on a single responsibility

### Commit Messages
Use conventional commit format:
```bash
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```bash
feat: add playlist analysis tool
fix: resolve authentication timeout issue
docs: update installation guide
test: add comprehensive API tests
```

### Branch Naming
- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `test/description`: Test-related changes

## 🧪 Testing

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/plex_mcp --cov-report=html

# Run specific test file
pytest tests/test_specific_feature.py

# Run tests in verbose mode
pytest -v
```

### Writing Tests
- Write tests for all new features
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (Plex API calls)
- Aim for >80% code coverage

### Test Structure
```python
import pytest
from plex_mcp.api.core import get_plex_status

class TestGetPlexStatus:
    def test_successful_status_retrieval(self, mock_plex_server):
        # Test successful case
        pass

    def test_server_unavailable(self, mock_plex_server):
        # Test error handling
        pass

    def test_invalid_token(self, mock_plex_server):
        # Test authentication failure
        pass
```

## 📚 Documentation

### Documentation Standards
- Use clear, concise language
- Include code examples where helpful
- Keep documentation up to date with code changes
- Use proper markdown formatting

### Documentation Files
- **README.md**: Project overview and quick start
- **docs/**: Detailed documentation
- **CHANGELOG.md**: Version history
- **API docs**: Auto-generated from docstrings

### Updating Documentation
1. Make your code changes
2. Update relevant documentation files
3. Test documentation builds (if applicable)
4. Ensure links and references are correct

## 🔄 Pull Request Process

### Before Submitting
1. **Update tests**: Ensure all tests pass
2. **Update documentation**: Keep docs current
3. **Code formatting**: Run `black` and `flake8`
4. **Type checking**: Run `mypy`
5. **Self-review**: Check your own code

### Creating a Pull Request
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Commit your changes**: `git commit -m "feat: add your feature"`
5. **Push to your fork**: `git push origin feature/your-feature-name`
6. **Create a Pull Request** on GitHub

### PR Template
Fill out the PR template with:
- Description of changes
- Type of change (bug fix, feature, etc.)
- Testing instructions
- Screenshots (if UI changes)
- Related issues

### Review Process
1. **Automated checks**: CI/CD pipeline runs
2. **Code review**: Maintainers review your code
3. **Feedback**: Address any requested changes
4. **Approval**: PR is approved and merged
5. **Deployment**: Changes are deployed automatically

## 🤝 Community

### Getting Help
- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Discord**: Real-time community support

### Communication Guidelines
- Be respectful and constructive
- Use clear, descriptive language
- Provide context for your questions
- Share solutions you've found

### Recognition
Contributors are recognized in:
- CHANGELOG.md for significant contributions
- GitHub release notes
- Project documentation

## 🎯 Quality Standards

### Code Quality Checklist
- [ ] All tests pass
- [ ] Code is properly typed
- [ ] No linting errors
- [ ] Documentation updated
- [ ] Commit messages follow conventions
- [ ] Security considerations addressed

### Review Criteria
- **Functionality**: Code works as intended
- **Code Quality**: Follows project standards
- **Testing**: Adequate test coverage
- **Documentation**: Clear and complete
- **Security**: No security vulnerabilities
- **Performance**: No performance regressions

## 🚀 Advanced Contributions

### Architecture Decisions
For significant changes, please:
- Open an issue first to discuss the change
- Provide rationale for the approach
- Consider backward compatibility
- Document breaking changes

### New Features
When adding new features:
- Follow the existing patterns
- Add comprehensive tests
- Update documentation
- Consider CLI interface changes
- Update configuration examples

### Performance Improvements
For performance-related changes:
- Include benchmarks before/after
- Consider memory usage implications
- Test with realistic data sizes
- Document performance characteristics

## 📞 Support

### For Contributors
- **Questions**: GitHub Discussions
- **Bugs**: GitHub Issues
- **Security**: security@plexmcp.dev
- **General**: hello@plexmcp.dev

### For Maintainers
- **Code Review**: Focus on functionality and quality
- **Mentorship**: Help new contributors learn
- **Community**: Foster positive interactions
- **Quality**: Maintain high standards

---

## 🙏 Thank You

Your contributions help make PlexMCP better for everyone. We appreciate your time and effort in helping improve this project!

**Happy contributing!** 🎉
