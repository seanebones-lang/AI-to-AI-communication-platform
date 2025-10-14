#!/bin/bash

echo "🚀 Starting Enterprise AI Integration Demo"
echo "=========================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. Frontend will need manual setup."
    echo "   Install Node.js from https://nodejs.org/"
    FRONTEND_AVAILABLE=false
else
    FRONTEND_AVAILABLE=true
fi

# Backend setup
echo "📦 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from example..."
    cp .env.example .env
    echo "📝 Please edit backend/.env and add your ANTHROPIC_API_KEY"
    echo "   Get your API key from: https://console.anthropic.com/"
fi

# Start backend in background
echo "🔥 Starting backend server..."
python main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Frontend setup (if Node.js is available)
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "📦 Setting up frontend..."
    cd ../frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Start frontend
    echo "🔥 Starting frontend server..."
    npm run dev &
    FRONTEND_PID=$!
    
    echo ""
    echo "✅ Demo is running!"
    echo "   Backend:  http://localhost:8000"
    echo "   Frontend: http://localhost:5173"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    
    # Wait for user to stop
    wait $BACKEND_PID $FRONTEND_PID
else
    echo ""
    echo "✅ Backend is running!"
    echo "   Backend:  http://localhost:8000"
    echo ""
    echo "⚠️  Frontend not started - Node.js required"
    echo "   Install Node.js and run: cd frontend && npm install && npm run dev"
    echo ""
    echo "Press Ctrl+C to stop the backend server"
    
    # Wait for backend
    wait $BACKEND_PID
fi

# Cleanup
echo ""
echo "🛑 Shutting down demo..."
if [ "$FRONTEND_AVAILABLE" = true ]; then
    kill $FRONTEND_PID 2>/dev/null
fi
kill $BACKEND_PID 2>/dev/null
echo "✅ Demo stopped successfully!"
