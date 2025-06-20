# Contributing to POP API

Thank you for your interest in contributing to the Point of Presence API! This document provides guidelines and information for contributors.

## Quick Start for Contributors

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pop.git
   cd pop
   ```
3. **Set up development environment** (see [Development Setup](#development-setup))
4. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
5. **Make your changes** following our [coding standards](#coding-standards)
6. **Test your changes** thoroughly
7. **Submit a pull request**

## 🛠️ Development Setup

### Prerequisites
- Python 3.9 or higher
- Docker and Docker Compose
- Git

### Local Development Environment

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # Development dependencies
   ```

3. **Configure environment**:
   ```bash
   cp example.env .env
   # Edit .env with your development settings
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Run the application**:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

### Development with Docker

```bash
# Start development environment
docker-compose up -d

# Access the container for development
docker exec -it pop-api bash

# Run tests inside container
docker exec -it pop-api pytest
```

## 📋 Coding Standards

### Python Code Style
- **Formatter**: [Black](https://black.readthedocs.io/) with 79 character line limit
- **Linter**: [Flake8](https://flake8.pycqa.org/)
- **Import sorting**: [isort](https://pycqa.github.io/isort/)

### Code Quality Requirements
- **Type hints**: Required for all function parameters and return values
- **Docstrings**: NumPy-style docstrings for all public functions and classes
- **Line length**: Maximum 79 characters (PEP 8 compliant)
- **Comments**: English only, clear and concise

### Example Function Structure
```python
def create_dataset(
    dataset_name: str, 
    owner_org: str, 
    description: Optional[str] = None
) -> str:
    """
    Create a new dataset in CKAN.

    Parameters
    ----------
    dataset_name : str
        The unique name for the dataset.
    owner_org : str
        The organization ID that will own the dataset.
    description : Optional[str], default=None
        Optional description for the dataset.

    Returns
    -------
    str
        The ID of the created dataset.

    Raises
    ------
    ValueError
        If dataset_name is invalid or already exists.
    HTTPException
        If CKAN API call fails.
    """
    # Implementation here
    return dataset_id
```

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_routes.py

# Run tests with verbose output
pytest -v
```

### Writing Tests
- **Test files**: Place in `tests/` directory with `test_*.py` naming
- **Coverage**: Aim for >80% code coverage for new features
- **Test types**: Include unit tests, integration tests, and API endpoint tests
- **Fixtures**: Use pytest fixtures for common test setup

### Test Structure Example
```python
import pytest
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_create_dataset_success():
    """Test successful dataset creation."""
    payload = {
        "dataset_name": "test_dataset",
        "dataset_title": "Test Dataset",
        "owner_org": "test_org"
    }
    response = client.post("/datasource", json=payload)
    assert response.status_code == 201
    assert "id" in response.json()

def test_create_dataset_invalid_input():
    """Test dataset creation with invalid input."""
    payload = {"invalid": "data"}
    response = client.post("/datasource", json=payload)
    assert response.status_code == 422
```

## 🔄 Pull Request Process

### Before Submitting
1. **Update tests** for any new functionality
2. **Run the full test suite** and ensure it passes
3. **Update documentation** if needed
4. **Run code formatting**:
   ```bash
   black api/ tests/
   flake8 api/ tests/
   ```

### Pull Request Requirements
- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Reference related issues** using `Fixes #issue_number`
- **Include screenshots** for UI changes
- **Test coverage** maintained or improved

### PR Template
```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented appropriately
- [ ] Documentation updated
- [ ] Tests added/updated
```

## 📁 Project Structure

Understanding the codebase organization:

```
pop/
├── api/
│   ├── config/          # Configuration management
│   │   ├── ckan_settings.py
│   │   ├── kafka_settings.py
│   │   └── keycloak_settings.py
│   ├── models/          # Pydantic data models
│   │   ├── *request_model.py
│   │   └── *response_model.py
│   ├── routes/          # API endpoints
│   │   ├── register_routes/
│   │   ├── search_routes/
│   │   ├── delete_routes/
│   │   └── update_routes/
│   ├── services/        # Business logic
│   ├── tasks/           # Background tasks
│   └── templates/       # HTML templates
├── tests/               # Test suite
├── static/              # Static web assets
└── docs/                # Additional documentation
```

## 🐛 Bug Reports

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Test with latest version** from main branch
3. **Gather relevant information** (logs, environment details)

### Bug Report Template
```markdown
**Bug Description**
Clear description of the bug.

**Steps to Reproduce**
1. Step 1
2. Step 2
3. Step 3

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Docker version: [if applicable]
- Browser: [if web-related]

**Additional Context**
Any other relevant information.
```

## 💡 Feature Requests

### Feature Request Template
```markdown
**Feature Description**
Clear description of the requested feature.

**Problem Statement**
What problem does this feature solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Any alternative solutions considered?

**Additional Context**
Any other relevant information.
```

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `question` - Further information requested
- `wontfix` - This will not be worked on

## 📚 Additional Resources

- **API Documentation**: http://localhost:8001/docs (when running locally)
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **CKAN API Documentation**: https://docs.ckan.org/en/latest/api/
- **Pydantic Documentation**: https://pydantic-docs.helpmanual.io/
- **Pytest Documentation**: https://docs.pytest.org/

## 🤝 Community Guidelines

- **Be respectful** and inclusive
- **Use clear communication** in issues and PRs
- **Help others** when you can
- **Follow the code of conduct**
- **Ask questions** if you're unsure about something

## 📧 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: Maintainers will provide feedback on PRs

---

Thank you for contributing to POP API! 🎉