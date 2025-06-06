# Contributing to ESG Reporting

Thank you for considering contributing to the ESG Reporting project! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## How to Contribute

### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template when creating new issues
3. Provide clear reproduction steps
4. Include relevant environment information

### Submitting Changes

1. Fork the repository
2. Create a feature branch from `main`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Update documentation as needed
6. Submit a pull request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/ESGReporting.git
cd ESGReporting

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
make install
make dev-deps

# Run tests
make test
```

## Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write descriptive docstrings
- Maximum line length: 88 characters
- Use `black` for code formatting
- Use `isort` for import sorting

### Testing Requirements

- Write tests for all new functionality
- Maintain test coverage above 80%
- Use descriptive test names
- Mock external dependencies
- Include both unit and integration tests

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Include examples in docstrings
- Update API documentation

## Project Structure

```
ESGReporting/
├── src/esg_reporting/      # Main package
├── tests/                  # Test suite
├── infra/                  # Azure infrastructure
├── docs/                   # Documentation
└── scripts/                # Utility scripts
```

## Azure Development

When working with Azure resources:

1. Use managed identity for authentication
2. Follow Azure security best practices
3. Test with real Azure resources when possible
4. Update Bicep templates for infrastructure changes
5. Document any new Azure service dependencies

## Pull Request Process

1. **Create a clear PR title** following the format:
   - `feat: add new feature`
   - `fix: resolve issue with...`
   - `docs: update documentation`
   - `test: add tests for...`

2. **Fill out the PR template** with:
   - Description of changes
   - Testing performed
   - Documentation updates
   - Breaking changes (if any)

3. **Ensure all checks pass**:
   - All tests pass
   - Code coverage maintained
   - Linting passes
   - Security checks pass

4. **Request review** from maintainers

## Release Process

1. Version numbers follow [Semantic Versioning](https://semver.org/)
2. Update CHANGELOG.md with release notes
3. Tag releases in git
4. GitHub Actions handles automated deployment

## Getting Help

- Check the documentation first
- Search existing issues
- Ask questions in GitHub Discussions
- Join our community chat (if available)

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to make ESG reporting better for everyone!
