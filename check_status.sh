#!/bin/bash

# CiteMesh Status Check Script
# Run this anytime to check system status

echo "╔════════════════════════════════════════════╗"
echo "║     CiteMesh System Status Check          ║"
echo "╚════════════════════════════════════════════╝"
echo ""

# Check Backend
echo "🔧 Backend (FastAPI + OpenAlex):"
if curl -s http://127.0.0.1:8000/docs > /dev/null 2>&1; then
    echo "   ✅ Running on http://127.0.0.1:8000"
    echo "   📚 API Docs: http://127.0.0.1:8000/docs"
else
    echo "   ❌ Not running"
    echo "   💡 Start: cd hemal/backend && uvicorn app:app --reload"
fi
echo ""

# Check Frontend
echo "⚛️  Frontend (React + Vite):"
if curl -s http://localhost:5174 > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:5174"
elif curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Running on http://localhost:5173"
else
    echo "   ❌ Not running"
    echo "   💡 Start: cd citemesh-ui && npm run dev"
fi
echo ""

# Check API Keys
echo "🔑 API Keys:"
cd "$(dirname "$0")/hemal/backend" 2>/dev/null
if [ -f .env ]; then
    KEY_COUNT=$(grep "AI_API_KEYS=" .env | grep -o "AIza" | wc -l | tr -d ' ')
    echo "   ✅ $KEY_COUNT keys configured"
    echo "   💡 Validate: python3 ../../validate_api_keys.py"
else
    echo "   ❌ .env file not found"
fi
cd - > /dev/null 2>&1
echo ""

# Integration Test
echo "🧪 Quick Integration Test:"
echo "   Run: python3 quick_test.py"
echo ""

# Usage Instructions
echo "📖 Usage:"
echo "   Frontend:  Open http://localhost:5174"
echo "   Search:    Scroll to 'Ask CiteMesh Anything'"
echo "   Query:     Try 'Find quantum computing papers from 2024'"
echo ""

echo "╔════════════════════════════════════════════╗"
echo "║         Ready to Query OpenAlex!           ║"
echo "╚════════════════════════════════════════════╝"
