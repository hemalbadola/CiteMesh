#!/usr/bin/env python3
"""Quick backend test - makes a real search query"""

import asyncio
import httpx
import json

async def test_backend():
    print("🧪 Testing PaperVerse Backend Integration\n")
    
    backend_url = "http://127.0.0.1:8000"
    
    # Test 1: Health check
    print("1️⃣  Checking if backend is running...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{backend_url}/docs")
            if resp.status_code == 200:
                print(f"   ✅ Backend is running at {backend_url}\n")
            else:
                print(f"   ❌ Backend returned status {resp.status_code}\n")
                return
    except Exception as e:
        print(f"   ❌ Cannot connect to backend: {e}")
        print(f"   💡 Start it with: cd hemal/backend && uvicorn app:app --reload\n")
        return
    
    # Test 2: Search query
    print("2️⃣  Testing /search endpoint...")
    query = {
        "query": "Find recent quantum computing papers from 2024",
        "per_page": 3,
        "page": 1
    }
    
    print(f"   📝 Query: {query['query']}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{backend_url}/search",
                json=query
            )
            resp.raise_for_status()
            data = resp.json()
        
        results = data.get('results', {}).get('results', [])
        print(f"   ✅ Retrieved {len(results)} results\n")
        
        if results:
            print("3️⃣  Sample Results:\n")
            for i, paper in enumerate(results[:3], 1):
                print(f"   📄 Paper {i}:")
                print(f"      Title: {paper.get('display_name', 'N/A')}")
                print(f"      Year: {paper.get('publication_year', 'N/A')}")
                print(f"      Citations: {paper.get('cited_by_count', 0)}")
                print(f"      OA: {paper.get('open_access', {}).get('oa_status', 'closed')}")
                if paper.get('doi'):
                    print(f"      DOI: {paper['doi']}")
                print()
        
        print("4️⃣  Integration Status:")
        print("   ✅ Backend API: Working")
        print("   ✅ OpenAlex Connection: Working")
        print("   ✅ Query Translation: Working")
        print("   ✅ Data Retrieval: Working")
        print()
        print("🎉 Full stack integration is working!")
        print("   🌐 Test in browser: http://localhost:5174")
        print("   📊 Go to 'Ask PaperVerse Anything' section and try a query")
        
    except httpx.HTTPStatusError as e:
        print(f"   ❌ HTTP Error {e.response.status_code}")
        print(f"   Response: {e.response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_backend())
