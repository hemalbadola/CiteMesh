# CiteMesh Backend API Documentation

## Base URL
- Local: `http://localhost:8080`
- Production: `https://citemesh-api.ondigitalocean.app` (update with actual URL)

## Authentication
Currently uses placeholder `user_id=1`. Firebase Authentication integration coming soon.

---

## 📚 Collections API (`/api/collections`)

### Create Collection
```http
POST /api/collections/
Content-Type: application/json

{
  "name": "Machine Learning Papers",
  "description": "My ML research collection",
  "color": "#6366f1",
  "icon": "🤖",
  "is_public": false
}
```

### List Collections
```http
GET /api/collections/?skip=0&limit=50
```

### Get Collection
```http
GET /api/collections/{collection_id}
```

### Update Collection
```http
PUT /api/collections/{collection_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "description": "Updated description",
  "is_public": true
}
```

### Delete Collection
```http
DELETE /api/collections/{collection_id}
```

### Add Paper to Collection
```http
POST /api/collections/{collection_id}/papers
Content-Type: application/json

{
  "paper_id": "paper123",
  "paper_title": "Attention Is All You Need",
  "paper_authors": "Vaswani et al.",
  "paper_year": 2017,
  "note": "Transformer architecture paper"
}
```

### List Papers in Collection
```http
GET /api/collections/{collection_id}/papers
```

### Remove Paper from Collection
```http
DELETE /api/collections/{collection_id}/papers/{paper_id}
```

### Collection Statistics
```http
GET /api/collections/stats/summary
```

---

## 🔗 Citations API (`/api/citations`)

### Add Citation Link
```http
POST /api/citations/
Content-Type: application/json

{
  "source_paper_id": "paper1",
  "target_paper_id": "paper2",
  "note": "Paper2 builds on Paper1's methodology"
}
```

### List Citation Links
```http
GET /api/citations/?skip=0&limit=100
```

### Get Network Graph
```http
GET /api/citations/network?user_id=1
```

Response:
```json
{
  "nodes": [
    {
      "id": "paper1",
      "label": "Paper Title",
      "citation_count": 5,
      "size": 15,
      "color": "#ef4444"
    }
  ],
  "edges": [
    {
      "source": "paper1",
      "target": "paper2",
      "weight": 1
    }
  ]
}
```

### Delete Citation Link
```http
DELETE /api/citations/{link_id}
```

### Citation Statistics
```http
GET /api/citations/stats
```

### Get Related Papers
```http
GET /api/citations/paper/{paper_id}/related?limit=10
```

---

## 🔍 Search API (`/api/search`)

### Search Papers
```http
POST /api/search/search
Content-Type: application/json

{
  "query": "machine learning transformers",
  "filters": {
    "year_from": 2017,
    "year_to": 2024,
    "min_citations": 100,
    "open_access": true,
    "sort_by": "cited_by_count"
  },
  "page": 1,
  "per_page": 10,
  "use_ai_enhancement": true
}
```

Response:
```json
{
  "query": "machine learning transformers",
  "enhanced_query": "neural network transformer architectures attention mechanisms deep learning",
  "results": [
    {
      "id": "https://openalex.org/W...",
      "title": "Attention Is All You Need",
      "authors": [
        {
          "name": "Ashish Vaswani",
          "institution": "Google Brain"
        }
      ],
      "publication_year": 2017,
      "cited_by_count": 50000,
      "doi": "10.48550/arXiv.1706.03762",
      "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
      "abstract": "...",
      "concepts": [
        {
          "id": "C41008148",
          "name": "Deep learning",
          "score": 0.95
        }
      ],
      "open_access": true
    }
  ],
  "total_results": 1234,
  "page": 1,
  "per_page": 10,
  "total_pages": 124,
  "search_time_ms": 450
}
```

### Get Query Suggestions
```http
GET /api/search/suggest?query=machine learning
```

Response:
```json
{
  "original_query": "machine learning",
  "suggestions": [
    "machine learning recent advances",
    "machine learning systematic review",
    "machine learning applications"
  ],
  "enhanced_query": "machine learning algorithms deep neural networks artificial intelligence"
}
```

### Get Trending Topics
```http
GET /api/search/trending?period=week&limit=10
```

### Search Statistics
```http
GET /api/search/stats
```

---

## 💬 Chat API (`/api/chat`)

### Create Chat Session
```http
POST /api/chat/sessions
Content-Type: application/json

{
  "title": "Research Discussion",
  "model": "gemini",
  "system_prompt": "You are an expert AI research assistant."
}
```

### List Chat Sessions
```http
GET /api/chat/sessions?limit=50
```

### Get Session with Messages
```http
GET /api/chat/sessions/{session_id}
```

Response:
```json
{
  "id": 1,
  "user_id": 1,
  "title": "Research Discussion",
  "model": "gemini",
  "message_count": 5,
  "last_message_at": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:00:00",
  "updated_at": "2024-01-15T10:30:00",
  "messages": [
    {
      "id": 1,
      "session_id": 1,
      "role": "user",
      "content": "What is a transformer?",
      "paper_references": null,
      "created_at": "2024-01-15T10:00:00"
    },
    {
      "id": 2,
      "session_id": 1,
      "role": "assistant",
      "content": "A transformer is a deep learning architecture...",
      "paper_references": null,
      "created_at": "2024-01-15T10:00:30"
    }
  ]
}
```

