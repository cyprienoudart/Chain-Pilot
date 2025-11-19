#!/bin/bash

# ChainPilot API Startup Script

echo "🚀 Starting ChainPilot API..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file from env_template.txt"
    echo ""
    echo "Quick setup:"
    echo "  1. cp env_template.txt .env"
    echo "  2. Edit .env and add your RPC URL"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "🔧 Virtual environment not activated"
    echo "   Attempting to activate..."
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    elif [ -f .venv/bin/activate ]; then
        source .venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment not found"
        echo "   Please create one: python3 -m venv venv"
        exit 1
    fi
fi

echo ""
echo "✅ Starting ChainPilot API on http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the API
python -m src.api.main

