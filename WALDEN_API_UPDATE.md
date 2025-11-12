# OpenAlex Walden API Integration

## Update Date: November 10, 2025

CiteMesh has been updated to use the new **OpenAlex Walden** rewrite, launched November 3, 2025.

## What Changed

### API Parameters
All OpenAlex API calls now include:
- `data-version=2` - Activates Walden backend (new engine)
- `include_xpac=true` - Includes expanded content pack from DataCite

### Benefits


✅ **190M+ new works** - Datasets, software, dissertations from DataCite  
✅ **Better metadata** - More citations, better references, improved OA detection  
✅ **Better language detection** - Accurate non-English work classification  
✅ **Better licenses** - More complete license information  
✅ **Faster performance** - Optimized backend processing  

## Files Updated

### Frontend (citemesh-ui)
1. **`/src/config/openalex.ts`** (NEW)
   - Centralized OpenAlex API configuration
   - `fetchFromOpenAlex()` helper function
   - Automatic Walden parameter injection

2. **`/src/pages/PaperDetail.tsx`**
   - Updated to use `fetchFromOpenAlex()` helper
   - Paper detail fetching uses Walden API
   - Related papers fetching uses Walden API

### Backend
1. **`/backend/app/api/search.py`**
   - Added `data-version=2` and `include_xpac=true` to all OpenAlex requests
   - Updated search endpoint
   - Updated trending topics endpoint  
   - Updated stats endpoint
   - Added documentation comments

## Usage

### Frontend
```typescript
import { fetchFromOpenAlex } from '../config/openalex';

// Fetch a work by ID (automatically includes Walden parameters)
const response = await fetchFromOpenAlex('/works/W2741809807');

// Search with custom parameters
const response = await fetchFromOpenAlex('/works', {
  search: 'machine learning',
  per_page: '25'
});
```

### Backend
```python
# All OpenAlex requests automatically include Walden parameters
params = {
    "search": query,
    "data-version": "2",
    "include_xpac": "true"
}
```

## Coming Soon (Q4 2025)

OpenAlex announced these features are coming:

1. **PDF Download Endpoint** 🔥
   - Direct PDF access by DOI/OpenAlex ID
   - Will allow us to cache PDFs in DigitalOcean Spaces
   - Better control over PDF viewing experience

2. **Vector Search Endpoint**
   - Semantic similarity search
   - Better "related papers" discovery
   - Natural language queries

3. **Community Curation Portal**
   - Wikipedia-style metadata editing
   - Changes live in days
   - Fix errors directly

4. **Better Funding Metadata**
   - New grants entity
   - Better coverage of grants and funders

## Testing

To verify Walden is working:

```bash
# Frontend - check browser network tab
# Should see: ?data-version=2&include_xpac=true in all OpenAlex URLs

# Backend - test search endpoint
curl "https://paperverse-kvw2y.ondigitalocean.app/api/search" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"query": "machine learning", "page": 1, "per_page": 10}'
```

## Documentation

- OpenAlex Docs: https://docs.openalex.org/
- Walden Release Notes: https://blog.ourresearch.org/openalex-walden-launch/
- OREO Comparison Tool: https://oreo.openalex.org/

## Notes

- Old API data (`data-version=1`) is still available until December 2025
- The Walden dataset is 5% different from classic (mostly improvements)
- All IDs remain stable across versions
- Schema hasn't changed, just better data quality
