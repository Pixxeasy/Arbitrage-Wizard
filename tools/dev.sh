#!/bin/bash

# ArbitrageWizard Development Script

echo "🚀 Starting ArbitrageWizard development environment..."

# Function to kill background processes
cleanup() {
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set up cleanup trap
trap cleanup SIGINT SIGTERM

# Start shared packages in watch mode
echo "📦 Starting shared packages in watch mode..."
cd packages/shared-types && npm run dev &
cd ../shared-utils && npm run dev &

# Start frontend development server
echo "🖥️  Starting frontend development server..."
cd ../../apps/frontend && npm run dev &

# Start backend development server
echo "🐍 Starting backend development server..."
cd ../backend-api && conda activate arbitrage-wizard-backend && python -m uvicorn app.main:app --reload --port 8000 &

echo "✅ All services started!"
echo "📱 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for any background job to finish
wait