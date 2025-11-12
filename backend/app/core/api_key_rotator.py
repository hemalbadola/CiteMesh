"""API Key rotation utility for handling multiple API keys with automatic fallback."""
import os
import random
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()


class APIKeyRotator:
    """Handles API key rotation with automatic fallback on failure."""
    
    def __init__(self, prefix: str):
        """
        Initialize the key rotator.
        
        Args:
            prefix: The prefix for the API keys (e.g., 'AI_API_KEY', 'A4F_API_KEY')
        """
        self.prefix = prefix
        self.keys = self._load_keys()
        self.current_index = 0
        
    def _load_keys(self) -> List[str]:
        """Load all API keys with the given prefix from environment."""
        keys = []
        i = 1
        while True:
            key = os.getenv(f"{self.prefix}_{i}")
            if not key:
                break
            keys.append(key)
            i += 1
        
        # Also try loading from comma-separated format
        if not keys:
            keys_str = os.getenv(f"{self.prefix}S")  # e.g., AI_API_KEYS or A4F_API_KEYS
            if keys_str:
                keys = [k.strip() for k in keys_str.split(',') if k.strip()]
        
        return keys
    
    def get_key(self) -> Optional[str]:
        """Get the current API key."""
        if not self.keys:
            return None
        return self.keys[self.current_index]
    
    def rotate(self) -> Optional[str]:
        """Rotate to the next API key and return it."""
        if not self.keys:
            return None
        
        self.current_index = (self.current_index + 1) % len(self.keys)
        return self.keys[self.current_index]
    
    def get_random_key(self) -> Optional[str]:
        """Get a random API key from the pool."""
        if not self.keys:
            return None
        return random.choice(self.keys)
    
    def mark_key_failed(self, key: str) -> None:
        """
        Mark a key as failed and rotate to the next one.
        This could be extended to track failed keys and avoid them.
        """
        if key in self.keys:
            # Remove the failed key from current index if it matches
            if self.keys[self.current_index] == key:
                self.rotate()
    
    def get_all_keys(self) -> List[str]:
        """Return all available keys."""
        return self.keys.copy()
    
    def total_keys(self) -> int:
        """Return the total number of keys available."""
        return len(self.keys)


# Convenience functions for common use cases
def get_gemini_key() -> Optional[str]:
    """Get a Gemini API key with rotation support."""
    rotator = APIKeyRotator("AI_API_KEY")
    return rotator.get_key()


def get_a4f_key() -> Optional[str]:
    """Get an A4F API key with rotation support."""
    rotator = APIKeyRotator("A4F_API_KEY")
    return rotator.get_key()


def get_key_with_retry(rotator: APIKeyRotator, max_attempts: Optional[int] = None) -> Optional[str]:
    """
    Get a key and allow retries up to the number of available keys.
    
    Args:
        rotator: The APIKeyRotator instance
        max_attempts: Maximum number of attempts (defaults to number of keys)
    
    Returns:
        A key from the rotator, or None if all keys exhausted
    """
    if max_attempts is None:
        max_attempts = rotator.total_keys()
    
    for _ in range(max_attempts):
        key = rotator.get_key()
        if key:
            return key
        rotator.rotate()
    
    return None


if __name__ == "__main__":
    # Test the rotator
    print("Testing Gemini API Key Rotator:")
    gemini_rotator = APIKeyRotator("AI_API_KEY")
    print(f"Total Gemini keys: {gemini_rotator.total_keys()}")
    for i in range(min(3, gemini_rotator.total_keys())):
        current_key = gemini_rotator.get_key()
        preview = f"{current_key[:20]}..." if current_key else "(no key)"
        print(f"  Key {i+1}: {preview}")
        gemini_rotator.rotate()
    
    print("\nTesting A4F API Key Rotator:")
    a4f_rotator = APIKeyRotator("A4F_API_KEY")
    print(f"Total A4F keys: {a4f_rotator.total_keys()}")
    for i in range(min(3, a4f_rotator.total_keys())):
        current_key = a4f_rotator.get_key()
        print(f"  Key {i+1}: {current_key or '(no key)'}")
        a4f_rotator.rotate()
