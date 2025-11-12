"""
PDF Service for on-demand paper downloads
Handles: Hugging Face dataset, arXiv direct, and DigitalOcean Spaces caching
"""
import base64
import os
import re
from typing import Optional, Dict
import requests
import boto3
from datasets import load_dataset
from botocore.exceptions import ClientError

# DigitalOcean Spaces configuration
SPACE_NAME = os.getenv("DO_SPACES_BUCKET", "paperverse-papers")
SPACE_REGION = os.getenv("DO_SPACES_REGION", "blr1")
SPACE_ENDPOINT = f"https://{SPACE_REGION}.digitaloceanspaces.com"
SPACE_KEY = os.getenv("DO_SPACES_KEY")
SPACE_SECRET = os.getenv("DO_SPACES_SECRET")

# Initialize S3 client
s3_client = None
if SPACE_KEY and SPACE_SECRET:
    s3_client = boto3.client(
        's3',
        region_name=SPACE_REGION,
        endpoint_url=SPACE_ENDPOINT,
        aws_access_key_id=SPACE_KEY,
        aws_secret_access_key=SPACE_SECRET
    )

# Hugging Face dataset (lazy loading)
hf_dataset = None


def get_hf_dataset():
    """Lazy load Hugging Face dataset"""
    global hf_dataset
    if hf_dataset is None:
        try:
            hf_dataset = load_dataset(
                "laion/CS-Arxiv-PDFs-08-25",
                split="train",
                streaming=True
            )
        except Exception as e:
            print(f"Failed to load HF dataset: {e}")
            hf_dataset = False  # Mark as failed
    return hf_dataset if hf_dataset is not False else None


def extract_arxiv_id(work_id: str, doi: Optional[str] = None) -> Optional[str]:
    """
    Extract arXiv ID from OpenAlex work ID or DOI
    
    Examples:
    - https://openalex.org/W2741809807 → None (not arXiv)
    - DOI: 10.48550/arXiv.2301.12345 → 2301.12345
    - https://arxiv.org/abs/2301.12345 → 2301.12345
    """
    # Try DOI first
    if doi:
        arxiv_match = re.search(r'arxiv\.(\d{4}\.\d{4,5})', doi.lower())
        if arxiv_match:
            return arxiv_match.group(1)
    
    # Try work_id if it contains arxiv reference
    if work_id and 'arxiv' in work_id.lower():
        arxiv_match = re.search(r'(\d{4}\.\d{4,5})', work_id)
        if arxiv_match:
            return arxiv_match.group(1)
    
    return None


def check_spaces_cache(arxiv_id: str) -> Optional[str]:
    """Check if PDF exists in DigitalOcean Spaces cache"""
    if not s3_client:
        return None
    
    try:
        key = f"arxiv/{arxiv_id}.pdf"
        s3_client.head_object(Bucket=SPACE_NAME, Key=key)
        return f"https://{SPACE_NAME}.{SPACE_REGION}.digitaloceanspaces.com/{key}"
    except ClientError:
        return None


def upload_to_spaces(arxiv_id: str, pdf_bytes: bytes) -> Optional[str]:
    """Upload PDF to DigitalOcean Spaces"""
    if not s3_client:
        return None
    
    try:
        key = f"arxiv/{arxiv_id}.pdf"
        s3_client.put_object(
            Bucket=SPACE_NAME,
            Key=key,
            Body=pdf_bytes,
            ContentType='application/pdf',
            ACL='public-read'
        )
        return f"https://{SPACE_NAME}.{SPACE_REGION}.digitaloceanspaces.com/{key}"
    except Exception as e:
        print(f"Failed to upload to Spaces: {e}")
        return None


def download_from_huggingface(arxiv_id: str) -> Optional[bytes]:
    """
    Try to find and download PDF from Hugging Face dataset
    
    Note: HF dataset uses format like "000000001/0000001" but we need to
    map arXiv IDs to this format. This is complex, so we'll use streaming
    search which is slow but works.
    """
    dataset = get_hf_dataset()
    if not dataset:
        return None
    
    try:
        # This is slow but necessary - we need to search through the dataset
        # In production, you'd want to build an index mapping arXiv IDs to HF keys
        # For now, we'll skip HF search and go straight to arXiv direct
        return None
    except Exception as e:
        print(f"HF download error: {e}")
        return None


def download_from_arxiv(arxiv_id: str) -> Optional[bytes]:
    """Download PDF directly from arXiv"""
    try:
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'CiteMesh/1.0 (Academic Research Tool)'
        })
        
        if response.status_code == 200 and response.headers.get('Content-Type') == 'application/pdf':
            return response.content
        
        return None
    except Exception as e:
        print(f"arXiv download error: {e}")
        return None


def get_pdf_url(work_id: str, doi: Optional[str] = None, existing_pdf_url: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Get PDF URL for a paper, downloading and caching if necessary
    
    Returns:
        {
            "pdf_url": "https://...",  # URL to PDF
            "source": "cache|arxiv|openalex|none",  # Where PDF came from
            "arxiv_id": "2301.12345",  # arXiv ID if available
            "error": "Error message if failed"
        }
    """
    # If OpenAlex already has a PDF URL, use it
    if existing_pdf_url:
        return {
            "pdf_url": existing_pdf_url,
            "source": "openalex",
            "arxiv_id": None,
            "error": None
        }
    
    # Try to extract arXiv ID
    arxiv_id = extract_arxiv_id(work_id, doi)
    if not arxiv_id:
        return {
            "pdf_url": None,
            "source": "none",
            "arxiv_id": None,
            "error": "Not an arXiv paper"
        }
    
    # Check cache first
    cached_url = check_spaces_cache(arxiv_id)
    if cached_url:
        return {
            "pdf_url": cached_url,
            "source": "cache",
            "arxiv_id": arxiv_id,
            "error": None
        }
    
    # Try Hugging Face (currently disabled as search is too slow)
    # hf_pdf = download_from_huggingface(arxiv_id)
    # if hf_pdf:
    #     url = upload_to_spaces(arxiv_id, hf_pdf)
    #     if url:
    #         return {"pdf_url": url, "source": "huggingface", "arxiv_id": arxiv_id, "error": None}
    
    # Try arXiv direct download
    arxiv_pdf = download_from_arxiv(arxiv_id)
    if arxiv_pdf:
        url = upload_to_spaces(arxiv_id, arxiv_pdf)
        if url:
            return {
                "pdf_url": url,
                "source": "arxiv",
                "arxiv_id": arxiv_id,
                "error": None
            }
        else:
            # Upload failed but we have the PDF, return arXiv URL
            return {
                "pdf_url": f"https://arxiv.org/pdf/{arxiv_id}.pdf",
                "source": "arxiv",
                "arxiv_id": arxiv_id,
                "error": None
            }
    
    return {
        "pdf_url": None,
        "source": "none",
        "arxiv_id": arxiv_id,
        "error": "PDF not available"
    }
