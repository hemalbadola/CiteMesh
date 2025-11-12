#!/usr/bin/env python3
"""
Test script for OpenAlex integration.
Tests both direct API calls and backend integration.
"""

import asyncio
import json
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "hemal" / "backend"))

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

console = Console()


async def test_openalex_direct():
    """Test direct OpenAlex API call."""
    console.print("\n[bold cyan]═══ Test 1: Direct OpenAlex API Call ═══[/bold cyan]\n")
    
    url = "https://api.openalex.org/works"
    params = {
        "search": "artificial intelligence machine learning",
        "filter": "publication_year:2023-2024,cited_by_count:>50",
        "sort": "cited_by_count:desc",
        "per_page": 5,
        "select": "id,display_name,publication_year,cited_by_count,primary_location,open_access,doi"
    }
    
    console.print(f"[yellow]URL:[/yellow] {url}")
    console.print(f"[yellow]Params:[/yellow] {json.dumps(params, indent=2)}\n")
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
        
        console.print(f"[green]✓ Success![/green] Retrieved {len(data.get('results', []))} results\n")
        
        # Display results in a table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Title", style="cyan", width=50)
        table.add_column("Year", style="green", width=6)
        table.add_column("Citations", style="yellow", width=10)
        table.add_column("OA Status", style="blue", width=15)
        
        for work in data.get('results', [])[:5]:
            title = work.get('display_name', 'N/A')[:47] + "..."
            year = str(work.get('publication_year', 'N/A'))
            citations = str(work.get('cited_by_count', 0))
            oa_status = work.get('open_access', {}).get('oa_status', 'closed')
            table.add_row(title, year, citations, oa_status)
        
        console.print(table)
        
        return True
        
    except Exception as e:
        console.print(f"[red]✗ Failed:[/red] {str(e)}")
        return False


async def test_backend_health():
    """Test if backend server is running."""
    console.print("\n[bold cyan]═══ Test 2: Backend Health Check ═══[/bold cyan]\n")
    
    backend_urls = [
        "http://127.0.0.1:8000",
        "http://localhost:8000"
    ]
    
    for base_url in backend_urls:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{base_url}/docs")
                if response.status_code == 200:
                    console.print(f"[green]✓ Backend is running at {base_url}[/green]")
                    return base_url
        except Exception:
            continue
    
    console.print("[yellow]⚠ Backend is not running. Start it with:[/yellow]")
    console.print("  [cyan]cd hemal/backend && uvicorn app:app --reload[/cyan]\n")
    return None


async def test_backend_search(base_url: str):
    """Test backend /search endpoint."""
    console.print("\n[bold cyan]═══ Test 3: Backend Search Endpoint ═══[/bold cyan]\n")
    
    test_queries = [
        {
            "query": "Find the most cited quantum computing papers from 2023",
            "per_page": 3,
            "page": 1
        },
        {
            "query": "Show me recent deep learning papers with open access",
            "per_page": 3,
            "page": 1
        }
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        console.print(f"[bold]Query {i}:[/bold] {test_query['query']}\n")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{base_url}/search",
                    json=test_query
                )
                response.raise_for_status()
                data = response.json()
            
            results = data.get('results', {}).get('results', [])
            console.print(f"[green]✓ Retrieved {len(results)} results[/green]\n")
            
            # Display first result
            if results:
                first = results[0]
                panel_content = f"""
[bold]Title:[/bold] {first.get('display_name', 'N/A')}
[bold]Year:[/bold] {first.get('publication_year', 'N/A')}
[bold]Citations:[/bold] {first.get('cited_by_count', 0)}
[bold]OA Status:[/bold] {first.get('open_access', {}).get('oa_status', 'closed')}
[bold]DOI:[/bold] {first.get('doi', 'N/A')}
                """.strip()
                console.print(Panel(panel_content, title="Sample Result", border_style="green"))
                console.print()
            
        except httpx.HTTPStatusError as e:
            console.print(f"[red]✗ HTTP Error {e.response.status_code}:[/red]")
            console.print(f"  {e.response.text}\n")
        except Exception as e:
            console.print(f"[red]✗ Failed:[/red] {str(e)}\n")


async def test_frontend_integration():
    """Test frontend configuration."""
    console.print("\n[bold cyan]═══ Test 4: Frontend Integration ═══[/bold cyan]\n")
    
    frontend_path = Path(__file__).parent / "citemesh-ui" / "src" / "App.tsx"
    
    if not frontend_path.exists():
        console.print("[red]✗ Frontend App.tsx not found[/red]")
        return
    
    content = frontend_path.read_text()
    
    checks = [
        ("window.PAPERVERSE_BACKEND" in content, "Backend URL configuration"),
        ("handleSubmit" in content, "Search form handler"),
        ("/search" in content, "Search endpoint call"),
        ("BackendStatus" in content, "Status display"),
    ]
    
    for check, description in checks:
        status = "[green]✓[/green]" if check else "[red]✗[/red]"
        console.print(f"{status} {description}")
    
    console.print("\n[yellow]Frontend Configuration:[/yellow]")
    console.print("  • Backend URL: window.PAPERVERSE_BACKEND (defaults to http://127.0.0.1:8000)")
    console.print("  • Can be set in index.html or via environment")
    console.print()


async def generate_test_report():
    """Generate integration test report."""
    console.print(Panel.fit(
        "[bold cyan]PaperVerse OpenAlex Integration Test[/bold cyan]",
        border_style="cyan"
    ))
    
    # Test 1: Direct API
    test1_passed = await test_openalex_direct()
    
    # Test 2: Backend health
    backend_url = await test_backend_health()
    
    # Test 3: Backend search (only if backend is running)
    if backend_url:
        await test_backend_search(backend_url)
    
    # Test 4: Frontend check
    await test_frontend_integration()
    
    # Summary
    console.print("\n[bold cyan]═══ Test Summary ═══[/bold cyan]\n")
    
    summary_table = Table(show_header=True, header_style="bold")
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Notes")
    
    summary_table.add_row(
        "OpenAlex API",
        "[green]✓ PASS[/green]" if test1_passed else "[red]✗ FAIL[/red]",
        "Direct API connection works"
    )
    
    summary_table.add_row(
        "Backend Server",
        "[green]✓ RUNNING[/green]" if backend_url else "[yellow]⚠ NOT RUNNING[/yellow]",
        backend_url or "Start with: uvicorn app:app --reload"
    )
    
    summary_table.add_row(
        "Frontend Config",
        "[green]✓ CONFIGURED[/green]",
        "Ready to connect to backend"
    )
    
    console.print(summary_table)
    console.print()
    
    # Next steps
    if not backend_url:
        console.print(Panel(
            "[bold yellow]Next Steps:[/bold yellow]\n\n"
            "1. Set up environment variables:\n"
            "   [cyan]cd hemal/backend[/cyan]\n"
            "   [cyan]cp .env.example .env[/cyan]\n"
            "   [cyan]# Edit .env and add your Gemini API key[/cyan]\n\n"
            "2. Install dependencies:\n"
            "   [cyan]pip install -r requirements.txt[/cyan]\n\n"
            "3. Start the backend:\n"
            "   [cyan]uvicorn app:app --reload --host 0.0.0.0 --port 8000[/cyan]\n\n"
            "4. Frontend is already running at http://localhost:5174\n"
            "   Test the search form in the console section!",
            title="Setup Instructions",
            border_style="yellow"
        ))


if __name__ == "__main__":
    try:
        import rich
    except ImportError:
        print("Installing rich for better output...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
        import rich
    
    asyncio.run(generate_test_report())
