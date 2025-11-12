#!/bin/bash

# PaperVerse Full Stack Startup Script
# Starts both backend (FastAPI) and frontend (Vite)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/hemal/backend"
FRONTEND_DIR="$SCRIPT_DIR/citemesh-ui"

echo "╔════════════════════════════════════════════╗"
echo "║   PaperVerse Full Stack Startup            ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check if .env exists in backend
if [ ! -f "$BACKEND_DIR/.env" ]; then
    echo "⚠️  Backend .env file not found!"
    echo "📝 Creating from .env.example..."
    if [ -f "$BACKEND_DIR/.env.example" ]; then
        cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env"
        echo "✓ Created .env file"
        echo ""
        echo "⚠️  IMPORTANT: Edit $BACKEND_DIR/.env and add your Gemini API key!"
        echo "   Get one at: https://makersuite.google.com/app/apikey"
        echo ""
        read -p "Press Enter after you've added your API key..." 
    else
        echo "❌ .env.example not found. Creating basic .env..."
        cat > "$BACKEND_DIR/.env" << 'EOF'
OPENALEX_BASE_URL=https://api.openalex.org
AI_PROVIDER=gemini
AI_MODEL=gemini-1.5-flash-latest
AI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/models
AI_API_KEYS=your_gemini_api_key_here
REQUEST_TIMEOUT_SECONDS=10.0
ENABLE_CACHE=true
CACHE_DIR=cache
PDF_CACHE_DIR=pdf_cache
PDF_DOWNLOAD_TIMEOUT_SECONDS=20.0
PDF_MAX_DOWNLOAD_MB=20.0
EOF
        echo "✓ Created basic .env file"
        echo "⚠️  Edit $BACKEND_DIR/.env and add your Gemini API key!"
        exit 1
    fi
fi

# Check Python dependencies
echo "🔍 Checking backend dependencies..."
cd "$BACKEND_DIR"

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

if [ ! -d "../../.venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../../.venv
fi

echo "📦 Activating virtual environment..."
source ../../.venv/bin/activate

echo "📦 Installing/updating Python dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check Node dependencies
echo ""
echo "🔍 Checking frontend dependencies..."
cd "$FRONTEND_DIR"

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install Node.js"
    exit 1
fi

if [ ! -d "node_modules" ]; then
    echo "📦 Installing npm dependencies..."
    npm install
fi

# Start backend in background
echo ""
echo "🚀 Starting backend server..."
cd "$BACKEND_DIR"
source ../../.venv/bin/activate

# Kill any existing uvicorn process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

uvicorn app:app --reload --host 0.0.0.0 --port 8000 > ../../backend.log 2>&1 &
BACKEND_PID=$!

echo "✓ Backend starting on http://127.0.0.1:8000 (PID: $BACKEND_PID)"
echo "  📋 Logs: $SCRIPT_DIR/backend.log"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
        echo "✓ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check backend.log"
        kill $BACKEND_PID 2>/dev/null || true
        exit 1
    fi
    sleep 1
done

# Start frontend in background
echo ""
echo "🚀 Starting frontend server..."
cd "$FRONTEND_DIR"

# Kill any existing vite process on port 5173/5174
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5174 | xargs kill -9 2>/dev/null || true

npm run dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✓ Frontend starting (PID: $FRONTEND_PID)"
echo "  📋 Logs: $SCRIPT_DIR/frontend.log"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:5173 > /dev/null 2>&1 || curl -s http://localhost:5174 > /dev/null 2>&1; then
        echo "✓ Frontend is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "╔════════════════════════════════════════════╗"
echo "║          🎉 PaperVerse is Running!         ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "🌐 Frontend:  http://localhost:5173 or http://localhost:5174"
echo "🔧 Backend:   http://127.0.0.1:8000"
echo "📚 API Docs:  http://127.0.0.1:8000/docs"
echo ""
echo "📊 Process IDs:"
echo "   Backend:  $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f $SCRIPT_DIR/backend.log"
echo "   Frontend: tail -f $SCRIPT_DIR/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 Test the integration:"
echo "   python3 test_openalex_integration.py"
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" INT TERM

echo "Press Ctrl+C to stop all services..."
wait
