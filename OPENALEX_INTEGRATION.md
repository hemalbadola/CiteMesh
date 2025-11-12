# PaperVerse OpenAlex Integration Guide

## 🎯 Overview

This guide helps you test and verify the complete integration between:
- **OpenAlex API** (scholarly data source)
- **FastAPI Backend** (query translation + data fetching)
- **React Frontend** (user interface)

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

## 🚀 Quick Start

### 1. Set Up Backend Environment

```bash
cd hemal/backend
cp .env.example .env
# Edit .env and add your Gemini API key to AI_API_KEYS
```

### 2. Install Dependencies

```bash
# Backend
cd hemal/backend
pip install -r requirements.txt

# Frontend (if not done)
cd ../../citemesh-ui
npm install
```

### 3. Option A: Start Everything Automatically

```bash
# From project root
chmod +x start_paperverse.sh
./start_paperverse.sh
```

This will:
- ✅ Check dependencies
- ✅ Start backend on http://127.0.0.1:8000
- ✅ Start frontend on http://localhost:5173/5174
- ✅ Show logs and process IDs

### 3. Option B: Start Services Manually

**Terminal 1 - Backend:**
```bash
cd hemal/backend
source ../../.venv/bin/activate  # if using venv
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd citemesh-ui
npm run dev
```

## 🧪 Run Integration Tests

```bash
# From project root
python3 test_openalex_integration.py
```

This test suite will:
1. ✅ Test direct OpenAlex API connection
2. ✅ Check if backend is running
3. ✅ Test backend /search endpoint with sample queries
4. ✅ Verify frontend configuration
5. 📊 Generate a comprehensive report

## 🔍 Manual Testing Steps

### 1. Test Backend API Directly

Visit http://127.0.0.1:8000/docs for interactive API documentation.

**Sample Request:**
```bash
curl -X POST "http://127.0.0.1:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find the most cited machine learning papers from 2023",
    "per_page": 5,
    "page": 1
  }'
```

### 2. Test Frontend Integration

1. Open http://localhost:5173 or http://localhost:5174
2. Scroll to the "Ask PaperVerse Anything" section
3. Try these sample queries:
   - "Find the most cited quantum computing papers from 2023"
   - "Show me recent reinforcement learning papers with open access"
   - "List papers about climate change from MIT"

### 3. Verify Connection Status

The frontend will automatically test the backend connection on load:
- ✅ Green: Backend connected
- ❌ Red: Cannot reach backend (check if it's running)

## 📊 Architecture

```
┌─────────────┐      Natural      ┌──────────────┐      OpenAlex     ┌──────────────┐
│   React     │  Language Query   │   FastAPI    │   API Request     │   OpenAlex   │
│  Frontend   │ ──────────────>   │   Backend    │ ───────────────>  │     API      │
│             │                    │              │                   │              │
│ localhost:  │  <───────────────  │ :8000        │  <──────────────  │  api.       │
│  5173/5174  │   JSON Results    │              │   JSON Response   │  openalex.org│
└─────────────┘                    └──────────────┘                   └──────────────┘
                                          │
                                          │ (Gemini API for
                                          ▼  query translation)
                                   ┌──────────────┐
                                   │   Google     │
                                   │   Gemini     │
                                   └──────────────┘
```

## 🔑 Key Endpoints

### Backend

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/docs` | GET | Interactive API documentation |
| `/search` | POST | Translate query + fetch from OpenAlex |
| `/pdf` | GET | Proxy and cache Open Access PDFs |

### Frontend

| Route | Description |
|-------|-------------|
| `#section-1` | Hero section |
| `#section-console` | Live search interface |
| Query form | Natural language research questions |

## 🐛 Troubleshooting

### Backend won't start

**Error: "AI_API_KEYS environment variable is not configured"**
- Solution: Add your Gemini API key to `hemal/backend/.env`

**Error: "Port 8000 is already in use"**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
```

### Frontend can't reach backend

**Status: "Cannot reach backend"**
1. Verify backend is running: `curl http://127.0.0.1:8000/docs`
2. Check CORS settings in `hemal/backend/app.py`
3. Ensure `window.PAPERVERSE_BACKEND` points to correct URL

### Query returns empty results

- Check OpenAlex API is accessible: `curl "https://api.openalex.org/works?search=AI&per_page=1"`
- Review backend logs for Gemini translation errors
- Try simpler queries first

## 📚 Sample Queries

**Basic Search:**
```
Find papers about neural networks
```

**Year Filter:**
```
Show me quantum computing research from 2023-2024
```

**Citation Sort:**
```
Most cited climate change papers since 2020
```

**Institution Filter:**
```
Deep learning papers from Stanford University
```

**Open Access:**
```
Find recent machine learning papers with open access PDFs
```

**Author Search:**
```
Papers by Andrew Ng about deep learning
```

**Collaboration:**
```
Joint research between MIT and Harvard in biomedical engineering
```

## 🔧 Configuration

### Backend Environment Variables

See `hemal/backend/.env`:
- `AI_API_KEYS`: Comma-separated Gemini API keys (required)
- `OPENALEX_BASE_URL`: OpenAlex endpoint (default: https://api.openalex.org)
- `ENABLE_CACHE`: Enable response caching (default: false)
- `REQUEST_TIMEOUT_SECONDS`: API timeout (default: 10.0)

### Frontend Configuration

Set in `citemesh-ui/index.html` or via environment:
```html
<script>
  window.PAPERVERSE_BACKEND = 'http://127.0.0.1:8000';
</script>
```

## 📈 Performance Tips

1. **Enable Caching**: Set `ENABLE_CACHE=true` in backend `.env`
2. **Use Multiple API Keys**: Add comma-separated keys to rotate requests
3. **Adjust Timeouts**: Increase for slow networks
4. **Limit Results**: Use smaller `per_page` values for faster responses

## 🎓 Learn More

- [OpenAlex API Docs](https://docs.openalex.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Gemini API Guide](https://ai.google.dev/docs)

## 🆘 Need Help?

1. Run the integration test: `python3 test_openalex_integration.py`
2. Check logs: `tail -f backend.log` or `tail -f frontend.log`
3. Review backend API docs at http://127.0.0.1:8000/docs
4. Verify OpenAlex directly: https://api.openalex.org/works?search=test
