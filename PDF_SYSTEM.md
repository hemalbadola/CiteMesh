# PDF On-Demand Download System

## Overview

CiteMesh now supports on-demand PDF downloads for research papers. When a user wants to read or chat with a paper, the system automatically:

1. **Checks cache** - Looks in DigitalOcean Spaces for previously downloaded papers
2. **Downloads from arXiv** - If not cached, downloads directly from arXiv
3. **Caches for future** - Saves to DigitalOcean Spaces for faster access next time
4. **Returns URL** - Provides the PDF URL to the frontend

## Architecture

```
User clicks "View PDF" or "Chat with Paper"
    ↓
Frontend calls: GET /api/pdf/get-pdf?work_id=W123&doi=10.48550/arXiv.2301.12345
    ↓
Backend checks:
    1. Is it an arXiv paper? (checks DOI/work_id)
    2. In DO Spaces cache? → Return cached URL
    3. Download from arXiv → Cache → Return URL
    ↓
Frontend displays PDF or enables chat
```

## API Endpoints

### Get PDF URL
```
GET /api/pdf/get-pdf
Query Parameters:
  - work_id: OpenAlex work ID (required)
  - doi: Paper DOI (optional, helps identify arXiv papers)
  - existing_pdf_url: OpenAlex PDF URL (optional, returned if available)

Response:
{
  "pdf_url": "https://paperverse-papers.blr1.digitaloceanspaces.com/arxiv/2301.12345.pdf",
  "source": "cache|arxiv|openalex",
  "arxiv_id": "2301.12345",
  "error": null
}
```

### Check PDF Availability
```
GET /api/pdf/check-pdf
Query Parameters:
  - work_id: OpenAlex work ID (required)
  - doi: Paper DOI (optional)

Response:
{
  "available": true,
  "source": "cache|arxiv|none",
  "cached": false,
  "arxiv_id": "2301.12345"
}
```

## Configuration

Add to your `.env` file:

```bash
DO_SPACES_KEY=your_digitalocean_spaces_key
DO_SPACES_SECRET=your_digitalocean_spaces_secret
DO_SPACES_BUCKET=paperverse-papers
DO_SPACES_REGION=blr1
```

## Coverage

- **arXiv papers**: ~2.5M CS papers (100% downloadable)
- **OpenAlex papers with existing PDFs**: Varies by field
- **Non-arXiv papers**: Not currently supported

## Cost Estimate

- **Storage**: $0.02/GB/month
  - 1000 papers ≈ 5GB ≈ $0.10/month
- **Bandwidth**: $0.01/GB outbound
  - 100 users/day ≈ 500 downloads/day ≈ $0.50/month
- **Total**: ~$1-5/month for typical usage

## Future Enhancements

1. **Hugging Face Integration**: Map arXiv IDs to HF dataset keys for faster downloads
2. **PubMed Central**: Add support for biomedical papers
3. **Unpaywall API**: Add open access papers from other sources
4. **Preemptive caching**: Cache popular papers before users request them
5. **CDN**: Add CloudFlare or similar for faster global access

## Frontend Integration

Example frontend code:

```javascript
// Get PDF URL when user clicks "View PDF"
const getPdfUrl = async (workId, doi) => {
  const response = await fetch(
    `/api/pdf/get-pdf?work_id=${workId}&doi=${encodeURIComponent(doi)}`
  );
  const data = await response.json();
  
  if (data.pdf_url) {
    window.open(data.pdf_url, '_blank');
  } else {
    alert(data.error || 'PDF not available');
  }
};

// Check if PDF is available (before showing button)
const checkPdfAvailable = async (workId, doi) => {
  const response = await fetch(
    `/api/pdf/check-pdf?work_id=${workId}&doi=${encodeURIComponent(doi)}`
  );
  const data = await response.json();
  return data.available;
};
```

## Testing

### Local Testing
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test API
curl "http://localhost:8000/api/pdf/get-pdf?work_id=W2741809807&doi=10.48550/arXiv.2301.12345"
```

### Production Testing
```bash
curl "https://paperverse-kvw2y.ondigitalocean.app/api/pdf/get-pdf?work_id=W2741809807&doi=10.48550/arXiv.2301.12345"
```

## Deployment

1. **Update environment variables** in DigitalOcean App Platform
2. **Deploy** the updated backend
3. **Test** with a few arXiv papers
4. **Monitor** DigitalOcean Spaces usage

## Troubleshooting

### PDF not downloading
- Check DO Spaces credentials
- Verify arXiv ID extraction (must be format: YYMM.NNNNN)
- Check arXiv is not rate limiting (429 error)

### Slow downloads
- First download takes ~2-5 seconds (from arXiv)
- Cached downloads are instant
- Consider CDN for better global performance

### Storage costs too high
- Monitor most-downloaded papers
- Consider setting TTL to delete old papers
- Implement smart caching (only cache papers accessed 2+ times)
