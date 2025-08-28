#!/bin/bash

# ArbitrageWizard Build Script

set -e

echo "🔧 Building ArbitrageWizard..."

# Build shared packages first
echo "📦 Building shared packages..."
cd packages/shared-types && npm run build
cd ../shared-utils && npm run build
cd ../mexc-sdk && npm run build

# Build frontend
echo "🖥️  Building frontend..."
cd ../../apps/frontend && npm run build

# Backend doesn't need a build step (Python)
echo "🐍 Backend ready (Python - no build needed)"

echo "✅ Build complete!"