### Update Session
```http
PUT /api/chat/sessions/{session_id}
Content-Type: application/json

{
  "title": "Updated Title",
  "system_prompt": "New system prompt"
}
```

### Delete Session
```http
DELETE /api/chat/sessions/{session_id}
```

### Send Message
```http
POST /api/chat/sessions/{session_id}/messages
Content-Type: application/json

{
  "content": "Explain attention mechanisms",
  "paper_references": ["paper1", "paper2"],
  "use_context": true,
  "model": "gemini"
}
```

Response:
```json
{
  "id": 3,
  "session_id": 1,
  "role": "assistant",
  "content": "Attention mechanisms allow models to focus...",
  "paper_references": null,
  "token_count": null,
  "created_at": "2024-01-15T10:31:00"
}
```

### Chat Statistics
```http
GET /api/chat/stats
```

Response:
```json
{
  "total_sessions": 10,
  "total_messages": 150,
  "last_chat_at": "2024-01-15T10:30:00"
}
```

---

## 📄 Papers API (`/api/papers`)

### Add Paper
```http
POST /api/papers/
Content-Type: application/json

{
  "title": "Attention Is All You Need",
  "authors": "Vaswani et al.",
  "publication_year": 2017,
  "venue": "NeurIPS",
  "doi": "10.48550/arXiv.1706.03762",
  "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
  "notes": "Seminal transformer paper",
  "tags": "transformers,attention,nlp"
}
```

### List Papers
```http
GET /api/papers/?skip=0&limit=50
```

### Get Paper
```http
GET /api/papers/{paper_id}
```

### Update Paper
```http
PUT /api/papers/{paper_id}
Content-Type: application/json

{
  "notes": "Updated notes",
  "tags": "transformers,attention,nlp,architecture"
}
```

### Delete Paper
```http
DELETE /api/papers/{paper_id}
```

### Paper Statistics
```http
GET /api/papers/stats
```

---

## 👥 Users API (`/api/users`)

### Register User
```http
POST /api/users/register
Content-Type: application/json

{
  "firebase_uid": "firebase_uid_123",
  "email": "user@example.com",
  "name": "John Doe"
}
```

### Get User Profile
```http
GET /api/users/me
```

### Update Profile
```http
PUT /api/users/profile
Content-Type: application/json

{
  "institution": "MIT",
  "department": "Computer Science",
  "role": "PhD Student",
  "bio": "Researching transformers"
}
```

---

## 📊 Activity API (`/api/activity`)

### Get Recent Activity
```http
GET /api/activity/recent?limit=20
```

### Log Activity
```http
POST /api/activity/log
Content-Type: application/json

{
  "activity_type": "paper_added",
  "description": "Added paper to library",
  "entity_type": "paper",
  "entity_id": 123
}
```

---

## 🔑 API Key Configuration

### Environment Variables Required

```bash
# Gemini API Keys (8 keys for rotation)
AI_API_KEY_1=your_key_1
AI_API_KEY_2=your_key_2
AI_API_KEY_3=your_key_3
AI_API_KEY_4=your_key_4
AI_API_KEY_5=your_key_5
AI_API_KEY_6=your_key_6
AI_API_KEY_7=your_key_7
AI_API_KEY_8=your_key_8

# A4F API Keys (7 keys for rotation)
A4F_API_KEY_1=your_a4f_key_1
A4F_API_KEY_2=your_a4f_key_2
A4F_API_KEY_3=your_a4f_key_3
A4F_API_KEY_4=your_a4f_key_4
A4F_API_KEY_5=your_a4f_key_5
A4F_API_KEY_6=your_a4f_key_6
A4F_API_KEY_7=your_a4f_key_7

# A4F Configuration
A4F_BASE_URL=https://api.a4f.co/v1
A4F_MODEL=provider-5/gpt-4o-mini

# OpenAlex Configuration
OPENALEX_EMAIL=your-email@example.com
```

### Key Rotation Features
- **Automatic Failover**: If one key fails, automatically tries the next
- **Random Selection**: Distributes load across all keys
- **Retry Logic**: Attempts all keys before giving up
- **Usage**: Keys are rotated automatically in Search and Chat APIs

---

## 📦 Response Formats

### Success Response
```json
{
  "id": 1,
  "field": "value",
  "created_at": "2024-01-15T10:00:00"
}
```

### Error Response
```json
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes
- `200 OK`: Success
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `502 Bad Gateway`: External API error
- `503 Service Unavailable`: Service temporarily down
- `504 Gateway Timeout`: Request timeout

---

## 🚀 Deployment

### DigitalOcean App Platform
- **Python Version**: 3.11
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8080`
- **Source Directory**: `backend`
- **Environment Variables**: Set all API keys in App Platform settings

### CORS Configuration
Currently allows:
- `http://localhost:5173`
- `http://localhost:5174`
- `https://citemesh.web.app`
- `https://citemesh.firebaseapp.com`

---

## 📚 Additional Resources

- **API Key Rotation**: See `backend/API_KEY_ROTATION.md`
- **Models Schema**: See `backend/app/models.py`
- **Database**: SQLite (development), PostgreSQL (production recommended)
