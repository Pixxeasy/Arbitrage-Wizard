# Contributing to ArbitrageWizard

Thank you for your interest in contributing to ArbitrageWizard! This guide will help you get started.

## Development Setup

Please see the [Getting Started Guide](docs/development/getting-started.md) for detailed setup instructions.

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style and patterns
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Frontend
   npm run lint:frontend
   npm run type-check:frontend
   npm run build:frontend
   
   # Backend
   cd apps/backend-api
   python -m pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Style Guidelines

### Frontend (TypeScript/React)
- Use TypeScript strict mode
- Follow React hooks best practices
- Use Chakra UI components where possible
- Organize code by features, not file types
- Use absolute imports (`@/features/auth`)

### Backend (Python/FastAPI)
- Follow PEP 8 style guidelines
- Use type hints for all functions
- Separate business logic into services
- Write comprehensive docstrings
- Use Pydantic for data validation

### General
- Write clear, descriptive commit messages
- Keep pull requests focused and small
- Add comments for complex business logic
- Update tests when changing functionality

## Project Structure

```
arbitrage-wizard/
├── apps/
│   ├── frontend/          # React TypeScript app
│   └── backend-api/       # FastAPI Python app
├── packages/
│   ├── mexc-sdk/          # MEXC exchange SDK
│   ├── shared-types/      # Shared TypeScript types
│   └── shared-utils/      # Shared utilities
├── docs/                  # Documentation
└── tools/                 # Build tools and scripts
```

## Pull Request Guidelines

- Provide a clear description of the changes
- Link any related issues
- Ensure all tests pass
- Request review from maintainers
- Be responsive to feedback

## Issue Reporting

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Node.js/Python version)
- Any error messages or logs

## Questions?

Feel free to open an issue for questions or reach out to the maintainers.

Thank you for contributing! 🚀