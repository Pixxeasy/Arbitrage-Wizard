# ArbitrageWizard

A comprehensive cryptocurrency arbitrage trading platform that detects and analyzes price differences across multiple exchanges.

## Architecture

This is a monorepo containing:

- **Frontend** (`apps/frontend`): React TypeScript application with Chakra UI
- **Backend API** (`apps/backend-api`): FastAPI Python application
- **MEXC SDK** (`packages/mexc-sdk`): TypeScript SDK for MEXC exchange
- **Shared Types** (`packages/shared-types`): Common TypeScript interfaces
- **Shared Utils** (`packages/shared-utils`): Common utility functions

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- MySQL database
- Conda (recommended for backend isolation)

### Installation

```bash
# Install all dependencies
npm run install:all

# Or install individually
npm install                        # Frontend and shared packages
npm run install:backend            # Backend (conda environment)

# Update backend dependencies after changes to requirements.txt
npm run update:backend             # Update conda environment

# Then activate the conda environment for backend development
conda activate arbitrage-wizard-backend

# Configure environment variables
# Edit apps/backend-api/.env with your database credentials
```

### Development

#### Quick Start - All Services
```bash
# Windows (default)
npm run dev

# Windows (PowerShell with cleanup)
npm run dev:powershell

# Unix/Linux/macOS/WSL
npm run dev:unix
```

#### Individual Services
```bash
# Start frontend development server
npm run dev:frontend

# Start backend development server
npm run dev:backend

# Run tests
npm run test:backend
npm run test:frontend
```

#### Development URLs
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Project Structure

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

## Features

- Real-time arbitrage opportunity detection
- Multi-exchange support (10+ exchanges)
- User authentication and configuration
- Historical arbitrage tracking
- Risk management and rate limiting

## Supported Exchanges

- MEXC
- Bybit
- KuCoin
- Binance
- OKX
- Bitget
- And more...

## Development Environment

This project supports development on **Windows, macOS, and Linux**:

- **Windows**: Uses batch scripts (`dev.bat`) or PowerShell (`dev.ps1`)
- **Unix/Linux/macOS**: Uses bash scripts (`dev.sh`)
- **WSL/Git Bash**: Can use either Windows or Unix scripts

The development scripts automatically start all required services and provide live reloading.

## Code Standards

- **Frontend**: Use absolute imports (`@/features/auth`, `@/shared/components`)
- **Backend**: Implement business logic in service layer
- **TypeScript**: Strict mode enabled throughout
- **Architecture**: Follow feature-based organization (frontend) and service-oriented design (backend)

## Key Documentation

- [Architecture Overview](docs/architecture/overview.md) - System design and patterns
- [Getting Started Guide](docs/development/getting-started.md) - Detailed setup instructions  
- [Contributing Guidelines](CONTRIBUTING.md) - Development workflow and standards
- [API Documentation](docs/api/) - FastAPI endpoints and schemas

## Testing

```bash
# Frontend tests
npm run test:frontend

# Backend tests  
cd apps/backend-api && python -m pytest

# Linting and type checking
npm run lint:frontend
npm run type-check:frontend
```

## Deployment

- **Frontend**: Builds to `apps/frontend/dist/` for static hosting
- **Backend**: Runs with `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **Environment**: Configure via `.env` file (see `.env.example`)
- **Database**: Requires MySQL with connection details in environment

## Contributing

Please read our contributing guidelines in `CONTRIBUTING.md`.

## License

This project is private and proprietary.