# Getting Started

This guide will help you set up the ArbitrageWizard development environment.

## Prerequisites

- Node.js 18+ 
- Python 3.9+
- MySQL database
- Git

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd arbitrage-wizard
   ```

2. **Install dependencies**
   ```bash
   # Install all frontend dependencies and workspace setup
   npm install
   
   # Install backend dependencies
   cd apps/backend-api
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit environment variables
   nano .env
   ```

4. **Database Setup**
   ```bash
   # Create database
   mysql -u root -p -e "CREATE DATABASE arbitrage_wizard_dev;"
   
   # Run migrations (if available)
   cd apps/backend-api
   python -m app.db.migrate
   ```

## Development Workflow

### Frontend Development
```bash
# Start frontend development server
npm run dev:frontend

# Build frontend
npm run build:frontend

# Lint frontend code
npm run lint:frontend
```

### Backend Development  
```bash
# Start backend development server
npm run dev:backend

# Run tests
npm run test:backend

# Run linting (if configured)
python -m flake8 apps/backend-api
```

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
├── tools/                 # Build tools and scripts
└── README.md
```

## Key Features

- **Monorepo Architecture**: All code in a single repository with workspaces
- **Feature-based Frontend**: Components organized by business features
- **Service-oriented Backend**: Clear separation of concerns with services layer
- **Shared Packages**: Reusable types and utilities across applications

## Next Steps

- [Architecture Overview](../architecture/overview.md)
- [API Documentation](../api/README.md)
- [Contributing Guidelines](contributing.md)