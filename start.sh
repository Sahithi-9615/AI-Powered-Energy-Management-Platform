#!/bin/bash

# Smart Energy Platform - Startup Script

echo "🔋 Smart Energy Analysis Platform"
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/Update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if model exists
if [ ! -f "model.pkl" ]; then
    echo "⚠️  Warning: model.pkl not found!"
    echo "   Please ensure your trained model is in the project directory."
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env with your API keys."
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting Flask server..."
echo "   Access the application at: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the Flask app
python app.py
