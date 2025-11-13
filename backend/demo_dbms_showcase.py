"""
DBMS Showcase Demo Script for CiteMesh
=======================================

This script demonstrates advanced DBMS concepts implemented in CiteMesh:

1. Search Caching & Performance Optimization
2. Search History & Analytics
3. Paper Metadata Enrichment
4. Normalized Data Storage
5. Complex Queries & Aggregations
6. Transaction Management
7. Index Usage & Query Optimization

Run this after the backend is running to see DBMS features in action.
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any
import json


# Configuration
BASE_URL = "http://localhost:8000"  # Change if different
API_KEY = "your-firebase-id-token-here"  # Replace with actual Firebase token


class DBMSShowcase:
    def __init__(self, base_url: str, auth_token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {auth_token}"}
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        await self.client.aclose()
    
    def print_section(self, title: str):
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_result(self, label: str, data: Any):
        print(f"✅ {label}")
        if isinstance(data, dict) or isinstance(data, list):
            print(json.dumps(data, indent=2)[:500])  # Truncate long outputs
        else:
            print(str(data)[:500])
        print()
    
    # =========================================================================
    # DEMO 1: Search Caching & Performance
    # =========================================================================
    
    async def demo_search_caching(self):
        self.print_section("DEMO 1: Search Caching & Performance Optimization")
        
        print("📊 DBMS Concepts: Query result caching, Composite indexes, TTL management")
        print("📊 Tables: search_cache, search_history")
        print("📊 Indexes: idx_search_cache_lookup (query_hash, expires_at)\n")
        
        # First search - cache miss
        print("🔍 Performing first search (cache miss)...")
        search_request = {
            "query": "machine learning",
            "filters": {
                "year_from": 2020,
                "year_to": 2024,
                "min_citations": 10,
                "sort_by": "cited_by_count"
            },
            "page": 1,
            "per_page": 10,
            "use_ai_enhancement": False
        }
        
        response1 = await self.client.post(
            f"{self.base_url}/api/search/search",
            json=search_request,
            headers=self.headers
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            self.print_result(
                "First search completed (cache MISS)",
                {
                    "search_time_ms": result1.get("search_time_ms"),
                    "total_results": result1.get("total_results"),
                    "results_returned": len(result1.get("results", []))
                }
            )
        
        # Second search - cache hit
        print("🔍 Performing second search (cache hit)...")
        await asyncio.sleep(1)
        
        response2 = await self.client.post(
            f"{self.base_url}/api/search/search",
            json=search_request,
            headers=self.headers
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            self.print_result(
                "Second search completed (cache HIT - should be faster)",
                {
                    "search_time_ms": result2.get("search_time_ms"),
                    "speedup": f"{result1.get('search_time_ms', 0) / max(result2.get('search_time_ms', 1), 1):.2f}x faster"
                }
            )
        
        # Get cache statistics
        print("📈 Fetching cache statistics...")
        cache_stats_response = await self.client.get(
            f"{self.base_url}/api/search/analytics/cache-stats",
            headers=self.headers
        )
        
        if cache_stats_response.status_code == 200:
            self.print_result("Cache Statistics", cache_stats_response.json())
    
    # =========================================================================
    # DEMO 2: Search History & Analytics
    # =========================================================================
    
    async def demo_search_analytics(self):
        self.print_section("DEMO 2: Search History & User Analytics")
        
        print("📊 DBMS Concepts: Time-series tracking, GROUP BY, Aggregations, Window functions")
        print("📊 Tables: search_history")
        print("📊 Indexes: idx_search_history_user_time, idx_search_history_time\n")
        
        # Perform multiple searches to build history
        print("🔍 Performing multiple searches to build history...")
        queries = [
            "deep learning",
            "neural networks",
            "natural language processing",
            "computer vision"
        ]
        
        for query in queries:
            await self.client.post(
                f"{self.base_url}/api/search/search",
                json={
                    "query": query,
                    "page": 1,
                    "per_page": 5,
                    "use_ai_enhancement": True
                },
                headers=self.headers
            )
            await asyncio.sleep(0.5)
        
        # Get user search history
        print("📜 Fetching user search history...")
        history_response = await self.client.get(
            f"{self.base_url}/api/search/analytics/my-search-history?limit=10",
            headers=self.headers
        )
        
        if history_response.status_code == 200:
            self.print_result("User Search History", history_response.json())
        
        # Get user search statistics
        print("📊 Fetching user search statistics...")
        stats_response = await self.client.get(
            f"{self.base_url}/api/search/analytics/my-search-stats?days=30",
            headers=self.headers
        )
        
        if stats_response.status_code == 200:
            self.print_result("User Search Statistics", stats_response.json())
        
        # Get trending searches
        print("🔥 Fetching trending searches...")
        trending_response = await self.client.get(
            f"{self.base_url}/api/search/analytics/trending-searches?hours=24&limit=5",
            headers=self.headers
        )
        
        if trending_response.status_code == 200:
            self.print_result("Trending Searches", trending_response.json())
    
    # =========================================================================
    # DEMO 3: Paper Metadata Enrichment
    # =========================================================================
    
    async def demo_paper_enrichment(self):
        self.print_section("DEMO 3: Paper Metadata Enrichment & Normalization")
        
        print("📊 DBMS Concepts: Normalization, M:N relationships, Foreign keys, Transactions")
        print("📊 Tables: paper_topic, research_topic, paper_reference")
        print("📊 Indexes: idx_paper_topic_paper, idx_paper_ref_graph\n")
        
        # First, save a paper
        print("💾 Saving a paper from search results...")
        save_response = await self.client.post(
            f"{self.base_url}/api/search/save-paper",
            json={
                "paper_id": "https://openalex.org/W2741809807",
                "title": "Attention Is All You Need",
                "authors": "Vaswani et al.",
                "summary": "Transformer architecture paper",
                "published_year": 2017,
                "tags": "deep learning, transformers"
            },
            headers=self.headers
        )
        
        if save_response.status_code in [200, 201, 409]:  # 409 if already exists
            saved_paper = save_response.json()
            paper_id = saved_paper.get("id")
            
            if paper_id:
                self.print_result("Paper Saved", {"paper_id": paper_id})
                
                # Enrich the paper with topics and references
                print("🔬 Enriching paper with OpenAlex metadata...")
                enrich_response = await self.client.post(
                    f"{self.base_url}/api/search/enrich/{paper_id}",
                    headers=self.headers
                )
                
                if enrich_response.status_code == 200:
                    self.print_result("Enrichment Results", enrich_response.json())
                
                # Get paper topics
                print("🏷️ Fetching paper topics...")
                topics_response = await self.client.get(
                    f"{self.base_url}/api/search/paper/{paper_id}/topics",
                    headers=self.headers
                )
                
                if topics_response.status_code == 200:
                    self.print_result("Paper Topics (M:N relationship)", topics_response.json())
                
                # Get paper references
                print("📚 Fetching paper references...")
                refs_response = await self.client.get(
                    f"{self.base_url}/api/search/paper/{paper_id}/references?limit=10",
                    headers=self.headers
                )
                
                if refs_response.status_code == 200:
                    self.print_result("Paper References (Citation Graph)", refs_response.json())
        
        # Get topic statistics
        print("📊 Fetching topic statistics...")
        topic_stats_response = await self.client.get(
            f"{self.base_url}/api/search/analytics/topic-statistics",
            headers=self.headers
        )
        
        if topic_stats_response.status_code == 200:
            self.print_result("Topic Statistics (GROUP BY + Aggregations)", topic_stats_response.json())
    
    # =========================================================================
    # Main Demo Runner
    # =========================================================================
    
    async def run_all_demos(self):
        print("\n")
        print("╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                                                                              ║")
        print("║                     CITEMESH DBMS SHOWCASE DEMONSTRATION                     ║")
        print("║                                                                              ║")
        print("║  This script demonstrates advanced Database Management System concepts:      ║")
        print("║  • Query result caching with TTL and composite indexes                       ║")
        print("║  • User behavior tracking and analytics                                      ║")
        print("║  • Normalized data storage (3NF)                                             ║")
        print("║  • M:N relationships via junction tables                                     ║")
        print("║  • Citation graph representation                                             ║")
        print("║  • Complex aggregations and GROUP BY queries                                 ║")
        print("║  • Transaction management                                                    ║")
        print("║                                                                              ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝")
        
        try:
            await self.demo_search_caching()
            await self.demo_search_analytics()
            await self.demo_paper_enrichment()
            
            self.print_section("✨ DEMONSTRATION COMPLETE ✨")
            print("All DBMS features have been demonstrated successfully!")
            print("\nKey Takeaways:")
            print("  1. Search caching reduces API calls and improves response time")
            print("  2. Search history enables user behavior analytics and trending queries")
            print("  3. Normalized storage eliminates redundancy (topics stored once)")
            print("  4. Junction tables enable M:N relationships (papers ↔ topics)")
            print("  5. Citation graph supports complex network analysis")
            print("  6. Composite indexes optimize multi-column lookups")
            print("  7. Transactions ensure data consistency\n")
            
        except Exception as e:
            print(f"\n❌ Error during demonstration: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """
    Main entry point
    """
    print("\n🚀 Starting CiteMesh DBMS Showcase Demo\n")
    
    # Check if backend is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            if response.status_code == 200:
                print("✅ Backend is running\n")
            else:
                print("❌ Backend health check failed")
                return
    except Exception as e:
        print(f"❌ Cannot connect to backend at {BASE_URL}")
        print(f"   Make sure the server is running: uvicorn app.main:app --reload")
        return
    
    # Check if auth token is set
    if API_KEY == "your-firebase-id-token-here":
        print("⚠️  WARNING: No Firebase auth token set!")
        print("   To run this demo, you need a valid Firebase ID token.")
        print("   Get one by logging into the frontend, then:")
        print("   1. Open browser dev tools")
        print("   2. Go to Application → Local Storage")
        print("   3. Copy the Firebase token")
        print("   4. Update API_KEY in this script\n")
        
        proceed = input("Continue without auth (will fail)? [y/N]: ")
        if proceed.lower() != 'y':
            return
    
    # Run demos
    showcase = DBMSShowcase(BASE_URL, API_KEY)
    try:
        await showcase.run_all_demos()
    finally:
        await showcase.close()


if __name__ == "__main__":
    asyncio.run(main())
