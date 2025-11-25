# Contributing to ChainPilot

Thank you for your interest in contributing to ChainPilot! This document provides guidelines and instructions for contributing.

---

## 🤝 How to Contribute

### Ways to Contribute

- **Report Bugs**: Help us identify and fix issues
- **Suggest Features**: Share ideas for new functionality
- **Improve Documentation**: Fix typos, add examples, clarify explanations
- **Write Code**: Fix bugs, implement features, optimize performance
- **Write Tests**: Increase test coverage
- **Review Code**: Provide feedback on pull requests

---

## 🐛 Reporting Bugs

### Before Submitting

1. Check if the bug has already been reported
2. Ensure you're using the latest version
3. Test in sandbox mode to isolate the issue
4. Collect relevant information (logs, error messages, steps to reproduce)

### Bug Report Template

```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Start server with `python3 run.py --sandbox`
2. Send request to `POST /api/v1/wallet/create`
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., macOS 13.0]
- Python version: [e.g., 3.13.0]
- ChainPilot version: [e.g., 1.0.0]
- Network: [e.g., Sepolia testnet]

**Logs**
```
Paste relevant logs here
```

**Additional Context**
Any other information about the problem.
```

---

## 💡 Suggesting Features

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Why would this feature be useful? Who would benefit?

**Proposed Solution**
How do you envision this working?

**Alternatives Considered**
What other approaches did you consider?

**Additional Context**
Screenshots, mockups, or examples from other projects.
```

---

## 🔧 Development Setup

### Prerequisites

- Python 3.13+
- Git
- Virtual environment tool
- Text editor or IDE

### Setup Steps

1. **Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/Chain-Pilot.git
cd Chain-Pilot
```

2. **Create Virtual Environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Run Tests**
```bash
python3 tests/test_all_comprehensive.py
```

5. **Start Server**
```bash
python3 run.py --sandbox
```

---

## 📝 Code Style

### Python

Follow PEP 8 with these specifics:

- **Line length**: 100 characters max
- **Indentation**: 4 spaces
- **Imports**: Grouped (standard library, third-party, local)
- **Docstrings**: Google style
- **Type hints**: Required for all functions

**Example**:
```python
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


async def process_transaction(
    transaction: Dict[str, Any],
    validate: bool = True
) -> Dict[str, Any]:
    """
    Process a cryptocurrency transaction.
    
    Args:
        transaction: Transaction details including to/from addresses
        validate: Whether to validate before processing
        
    Returns:
        Processed transaction result with status and hash
        
    Raises:
        ValueError: If transaction validation fails
    """
    if validate:
        _validate_transaction(transaction)
    
    # Process transaction
    logger.info(f"Processing transaction: {transaction}")
    return {"status": "success"}
```

### JavaScript

- **Style**: ES6+
- **Indentation**: 4 spaces
- **Semicolons**: Yes
- **Quotes**: Single quotes for strings
- **Functions**: async/await for async operations

**Example**:
```javascript
async function loadTransactions() {
    try {
        const response = await fetch(`${API_BASE}/audit/transactions`);
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Failed to load transactions:', error);
        showNotification('Error loading transactions', 'error');
    }
}
```

### Formatting Tools

```bash
# Python
black src/
flake8 src/

# JavaScript
prettier --write src/dashboard/static/*.js
```

---

## ✅ Testing

### Running Tests

```bash
# All comprehensive tests
python3 tests/test_all_comprehensive.py

# Specific test file
python3 tests/test_dashboard_real_data.py

# Phase-specific tests
python3 tests/phase_tests/test_phase6_security.py
```

### Writing Tests

- **Location**: `tests/` directory
- **Naming**: `test_*.py`
- **Coverage**: Aim for 100% code coverage
- **Independence**: Tests should not depend on each other
- **Cleanup**: Clean up test data after execution

**Example**:
```python
def test_wallet_creation():
    """Test that wallet creation works correctly"""
    # Arrange
    wallet_name = f"test_wallet_{int(time.time())}"
    
    # Act
    response = requests.post(
        f"{BASE_URL}/wallet/create",
        json={"wallet_name": wallet_name}
    )
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "address" in data
    assert data["wallet_name"] == wallet_name
    
    # Cleanup (if needed)
    # delete_test_wallet(wallet_name)
```

---

## 📤 Pull Request Process

### Before Submitting

