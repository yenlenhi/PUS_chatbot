#!/bin/bash
# ============================================
# Railway Build Strategy Selector
# Choose between pre-download or lightweight build
# ============================================

# Check environment variable to decide strategy
BUILD_STRATEGY=${BUILD_STRATEGY:-"lightweight"}

echo "🔧 Railway Build Strategy: $BUILD_STRATEGY"

if [ "$BUILD_STRATEGY" = "pre-download" ]; then
    echo "📥 Using Dockerfile with pre-downloaded models"
    echo "   ⚠️  Warning: Build may take 5-10 minutes"
    echo "   ✅ Benefit: Faster startup, offline deployment"
    docker build -f Dockerfile -t uni-bot:latest .
    
elif [ "$BUILD_STRATEGY" = "lightweight" ]; then
    echo "🚀 Using lightweight Dockerfile (models download on first run)"
    echo "   ✅ Benefit: Faster build time"
    echo "   ⚠️  Warning: First startup will download models (~400MB)"
    docker build -f Dockerfile.lightweight -t uni-bot:latest .
    
else
    echo "❌ Invalid BUILD_STRATEGY: $BUILD_STRATEGY"
    echo "   Valid options: 'pre-download' or 'lightweight'"
    exit 1
fi

echo "✅ Docker build completed successfully"
