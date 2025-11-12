"""Test A4F API keys to verify they work."""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.api_key_rotator import APIKeyRotator

# Load environment variables
load_dotenv()

def test_a4f_key(api_key: str, key_number: int) -> bool:
    """
    Test a single A4F API key.
    
    Args:
        api_key: The API key to test
        key_number: The key number for display
    
    Returns:
        True if the key works, False otherwise
    """
    try:
        import requests
        
        url = "https://api.a4f.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "provider-5/gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Say 'Hello' in one word"}
            ],
            "max_tokens": 10
        }
        
        print(f"\n🔑 Testing A4F_API_KEY_{key_number}...")
        print(f"   Key: {api_key[:20]}...{api_key[-10:]}")
        
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            message = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"   ✅ SUCCESS - Response: {message}")
            return True
        else:
            print(f"   ❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR - {str(e)}")
        return False


def main():
    """Test all A4F API keys."""
    print("=" * 60)
    print("A4F API KEY TESTER")
    print("=" * 60)
    
    # Initialize rotator
    rotator = APIKeyRotator("A4F_API_KEY")
    total_keys = rotator.total_keys()
    
    if total_keys == 0:
        print("\n❌ No A4F API keys found in environment!")
        print("   Make sure you have A4F_API_KEY_1, A4F_API_KEY_2, etc. in your .env file")
        return
    
    print(f"\n📊 Found {total_keys} A4F API keys to test")
    
    # Test each key
    working_keys = []
    failed_keys = []
    
    for i, key in enumerate(rotator.get_all_keys(), 1):
        if test_a4f_key(key, i):
            working_keys.append((i, key))
        else:
            failed_keys.append((i, key))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Working keys: {len(working_keys)}/{total_keys}")
    print(f"❌ Failed keys: {len(failed_keys)}/{total_keys}")
    
    if working_keys:
        print("\n✅ Working keys:")
        for num, key in working_keys:
            print(f"   A4F_API_KEY_{num}: {key[:20]}...{key[-10:]}")
    
    if failed_keys:
        print("\n❌ Failed keys:")
        for num, key in failed_keys:
            print(f"   A4F_API_KEY_{num}: {key[:20]}...{key[-10:]}")
    
    print("\n" + "=" * 60)
    
    if len(working_keys) > 0:
        print("✨ Key rotation ready! At least one key is working.")
    else:
        print("⚠️  WARNING: No working keys found!")


if __name__ == "__main__":
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ 'requests' library not found!")
        print("   Install it with: pip install requests")
        sys.exit(1)
    
    main()