1. **Update your fork**
```bash
git remote add upstream https://github.com/ORIGINAL/Chain-Pilot.git
git fetch upstream
git merge upstream/main
```

2. **Create a branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make changes**
- Write code
- Add tests
- Update documentation

4. **Test thoroughly**
```bash
python3 tests/test_all_comprehensive.py
```

5. **Commit changes**
```bash
git add .
git commit -m "feat: add new feature"
```

### Commit Message Format

Use conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(api): add endpoint for batch wallet creation

Add new POST /api/v1/wallets/batch endpoint that allows
creating multiple wallets in a single request.

Closes #123
```

```
fix(rules): correct daily spending limit calculation

Daily spending was incorrectly resetting at midnight local
time instead of UTC. Fixed to use UTC timezone.

Fixes #456
```

### Pull Request Template

When creating a PR, include:

```markdown
**Description**
Brief description of changes.

**Type of Change**
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

**Changes Made**
- Added X feature
- Fixed Y bug
- Updated Z documentation

**Testing**
- [ ] All existing tests pass
- [ ] Added new tests for new functionality
- [ ] Tested manually in sandbox mode

**Checklist**
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Added tests with good coverage

**Related Issues**
Closes #123
```

---

## 🎯 Areas for Contribution

### High Priority

- **Performance Optimization**: Optimize database queries, API response times
- **Test Coverage**: Add edge case tests, integration tests
- **Documentation**: Add more examples, improve clarity
- **Error Handling**: Better error messages, recovery strategies

### Medium Priority

- **New Features**: Multi-sig wallets, hardware wallet support
- **UI Improvements**: Dashboard enhancements, mobile responsiveness
- **Monitoring**: Add metrics, logging improvements
- **Security**: Security audits, penetration testing

### Low Priority

- **Code Refactoring**: Simplify complex functions
- **Type Hints**: Add type hints to legacy code
- **Comments**: Improve code documentation
- **Examples**: Add more usage examples

---

## 📚 Documentation

### Updating Documentation

Documentation lives in `docs/` directory:

- **API docs**: `docs/API.md`
- **Guides**: `docs/guides/`
- **Technical**: `docs/technical/`
- **Features**: `docs/phases/`

**When to update**:
- Adding new API endpoint → Update `docs/API.md`
- Adding new feature → Create/update guide
- Changing behavior → Update relevant docs
- Fixing bugs → Update if behavior documented

---

## 🔒 Security

### Reporting Security Issues

**DO NOT** open a public issue for security vulnerabilities.

Instead, email: security@chainpilot.dev

Include:
- Description of vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We'll respond within 48 hours.

### Security Best Practices

- Never commit private keys or secrets
- Use environment variables for sensitive config
- Validate all inputs
- Sanitize all outputs
- Follow principle of least privilege
- Keep dependencies updated

---

## 📞 Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Email**: support@chainpilot.dev
- **Discord**: [Join our community](https://discord.gg/chainpilot) (coming soon)

### Before Asking

1. Check existing issues and discussions
2. Read the documentation
3. Search for similar questions
4. Try to reproduce in sandbox mode
5. Gather relevant information (logs, versions, etc.)

---

## 🎓 Learning Resources

### For New Contributors

- **FastAPI**: https://fastapi.tiangolo.com/
- **Web3.py**: https://web3py.readthedocs.io/
- **Ethereum**: https://ethereum.org/developers
- **Python Async**: https://docs.python.org/3/library/asyncio.html

### For ChainPilot

- Read [How It Works](docs/technical/HOW_IT_WORKS.md)
- Study [API Documentation](docs/API.md)
- Review test files in `tests/`
- Check [Security Documentation](docs/phases/PHASE6_SECURITY.md)

---

## 🏆 Recognition

Contributors are recognized in:

- **CONTRIBUTORS.md**: All contributors listed
- **Release Notes**: Significant contributions mentioned
- **README.md**: Major contributors highlighted

We appreciate all contributions, big and small!

---

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behavior**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community

**Unacceptable behavior**:
- Trolling, insulting comments, personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct inappropriate in a professional setting

### Enforcement

Report violations to: conduct@chainpilot.dev

Maintainers will review and take appropriate action.

---

## 📝 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

## 🙏 Thank You!

Thank you for contributing to ChainPilot! Your efforts help make this project better for everyone.

**Questions?** Open an issue or contact us at support@chainpilot.dev

---

**Last Updated**: November 24, 2025  
**Version**: 1.0.0

