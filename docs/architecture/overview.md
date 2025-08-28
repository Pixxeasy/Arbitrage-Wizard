# Architecture Overview

ArbitrageWizard follows a modern, scalable architecture designed for cryptocurrency arbitrage detection and management.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   Frontend      │◄───┤   Backend API   │◄───┤   Exchange      │
│   (React)       │    │   (FastAPI)     │    │   Integrations  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │                 │
                       │   Database      │
                       │   (MySQL)       │
                       │                 │
                       └─────────────────┘
```

## Frontend Architecture

**Technology Stack:**
- React 18 with TypeScript
- Chakra UI for components
- Redux Toolkit for state management
- Vite for build tooling

**Structure:**
- **Feature-based organization**: Code organized by business features (auth, arbitrage, config)
- **Shared components**: Reusable UI components and utilities
- **Service layer**: API integration with RTK Query

## Backend Architecture

**Technology Stack:**
- FastAPI for API framework
- SQLAlchemy for ORM
- Pydantic for data validation
- MySQL for database

**Layers:**
1. **API Layer** (`app/api/routes/`): HTTP endpoints and request/response handling
2. **Service Layer** (`app/services/`): Business logic and orchestration
3. **CRUD Layer** (`app/crud/`): Database operations
4. **Model Layer** (`app/models/`): Database models and schemas

**Key Principles:**
- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Injection**: Services injected via FastAPI dependencies
- **Configuration Management**: Centralized settings with Pydantic
- **Error Handling**: Structured exception handling

## Exchange Integration

**Supported Exchanges:**
- MEXC, Bybit, KuCoin, Binance, OKX, Bitget, HTX, XT, Poloniex, BitMart

**Integration Pattern:**
- **Base Exchange Class**: Common interface for all exchanges
- **CCXT Library**: Standardized exchange interactions
- **Rate Limiting**: Built-in protection against API limits
- **Error Handling**: Robust error recovery and retry logic

## Data Flow

1. **Scanner Service** continuously monitors exchange prices
2. **Arbitrage Detection** identifies profitable opportunities
3. **Database Storage** persists opportunities and user data
4. **API Endpoints** serve data to frontend
5. **Real-time Updates** keep UI synchronized

## Security Considerations

- **JWT Authentication**: Secure user session management
- **API Key Management**: Encrypted storage of exchange credentials
- **Rate Limiting**: Protection against abuse
- **CORS Configuration**: Controlled cross-origin access

## Scalability Design

- **Microservice Ready**: Services can be extracted to separate deployments
- **Database Optimization**: Indexed queries and connection pooling
- **Caching Strategy**: Redis integration ready for high-traffic scenarios
- **Load Balancing**: Stateless design supports horizontal scaling

## Monitoring and Observability

- **Structured Logging**: Comprehensive logging throughout the application
- **Health Checks**: Endpoint monitoring and service health
- **Error Tracking**: Exception monitoring and alerting
- **Performance Metrics**: Response time and throughput monitoring