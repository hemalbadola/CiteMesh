# API Key Rotation - Usage Guide

## Overview

The `APIKeyRotator` utility provides automatic API key rotation with fallback support. When one key fails (rate limit, quota exceeded, etc.), it automatically tries the next available key.

## Features

- ✅ **Automatic rotation** - Cycles through keys when one fails
- ✅ **Multiple providers** - Works with Gemini, A4F, or any API keys
- ✅ **Random selection** - Can pick random keys for load distribution
- ✅ **Easy integration** - Simple Python class

## Setup

### Environment Variables

Your `.env` file should have numbered keys:

```env
# Gemini API Keys
AI_API_KEY_1=AIzaSy...
AI_API_KEY_2=AIzaSy...
AI_API_KEY_3=AIzaSy...

# A4F API Keys
A4F_API_KEY_1=ddc-a4f-...
A4F_API_KEY_2=ddc-a4f-...
A4F_API_KEY_3=ddc-a4f-...
```

## Usage

### Basic Usage

```python
from app.core.api_key_rotator import APIKeyRotator

# Create rotator for Gemini keys
gemini_rotator = APIKeyRotator("AI_API_KEY")

# Get current key
key = gemini_rotator.get_key()

# Rotate to next key
next_key = gemini_rotator.rotate()

# Get random key
random_key = gemini_rotator.get_random_key()
```

### With Retry Logic

```python
from app.core.api_key_rotator import APIKeyRotator
import requests

# Initialize rotator
a4f_rotator = APIKeyRotator("A4F_API_KEY")

max_retries = a4f_rotator.total_keys()

for attempt in range(max_retries):
    api_key = a4f_rotator.get_key()
    
    try:
        # Make API call
        response = requests.post(
            "https://api.a4f.co/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "provider-5/gpt-4o-mini",
                "messages": [{"role": "user", "content": "Hello"}]
            }
        )
        
        if response.status_code == 200:
            print("Success!")
            break
        else:
            print(f"Key {attempt + 1} failed, rotating...")
            a4f_rotator.rotate()
            
    except Exception as e:
        print(f"Error: {e}, rotating...")
        a4f_rotator.rotate()
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from app.core.api_key_rotator import APIKeyRotator

app = FastAPI()
a4f_rotator = APIKeyRotator("A4F_API_KEY")

@app.post("/chat")
async def chat(message: str):
    max_attempts = a4f_rotator.total_keys()
    
    for _ in range(max_attempts):
        key = a4f_rotator.get_key()
        
        try:
            # Your API call here
            result = make_api_call(key, message)
            return {"response": result}
        except RateLimitError:
            # Rotate and try next key
            a4f_rotator.rotate()
            continue
    
    raise HTTPException(status_code=503, detail="All API keys exhausted")
```

### Using Convenience Functions

```python
from app.core.api_key_rotator import get_gemini_key, get_a4f_key

# Quick access to keys
gemini_key = get_gemini_key()
a4f_key = get_a4f_key()
```

## Testing

### Test All A4F Keys

```bash
cd backend
source .venv/bin/activate
python test_a4f_keys.py
```

Output:
```
============================================================
A4F API KEY TESTER
============================================================
📊 Found 7 A4F API keys to test

🔑 Testing A4F_API_KEY_1...
   ✅ SUCCESS - Response: Hello!

...

✅ Working keys: 7/7
✨ Key rotation ready!
```

### Test Rotator

```bash
python app/core/api_key_rotator.py
```

## Available Models (A4F)

Popular models tested and working:

- `provider-5/gpt-4o-mini` - Fast and cheap OpenAI model
- `provider-5/gpt-5-nano` - Advanced reasoning model
- `provider-3/llama-3.3-70b` - Large open-source model
- `provider-3/qwen-2.5-72b` - High-performance Chinese model
- `provider-5/gemini-2.5-flash` - Google's Gemini

Full list: See `curl https://api.a4f.co/v1/models`

## Rate Limiting Strategy

The rotator helps avoid rate limits:

1. **Round-robin**: Default rotation pattern
2. **Random**: Use `get_random_key()` for load distribution
3. **Fallback**: Automatic retry with next key on failure

## Current Setup

✅ **Gemini**: 8 API keys configured
✅ **A4F**: 7 API keys configured (all tested and working)

## Example: Chat API with Rotation

```python
from openai import OpenAI
from app.core.api_key_rotator import APIKeyRotator

a4f_rotator = APIKeyRotator("A4F_API_KEY")

def chat_with_retry(message: str, max_attempts: int = None):
    if max_attempts is None:
        max_attempts = a4f_rotator.total_keys()
    
    for attempt in range(max_attempts):
        try:
            client = OpenAI(
                api_key=a4f_rotator.get_key(),
                base_url="https://api.a4f.co/v1"
            )
            
            response = client.chat.completions.create(
                model="provider-5/gpt-4o-mini",
                messages=[{"role": "user", "content": message}]
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            a4f_rotator.rotate()
    
    raise Exception("All keys exhausted")

# Usage
result = chat_with_retry("Explain API gateways")
print(result)
```

## Notes

- Keys rotate automatically on failure
- No manual tracking needed
- Works with any API that uses bearer token auth
- Thread-safe for concurrent requests (each request gets a key)
