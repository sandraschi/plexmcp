# Development Guide

This guide is for developers who want to contribute to Plex MCP or extend its functionality.

## Getting Started

### Prerequisites

- Python 3.8+
- Git
- Poetry (for dependency management)
- Plex Media Server (for testing)

### Setting Up the Development Environment

1. Fork and clone the repository:
   ```powershell
   git clone https://github.com/yourusername/plexmcp.git
   cd plexmcp
   ```

2. Install dependencies:
   ```powershell
   # Install Poetry if you don't have it
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
   
   # Install project dependencies
   poetry install
   
   # Activate the virtual environment
   poetry shell
   ```

3. Set up pre-commit hooks:
   ```powershell
   pre-commit install
   ```

## Project Structure

```
plexmcp/
├── src/                    # Source code
│   └── plex_mcp/          # Main package
│       ├── api/           # API endpoints
│       ├── models/        # Data models
│       ├── services/      # Business logic
│       ├── utils/         # Utility functions
│       ├── __init__.py
│       └── server.py      # Main application
├── tests/                 # Tests
├── .github/              # GitHub workflows
├── docs/                 # Documentation
├── pyproject.toml        # Project metadata
└── README.md             # Project README
```

## Adding New Features

1. Create a new branch:
   ```powershell
   git checkout -b feature/your-feature-name
   ```

2. Implement your changes following the code style:
   - Use type hints
   - Add docstrings
   - Write tests
   - Update documentation

3. Run tests and linting:
   ```powershell
   # Run tests
   pytest
   
   # Run linter
   flake8 src tests
   
   # Run type checking
   mypy src
   ```

4. Commit your changes with a descriptive message:
   ```powershell
   git commit -m "feat: add new feature"
   ```

5. Push and create a pull request

## Testing

### Running Tests

```powershell
# Run all tests
pytest

# Run a specific test file
pytest tests/test_plex_service.py

# Run tests with coverage
pytest --cov=src/plex_mcp --cov-report=term-missing
```

### Writing Tests

- Place tests in the `tests/` directory
- Follow the naming convention `test_*.py`
- Use fixtures for common test data
- Mock external dependencies

Example test:

```python
def test_play_media(mock_plex_server):
    """Test playing media on a client."""
    client = PlexMCPClient()
    result = client.play_media("Living Room TV", "12345")
    assert result.status == "success"
```

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters

## Documentation

### Building Documentation

Documentation is written in Markdown and built with MkDocs:

```powershell
# Install documentation dependencies
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

### Adding Documentation

- Add new Markdown files to the `docs/` directory
- Update `mkdocs.yml` to include new pages
- Use Google-style docstrings for Python code

## Releasing a New Version

1. Update the version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Commit the changes:
   ```powershell
   git commit -m "chore: release v1.0.0"
   ```
4. Create a tag:
   ```powershell
   git tag -a v1.0.0 -m "Version 1.0.0"
   ```
5. Push the tag:
   ```powershell
   git push origin v1.0.0
   ```
6. GitHub Actions will automatically build and publish the package

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
