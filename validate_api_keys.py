#!/usr/bin/env python3
"""
API Key Validator - Tests all configured Gemini API keys
"""

import os
import sys
from pathlib import Path
import asyncio
import httpx

# Load .env file
env_file = Path(__file__).parent / "hemal" / "backend" / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key] = value

api_keys = os.getenv("AI_API_KEYS", "").split(",")
api_keys = [key.strip() for key in api_keys if key.strip()]

if not api_keys:
    print("❌ No API keys found in AI_API_KEYS")
    sys.exit(1)

print(f"🔑 Found {len(api_keys)} API key(s) to test\n")

async def test_api_key(key: str, index: int) -> tuple[int, bool, str]:
    """Test a single API key"""
    masked_key = f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"
    
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash-lite:generateContent"
    payload = {
        "contents": [{
            "role": "user",
            "parts": [{"text": "Say 'test' only"}]
        }],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 10
        }
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{url}?key={key}",
                json=payload
            )
            
            if response.status_code == 200:
                return (index, True, masked_key)
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", "Invalid key")
                return (index, False, f"{masked_key} - {error_msg}")
            else:
                return (index, False, f"{masked_key} - HTTP {response.status_code}")
                
    except Exception as e:
        return (index, False, f"{masked_key} - Error: {str(e)}")

async def main():
    print("Testing API keys...\n")
    
    tasks = [test_api_key(key, i+1) for i, key in enumerate(api_keys)]
    results = await asyncio.gather(*tasks)
    
    valid_keys = []
    invalid_keys = []
    
    for index, is_valid, message in sorted(results):
        if is_valid:
            print(f"✅ Key {index}: {message} - VALID")
            valid_keys.append(api_keys[index-1])
        else:
            print(f"❌ Key {index}: {message} - INVALID")
            invalid_keys.append(api_keys[index-1])
    
    print(f"\n📊 Summary:")
    print(f"   Valid: {len(valid_keys)}/{len(api_keys)}")
    print(f"   Invalid: {len(invalid_keys)}/{len(api_keys)}")
    
    if invalid_keys:
        print(f"\n⚠️  Found {len(invalid_keys)} invalid key(s)")
        print(f"\n💡 To fix:")
        print(f"   1. Edit: hemal/backend/.env")
        print(f"   2. Update AI_API_KEYS with only valid keys")
        
        if valid_keys:
            print(f"\n✅ Suggested AI_API_KEYS (valid keys only):")
            print(f"   AI_API_KEYS={','.join(valid_keys)}")
    else:
        print(f"\n🎉 All API keys are valid!")
    
    return len(invalid_keys) == 0

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
